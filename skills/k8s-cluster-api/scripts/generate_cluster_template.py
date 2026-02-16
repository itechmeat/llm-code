#!/usr/bin/env python3
"""Generate cluster templates from ClusterClass definitions.

Generates Cluster API manifest YAML from a ClusterClass with variable
substitution and topology configuration.

Usage:
    python generate_cluster_template.py <clusterclass> [options]
    python generate_cluster_template.py --from-asset minimal

Examples:
    python generate_cluster_template.py myclass --name prod-cluster --namespace clusters
    python generate_cluster_template.py myclass --workers 3 --controlplane 3
    python generate_cluster_template.py --from-asset production --name my-cluster
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


# Available asset templates
ASSET_TEMPLATES = {
    "minimal": "cluster-minimal.yaml",
    "production": "cluster-production.yaml",
    "clusterclass": "cluster-clusterclass.yaml",
    "clusterclass-def": "clusterclass-example.yaml",
}


def get_assets_dir() -> Path:
    """Get path to assets directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "assets"


def list_asset_templates() -> dict[str, str]:
    """List available asset templates with descriptions."""
    return {
        "minimal": "Quick dev/test Docker cluster",
        "production": "Production HA cluster (3 CP, MHC, audit logging)",
        "clusterclass": "Topology-based cluster using ClusterClass",
        "clusterclass-def": "Full ClusterClass definition example",
    }


def load_asset_template(
    name: str, replacements: dict[str, str] | None = None
) -> str | None:
    """Load and optionally customize an asset template."""
    if name not in ASSET_TEMPLATES:
        return None

    assets_dir = get_assets_dir()
    template_file = assets_dir / ASSET_TEMPLATES[name]

    if not template_file.exists():
        return None

    content = template_file.read_text()

    # Apply replacements if provided
    if replacements:
        for placeholder, value in replacements.items():
            # Replace YAML values: name: old-value -> name: new-value
            pattern = rf"(name:\s*){re.escape(placeholder)}"
            content = re.sub(pattern, rf"\1{value}", content)
            # Also replace direct placeholders
            content = content.replace(placeholder, value)

    return content


def find_kubectl() -> str | None:
    """Find kubectl binary."""
    return shutil.which("kubectl")


