#!/usr/bin/env python3
"""Export cluster state for backup or migration.

Exports all CAPI resources for a cluster to YAML files, suitable for
backup, disaster recovery, or clusterctl move operations.

Usage:
    python export_cluster_state.py <cluster-name> [options]

Examples:
    python export_cluster_state.py my-cluster -o ./backup/
    python export_cluster_state.py my-cluster --namespace clusters --include-secrets
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def find_kubectl() -> str | None:
    """Find kubectl binary."""
    return shutil.which("kubectl")


def run_kubectl(
    args: list[str],
    timeout: int = 60,
) -> tuple[bool, str, str]:
    """Run kubectl command and return (success, stdout, stderr)."""
    kubectl = find_kubectl()
    if not kubectl:
        return False, "", "kubectl not found"

    cmd = [kubectl] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"


def get_cluster(name: str, namespace: str) -> dict[str, Any] | None:
    """Get Cluster resource."""
    success, stdout, _ = run_kubectl(
        ["get", f"clusters.cluster.x-k8s.io/{name}", "-n", namespace, "-o", "json"]
    )
    if not success:
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return None


def get_resources_for_cluster(
    resource_type: str,
    cluster_name: str,
    namespace: str,
) -> list[dict[str, Any]]:
    """Get all resources of a type for a cluster."""
    success, stdout, _ = run_kubectl(
        [
            "get",
            resource_type,
            "-n",
            namespace,
            "-l",
            f"cluster.x-k8s.io/cluster-name={cluster_name}",
            "-o",
            "json",
        ]
    )
    if not success:
        return []

    try:
        data = json.loads(stdout)
        return data.get("items", [])
    except json.JSONDecodeError:
        return []


def clean_resource(resource: dict[str, Any], preserve_status: bool = False) -> dict[str, Any]:
    """Clean resource for export (remove runtime fields)."""
    # Deep copy
    import copy

    cleaned = copy.deepcopy(resource)

    # Remove metadata fields
    metadata = cleaned.get("metadata", {})
    fields_to_remove = [
        "uid",
        "resourceVersion",
        "generation",
        "creationTimestamp",
        "managedFields",
        "selfLink",
    ]
    for field in fields_to_remove:
        metadata.pop(field, None)

    # Clean annotations
    annotations = metadata.get("annotations", {})
    anno_prefixes_to_remove = [
        "kubectl.kubernetes.io/",
        "deployment.kubernetes.io/",
    ]
    annotations = {
        k: v
        for k, v in annotations.items()
        if not any(k.startswith(prefix) for prefix in anno_prefixes_to_remove)
    }
    if annotations:
        metadata["annotations"] = annotations
    else:
        metadata.pop("annotations", None)

    # Clean finalizers for export (optional - may want to keep)
    # metadata.pop("finalizers", None)

    # Remove ownerReferences
    metadata.pop("ownerReferences", None)

    cleaned["metadata"] = metadata

    # Remove status unless requested
    if not preserve_status:
        cleaned.pop("status", None)

    return cleaned


def to_yaml(resource: dict[str, Any]) -> str:
    """Convert resource to YAML."""
    try:
        import yaml

        return yaml.dump(resource, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except ImportError:
        # Fallback to JSON if PyYAML not available
        return json.dumps(resource, indent=2)


def export_cluster(
    cluster_name: str,
    namespace: str,
    output_dir: Path,
    include_secrets: bool = False,
    include_status: bool = False,
) -> dict[str, int]:
    """Export all cluster resources."""
    stats = {"exported": 0, "errors": 0}

    # Resource types to export
    resource_types = [
        # Core CAPI
        "clusters.cluster.x-k8s.io",
        "machines.cluster.x-k8s.io",
        "machinesets.cluster.x-k8s.io",
        "machinedeployments.cluster.x-k8s.io",
        "machinepools.cluster.x-k8s.io",
        "machinehealthchecks.cluster.x-k8s.io",
        "clusterresourcesets.addons.cluster.x-k8s.io",
        "clusterresourcesetbindings.addons.cluster.x-k8s.io",
        # Bootstrap
        "kubeadmconfigs.bootstrap.cluster.x-k8s.io",
        "kubeadmconfigtemplates.bootstrap.cluster.x-k8s.io",
        # Control Plane
        "kubeadmcontrolplanes.controlplane.cluster.x-k8s.io",
        "kubeadmcontrolplanetemplates.controlplane.cluster.x-k8s.io",
        # IPAM (if exists)
        "ipaddressclaims.ipam.cluster.x-k8s.io",
        "ipaddresses.ipam.cluster.x-k8s.io",
    ]

    # Provider-specific types (discover dynamically)
    provider_types = discover_provider_types()
    resource_types.extend(provider_types)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export the main cluster first
    cluster = get_cluster(cluster_name, namespace)
    if not cluster:
        print(f"Error: Cluster '{cluster_name}' not found in namespace '{namespace}'")
        return {"exported": 0, "errors": 1}

    # Write cluster
    cluster_file = output_dir / "cluster.yaml"
    cleaned = clean_resource(cluster, include_status)
    cluster_file.write_text(to_yaml(cleaned))
    stats["exported"] += 1
    print(f"  Exported: Cluster/{cluster_name}")

    # Export referenced infrastructure cluster (from cluster.spec.infrastructureRef)
    infra_ref = cluster.get("spec", {}).get("infrastructureRef", {})
    if infra_ref:
        export_referenced_resource(
            infra_ref,
            namespace,
            output_dir / "infrastructure-cluster.yaml",
            include_status,
            stats,
        )

    # Export referenced control plane
    cp_ref = cluster.get("spec", {}).get("controlPlaneRef", {})
    if cp_ref:
        export_referenced_resource(
            cp_ref,
            namespace,
            output_dir / "control-plane.yaml",
            include_status,
            stats,
        )

    # Export by resource type
    for resource_type in resource_types:
        resources = get_resources_for_cluster(resource_type, cluster_name, namespace)
        if not resources:
            continue

        # Create subdirectory for resource type
        type_name = resource_type.split(".")[0]
        type_dir = output_dir / type_name
        type_dir.mkdir(exist_ok=True)

        for resource in resources:
            name = resource.get("metadata", {}).get("name", "unknown")
            cleaned = clean_resource(resource, include_status)

            filename = f"{name}.yaml"
            (type_dir / filename).write_text(to_yaml(cleaned))
            stats["exported"] += 1
            print(f"  Exported: {resource.get('kind', type_name)}/{name}")

    # Export secrets if requested
    if include_secrets:
        export_secrets(cluster_name, namespace, output_dir, stats)

    # Write manifest (list of exported resources)
    write_manifest(output_dir, cluster_name, namespace, stats)

    return stats


def export_referenced_resource(
    ref: dict[str, Any],
    namespace: str,
    output_file: Path,
    include_status: bool,
    stats: dict[str, int],
) -> None:
    """Export a referenced resource."""
    kind = ref.get("kind", "")
    name = ref.get("name", "")
    api_version = ref.get("apiVersion", "")

    if not kind or not name or not api_version:
        return

    # Convert apiVersion to resource type
    group = api_version.split("/")[0] if "/" in api_version else ""
    resource_type = f"{kind.lower()}s.{group}" if group else kind.lower()

    success, stdout, _ = run_kubectl(
        ["get", f"{resource_type}/{name}", "-n", namespace, "-o", "json"]
    )
    if not success:
        return

    try:
        resource = json.loads(stdout)
        cleaned = clean_resource(resource, include_status)
        output_file.write_text(to_yaml(cleaned))
        stats["exported"] += 1
        print(f"  Exported: {kind}/{name}")
    except json.JSONDecodeError:
        stats["errors"] += 1


def discover_provider_types() -> list[str]:
    """Discover provider-specific CRD types."""
    provider_types = []

    # Common infrastructure providers
    infra_providers = [
        "awsclusters",
        "awsmachines",
        "awsmachinetemplates",
        "azureclusters",
        "azuremachines",
        "azuremachinetemplates",
        "gcpclusters",
        "gcpmachines",
        "gcpmachinetemplates",
        "vsphereclusters",
        "vspheremachines",
        "vspheremachinetemplates",
        "dockerclusters",
        "dockermachines",
        "dockermachinetemplates",
        "metal3clusters",
        "metal3machines",
        "metal3machinetemplates",
    ]

    for resource in infra_providers:
        # Check if CRD exists
        success, _, _ = run_kubectl(
            ["api-resources", "--api-group=infrastructure.cluster.x-k8s.io", "-o", "name"],
            timeout=10,
        )
        if success:
            break

    # Return infrastructure types that might exist
    return [
        f"{r}.infrastructure.cluster.x-k8s.io"
        for r in ["awsclusters", "awsmachines", "azureclusters", "azuremachines", "vsphereclusters", "vspheremachines"]
    ]


def export_secrets(
    cluster_name: str,
    namespace: str,
    output_dir: Path,
    stats: dict[str, int],
) -> None:
    """Export cluster-related secrets."""
    secrets_dir = output_dir / "secrets"
    secrets_dir.mkdir(exist_ok=True)

    # Get secrets with cluster label
    success, stdout, _ = run_kubectl(
        [
            "get",
            "secrets",
            "-n",
            namespace,
            "-l",
            f"cluster.x-k8s.io/cluster-name={cluster_name}",
            "-o",
            "json",
        ]
    )
    if not success:
        return

    try:
        data = json.loads(stdout)
        for secret in data.get("items", []):
            name = secret.get("metadata", {}).get("name", "unknown")
            cleaned = clean_resource(secret, False)

            # Remove data but keep structure
            if "data" in cleaned:
                cleaned["data"] = {k: "***REDACTED***" for k in cleaned["data"]}

            filename = f"{name}.yaml"
            (secrets_dir / filename).write_text(to_yaml(cleaned))
            stats["exported"] += 1
            print(f"  Exported: Secret/{name} (data redacted)")
    except json.JSONDecodeError:
        stats["errors"] += 1


def write_manifest(
    output_dir: Path,
    cluster_name: str,
    namespace: str,
    stats: dict[str, int],
) -> None:
    """Write export manifest file."""
    manifest = {
        "exportDate": datetime.utcnow().isoformat() + "Z",
        "clusterName": cluster_name,
        "namespace": namespace,
        "stats": stats,
        "files": [],
    }

    # List all exported files
    for path in sorted(output_dir.rglob("*.yaml")):
        if path.name != "manifest.yaml":
            manifest["files"].append(str(path.relative_to(output_dir)))

    manifest_file = output_dir / "manifest.yaml"
    manifest_file.write_text(to_yaml(manifest))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export cluster state for backup/migration",
    )
    parser.add_argument(
        "cluster",
        help="Cluster name to export",
    )
    parser.add_argument(
        "--namespace",
        "-n",
        default="default",
        help="Cluster namespace (default: default)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output directory (default: ./<cluster-name>-export)",
    )
    parser.add_argument(
        "--include-secrets",
        action="store_true",
        help="Include secrets (data will be redacted)",
    )
    parser.add_argument(
        "--include-status",
        action="store_true",
        help="Include status fields in export",
    )
    args = parser.parse_args()

    if not find_kubectl():
        print("Error: kubectl not found in PATH", file=sys.stderr)
        return 1

    output_dir = Path(args.output or f"./{args.cluster}-export")

    if output_dir.exists():
        print(f"Warning: Output directory exists: {output_dir}")
        response = input("Overwrite? [y/N]: ")
        if response.lower() != "y":
            return 1

    print(f"\nExporting cluster '{args.cluster}' from namespace '{args.namespace}'")
    print(f"Output directory: {output_dir}")
    print("-" * 50)

    stats = export_cluster(
        cluster_name=args.cluster,
        namespace=args.namespace,
        output_dir=output_dir,
        include_secrets=args.include_secrets,
        include_status=args.include_status,
    )

    print("-" * 50)
    print(f"\n✓ Export complete!")
    print(f"  Resources exported: {stats['exported']}")
    print(f"  Errors: {stats['errors']}")
    print(f"\nTo restore, apply the manifests in order:")
    print(f"  kubectl apply -f {output_dir}/ --recursive")
    print(f"\nFor clusterctl move, use:")
    print(f"  clusterctl move --to-kubeconfig <target> --namespace {args.namespace}")

    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