def get_clusterclass(name: str, namespace: str | None = None) -> dict[str, Any] | None:
    """Fetch ClusterClass from cluster."""
    kubectl = find_kubectl()
    if not kubectl:
        return None

    cmd = [kubectl, "get", f"clusterclasses.cluster.x-k8s.io/{name}", "-o", "json"]
    if namespace:
        cmd.extend(["-n", namespace])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def extract_variables(clusterclass: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract variable definitions from ClusterClass."""
    spec = clusterclass.get("spec", {})
    variables = []

    # Get variable definitions
    for var_def in spec.get("variables", []):
        var_info = {
            "name": var_def.get("name", ""),
            "required": var_def.get("required", False),
            "metadata": var_def.get("metadata", {}),
            "schema": var_def.get("schema", {}),
        }

        # Extract default from schema if present
        openapi = var_info["schema"].get("openAPIV3Schema", {})
        if "default" in openapi:
            var_info["default"] = openapi["default"]

        variables.append(var_info)

    return variables


def get_worker_classes(clusterclass: dict[str, Any]) -> list[str]:
    """Get available worker MachineDeployment classes."""
    spec = clusterclass.get("spec", {})
    workers = spec.get("workers", {})
    classes = []

    for md_class in workers.get("machineDeployments", []):
        class_name = md_class.get("class", "")
        if class_name:
            classes.append(class_name)

    for mp_class in workers.get("machinePools", []):
        class_name = mp_class.get("class", "")
        if class_name:
            classes.append(class_name)

    return classes


def generate_yaml(
    clusterclass_name: str,
    cluster_name: str,
    namespace: str,
    kubernetes_version: str,
    control_plane_replicas: int,
    worker_replicas: int,
    worker_class: str | None,
    variables: dict[str, Any],
    clusterclass: dict[str, Any],
) -> str:
    """Generate Cluster YAML from ClusterClass."""
    var_defs = extract_variables(clusterclass)
    worker_classes = get_worker_classes(clusterclass)

    # Build variables section
    topology_variables = []

    # Add user-provided variables
    for var_name, var_value in variables.items():
        topology_variables.append({"name": var_name, "value": var_value})

    # Add default values for unspecified required variables
    for var_def in var_defs:
        var_name = var_def["name"]
        if var_name not in variables:
            if "default" in var_def:
                topology_variables.append({"name": var_name, "value": var_def["default"]})
            elif var_def["required"]:
                # Placeholder for required variable
                topology_variables.append({"name": var_name, "value": f"<{var_name}>"})

    # Determine worker class
    if not worker_class and worker_classes:
        worker_class = worker_classes[0]

    # Build YAML manually for precise control
    lines = [
        "apiVersion: cluster.x-k8s.io/v1beta1",
        "kind: Cluster",
        "metadata:",
        f"  name: {cluster_name}",
        f"  namespace: {namespace}",
        "spec:",
        "  topology:",
        f"    class: {clusterclass_name}",
        f"    version: {kubernetes_version}",
        "    controlPlane:",
        f"      replicas: {control_plane_replicas}",
    ]

    # Add workers if worker class available
    if worker_class:
        lines.extend(
            [
                "    workers:",
                "      machineDeployments:",
                f"      - class: {worker_class}",
                f"        name: {worker_class}-0",
                f"        replicas: {worker_replicas}",
            ]
        )

    # Add variables
    if topology_variables:
        lines.append("    variables:")
        for var in topology_variables:
            # Simple scalar values
            value = var["value"]
            if isinstance(value, bool):
                value_str = "true" if value else "false"
            elif isinstance(value, (int, float)):
                value_str = str(value)
            elif isinstance(value, str):
                # Quote if contains special chars
                if ":" in value or value.startswith("{") or value.startswith("["):
                    value_str = f'"{value}"'
                else:
                    value_str = value
            else:
                # Complex values as inline JSON
                value_str = json.dumps(value)

            lines.append(f"    - name: {var['name']}")
            lines.append(f"      value: {value_str}")

    return "\n".join(lines) + "\n"


def generate_from_scratch(
    clusterclass_name: str,
    cluster_name: str,
    namespace: str,
    kubernetes_version: str,
    control_plane_replicas: int,
    worker_replicas: int,
    worker_class: str,
) -> str:
    """Generate minimal template when ClusterClass not available."""
    return f"""apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: {cluster_name}
  namespace: {namespace}
spec:
  topology:
    class: {clusterclass_name}
    version: {kubernetes_version}
    controlPlane:
      replicas: {control_plane_replicas}
    workers:
      machineDeployments:
      - class: {worker_class}
        name: {worker_class}-0
        replicas: {worker_replicas}
    variables: []
    # TODO: Add required variables from ClusterClass definition
    # Use: kubectl describe clusterclass {clusterclass_name} to see available variables
"""


def list_clusterclasses(namespace: str | None = None) -> list[str]:
    """List available ClusterClasses."""
    kubectl = find_kubectl()
    if not kubectl:
        return []

    cmd = [kubectl, "get", "clusterclasses.cluster.x-k8s.io", "-o", "json"]
    if namespace:
        cmd.extend(["-n", namespace])
    else:
        cmd.append("--all-namespaces")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        items = data.get("items", [])
        return [
            f"{item['metadata'].get('namespace', 'default')}/{item['metadata']['name']}"
            for item in items
        ]
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return []


def print_clusterclass_info(clusterclass: dict[str, Any]) -> None:
    """Print ClusterClass information."""
    metadata = clusterclass.get("metadata", {})
    spec = clusterclass.get("spec", {})

    name = metadata.get("name", "unknown")
    namespace = metadata.get("namespace", "default")

    print(f"\nClusterClass: {namespace}/{name}")
    print("=" * 50)

    # Infrastructure
    infra_ref = spec.get("infrastructure", {}).get("ref", {})
    if infra_ref:
        print(f"\nInfrastructure: {infra_ref.get('kind')}")

    # Control plane
    cp = spec.get("controlPlane", {})
    cp_ref = cp.get("ref", {})
    if cp_ref:
        print(f"Control Plane: {cp_ref.get('kind')}")

    # Workers
    workers = spec.get("workers", {})
    md_classes = workers.get("machineDeployments", [])
    if md_classes:
        print("\nWorker Classes (MachineDeployment):")
        for md in md_classes:
            print(f"  - {md.get('class')}")

    mp_classes = workers.get("machinePools", [])
    if mp_classes:
        print("\nWorker Classes (MachinePool):")
        for mp in mp_classes:
            print(f"  - {mp.get('class')}")

    # Variables
    variables = extract_variables(clusterclass)
    if variables:
        print("\nVariables:")
        for var in variables:
            required = "required" if var["required"] else "optional"
            default_str = f", default: {var.get('default')}" if "default" in var else ""
            print(f"  - {var['name']} ({required}{default_str})")

            # Description
            desc = var.get("metadata", {}).get("description", "")
            if desc:
                print(f"    {desc[:80]}...")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate cluster templates from ClusterClass",
    )
    parser.add_argument(
        "clusterclass",
        nargs="?",
        help="ClusterClass name (omit to list available)",
    )
    parser.add_argument(
        "--name",
        "-n",
        default="my-cluster",
        help="Cluster name (default: my-cluster)",
    )
    parser.add_argument(
        "--namespace",
        default="default",
        help="Target namespace (default: default)",
    )
    parser.add_argument(
        "--version",
        "-v",
        default="v1.28.0",
        help="Kubernetes version (default: v1.28.0)",
    )
    parser.add_argument(
        "--controlplane",
        "-c",
        type=int,
        default=1,
        help="Control plane replicas (default: 1)",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=1,
        help="Worker replicas (default: 1)",
    )
    parser.add_argument(
        "--worker-class",
        default=None,
        help="Worker MachineDeployment class name",
    )
    parser.add_argument(
        "--var",
        action="append",
        default=[],
        help="Set variable (format: name=value), can repeat",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show ClusterClass info instead of generating",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write to file instead of stdout",
    )
    parser.add_argument(
        "--from-asset",
        choices=list(ASSET_TEMPLATES.keys()),
        help="Generate from predefined asset template instead of ClusterClass",
    )
    parser.add_argument(
        "--list-assets",
        action="store_true",
        help="List available asset templates",
    )
    args = parser.parse_args()

    # List assets mode
    if args.list_assets:
        print("Available asset templates:")
        for name, desc in list_asset_templates().items():
            print(f"  {name:16} - {desc}")
        return 0

    # From-asset mode
    if args.from_asset:
        replacements = {}
        if args.name != "my-cluster":
            # Apply name replacements based on template type
            if args.from_asset == "minimal":
                replacements["capi-quickstart"] = args.name
            elif args.from_asset == "production":
                replacements["prod-cluster"] = args.name
            elif args.from_asset == "clusterclass":
                replacements["my-cluster"] = args.name

        yaml_output = load_asset_template(args.from_asset, replacements)
        if not yaml_output:
            print(f"Error: Asset template '{args.from_asset}' not found", file=sys.stderr)
            return 1

        if args.output:
            with open(args.output, "w") as f:
                f.write(yaml_output)
            print(f"Template written to: {args.output}", file=sys.stderr)
        else:
            print(yaml_output)
        return 0

    if not find_kubectl():
        print("Error: kubectl not found in PATH", file=sys.stderr)
        return 1

    # List mode
    if not args.clusterclass:
        print("Available ClusterClasses:")
        classes = list_clusterclasses()
        if not classes:
            print("  No ClusterClasses found")
        else:
            for cc in classes:
                print(f"  - {cc}")
        return 0

    # Fetch ClusterClass
    clusterclass = get_clusterclass(args.clusterclass, args.namespace)

    # Info mode
    if args.info:
        if not clusterclass:
            print(f"Error: ClusterClass '{args.clusterclass}' not found", file=sys.stderr)
            return 1
        print_clusterclass_info(clusterclass)
        return 0

    # Parse variables
    variables = {}
    for var_str in args.var:
        if "=" not in var_str:
            print(f"Error: Invalid variable format: {var_str}", file=sys.stderr)
            print("  Use: --var name=value", file=sys.stderr)
            return 1
        name, value = var_str.split("=", 1)

        # Try to parse as JSON for complex values
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            # Keep as string if not valid JSON
            pass

        variables[name] = value

    # Generate template
    if clusterclass:
        yaml_output = generate_yaml(
            clusterclass_name=args.clusterclass,
            cluster_name=args.name,
            namespace=args.namespace,
            kubernetes_version=args.version,
            control_plane_replicas=args.controlplane,
            worker_replicas=args.workers,
            worker_class=args.worker_class,
            variables=variables,
            clusterclass=clusterclass,
        )
    else:
        print(
            f"Warning: ClusterClass '{args.clusterclass}' not found, generating minimal template",
            file=sys.stderr,
        )
        yaml_output = generate_from_scratch(
            clusterclass_name=args.clusterclass,
            cluster_name=args.name,
            namespace=args.namespace,
            kubernetes_version=args.version,
            control_plane_replicas=args.controlplane,
            worker_replicas=args.workers,
            worker_class=args.worker_class or "default-worker",
        )

    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(yaml_output)
        print(f"Template written to: {args.output}", file=sys.stderr)
    else:
        print(yaml_output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
