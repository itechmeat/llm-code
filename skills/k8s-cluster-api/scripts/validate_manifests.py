#!/usr/bin/env python3
"""Validate Cluster API YAML manifests against JSON schemas.

This script validates YAML manifests for Cluster API resources
(Cluster, Machine, ClusterClass, etc.) against their JSON schemas.

Usage:
    python validate_manifests.py <manifest.yaml>
    python validate_manifests.py manifests/*.yaml
    python validate_manifests.py --dir ./clusters/

Examples:
    python validate_manifests.py cluster.yaml
    python validate_manifests.py --dir ./manifests/ --recursive
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# Known Cluster API resource kinds and their API groups
CAPI_RESOURCES = {
    "Cluster": "cluster.x-k8s.io",
    "Machine": "cluster.x-k8s.io",
    "MachineSet": "cluster.x-k8s.io",
    "MachineDeployment": "cluster.x-k8s.io",
    "MachinePool": "cluster.x-k8s.io",
    "MachineHealthCheck": "cluster.x-k8s.io",
    "ClusterClass": "cluster.x-k8s.io",
    "ClusterResourceSet": "addons.cluster.x-k8s.io",
    "ClusterResourceSetBinding": "addons.cluster.x-k8s.io",
    "KubeadmConfig": "bootstrap.cluster.x-k8s.io",
    "KubeadmConfigTemplate": "bootstrap.cluster.x-k8s.io",
    "KubeadmControlPlane": "controlplane.cluster.x-k8s.io",
    "KubeadmControlPlaneTemplate": "controlplane.cluster.x-k8s.io",
    "IPAddress": "ipam.cluster.x-k8s.io",
    "IPAddressClaim": "ipam.cluster.x-k8s.io",
    "ExtensionConfig": "runtime.cluster.x-k8s.io",
}

# Required fields per resource kind
REQUIRED_FIELDS = {
    "Cluster": {
        "spec": ["infrastructureRef"],
    },
    "Machine": {
        "spec": ["clusterName", "bootstrap", "infrastructureRef"],
    },
    "MachineDeployment": {
        "spec": ["clusterName", "selector", "template"],
    },
    "MachineSet": {
        "spec": ["clusterName", "selector", "template"],
    },
    "MachineHealthCheck": {
        "spec": ["clusterName", "selector"],
    },
    "ClusterClass": {
        "spec": ["infrastructure", "controlPlane", "workers"],
    },
    "KubeadmConfig": {
        "spec": [],
    },
    "KubeadmControlPlane": {
        "spec": ["version"],
    },
}


class ValidationError:
    def __init__(self, path: str, message: str, severity: str = "error"):
        self.path = path
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        icon = "❌" if self.severity == "error" else "⚠️"
        return f"{icon} {self.path}: {self.message}"


def validate_api_version(doc: dict[str, Any]) -> list[ValidationError]:
    """Validate apiVersion field."""
    errors = []
    api_version = doc.get("apiVersion", "")

    if not api_version:
        errors.append(ValidationError("apiVersion", "Missing apiVersion field"))
        return errors

    kind = doc.get("kind", "")
    if kind in CAPI_RESOURCES:
        expected_group = CAPI_RESOURCES[kind]
        if not api_version.startswith(expected_group):
            errors.append(
                ValidationError(
                    "apiVersion",
                    f"Expected group '{expected_group}', got '{api_version}'",
                    "warning",
                )
            )

    # Check for deprecated v1alpha versions
    if "v1alpha" in api_version:
        errors.append(
            ValidationError(
                "apiVersion",
                f"v1alpha API versions are deprecated: {api_version}",
                "warning",
            )
        )

    return errors


def validate_metadata(doc: dict[str, Any]) -> list[ValidationError]:
    """Validate metadata field."""
    errors = []
    metadata = doc.get("metadata", {})

    if not metadata:
        errors.append(ValidationError("metadata", "Missing metadata field"))
        return errors

    if not metadata.get("name"):
        errors.append(ValidationError("metadata.name", "Missing name field"))

    # Check for required labels on certain resources
    kind = doc.get("kind", "")
    labels = metadata.get("labels", {})

    if kind in ("Machine", "MachineSet", "MachineDeployment", "MachinePool"):
        if "cluster.x-k8s.io/cluster-name" not in labels:
            spec_cluster = doc.get("spec", {}).get("clusterName", "")
            if not spec_cluster:
                errors.append(
                    ValidationError(
                        "metadata.labels",
                        "Missing cluster.x-k8s.io/cluster-name label",
                        "warning",
                    )
                )

    return errors


def validate_spec(doc: dict[str, Any]) -> list[ValidationError]:
    """Validate spec field based on resource kind."""
    errors = []
    kind = doc.get("kind", "")
    spec = doc.get("spec", {})

    if not spec:
        errors.append(ValidationError("spec", "Missing spec field"))
        return errors

    # Check required fields
    if kind in REQUIRED_FIELDS:
        required = REQUIRED_FIELDS[kind].get("spec", [])
        for field in required:
            if field not in spec:
                errors.append(
                    ValidationError(f"spec.{field}", f"Missing required field: {field}")
                )

    # Kind-specific validations
    if kind == "Cluster":
        errors.extend(_validate_cluster_spec(spec))
    elif kind == "Machine":
        errors.extend(_validate_machine_spec(spec))
    elif kind == "MachineDeployment":
        errors.extend(_validate_machine_deployment_spec(spec))
    elif kind == "ClusterClass":
        errors.extend(_validate_cluster_class_spec(spec))

    return errors


def _validate_cluster_spec(spec: dict[str, Any]) -> list[ValidationError]:
    """Validate Cluster spec."""
    errors = []

    infra_ref = spec.get("infrastructureRef", {})
    if infra_ref:
        if not infra_ref.get("kind"):
            errors.append(
                ValidationError(
                    "spec.infrastructureRef.kind", "Missing kind in infrastructureRef"
                )
            )
        if not infra_ref.get("name"):
            errors.append(
                ValidationError(
                    "spec.infrastructureRef.name", "Missing name in infrastructureRef"
                )
            )

    cp_ref = spec.get("controlPlaneRef", {})
    if cp_ref:
        if not cp_ref.get("kind"):
            errors.append(
                ValidationError(
                    "spec.controlPlaneRef.kind", "Missing kind in controlPlaneRef"
                )
            )

    return errors


def _validate_machine_spec(spec: dict[str, Any]) -> list[ValidationError]:
    """Validate Machine spec."""
    errors = []

    bootstrap = spec.get("bootstrap", {})
    if bootstrap:
        if not bootstrap.get("configRef") and not bootstrap.get("dataSecretName"):
            errors.append(
                ValidationError(
                    "spec.bootstrap",
                    "Must have either configRef or dataSecretName",
                )
            )

    return errors


def _validate_machine_deployment_spec(spec: dict[str, Any]) -> list[ValidationError]:
    """Validate MachineDeployment spec."""
    errors = []

    template = spec.get("template", {})
    if template:
        template_spec = template.get("spec", {})
        if not template_spec.get("bootstrap"):
            errors.append(
                ValidationError(
                    "spec.template.spec.bootstrap", "Missing bootstrap in template"
                )
            )
        if not template_spec.get("infrastructureRef"):
            errors.append(
                ValidationError(
                    "spec.template.spec.infrastructureRef",
                    "Missing infrastructureRef in template",
                )
            )

    return errors


def _validate_cluster_class_spec(spec: dict[str, Any]) -> list[ValidationError]:
    """Validate ClusterClass spec."""
    errors = []

    infra = spec.get("infrastructure", {})
    if infra and not infra.get("ref"):
        errors.append(
            ValidationError("spec.infrastructure.ref", "Missing ref in infrastructure")
        )

    cp = spec.get("controlPlane", {})
    if cp and not cp.get("ref"):
        errors.append(
            ValidationError("spec.controlPlane.ref", "Missing ref in controlPlane")
        )

    return errors


def validate_document(doc: dict[str, Any], file_path: str) -> list[ValidationError]:
    """Validate a single YAML document."""
    errors = []

    if not isinstance(doc, dict):
        return [ValidationError(file_path, "Document is not a valid YAML mapping")]

    kind = doc.get("kind", "")
    if not kind:
        errors.append(ValidationError("kind", "Missing kind field"))

    errors.extend(validate_api_version(doc))
    errors.extend(validate_metadata(doc))
    errors.extend(validate_spec(doc))

    return errors


def validate_file(file_path: Path) -> tuple[int, int, list[ValidationError]]:
    """Validate a YAML file, returns (doc_count, error_count, errors)."""
    all_errors = []
    doc_count = 0

    try:
        content = file_path.read_text(encoding="utf-8")
        documents = list(yaml.safe_load_all(content))

        for doc in documents:
            if doc is None:
                continue
            doc_count += 1
            errors = validate_document(doc, str(file_path))
            all_errors.extend(errors)

    except yaml.YAMLError as e:
        all_errors.append(ValidationError(str(file_path), f"YAML parse error: {e}"))
    except OSError as e:
        all_errors.append(ValidationError(str(file_path), f"File read error: {e}"))

    error_count = sum(1 for e in all_errors if e.severity == "error")
    return doc_count, error_count, all_errors


def find_yaml_files(paths: list[Path], recursive: bool = False) -> list[Path]:
    """Find all YAML files from given paths."""
    files = []

    for path in paths:
        if path.is_file():
            if path.suffix in (".yaml", ".yml"):
                files.append(path)
        elif path.is_dir():
            pattern = "**/*.yaml" if recursive else "*.yaml"
            files.extend(path.glob(pattern))
            pattern = "**/*.yml" if recursive else "*.yml"
            files.extend(path.glob(pattern))

    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Cluster API YAML manifests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path(".")],
        help="Files or directories to validate",
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=Path,
        help="Directory containing manifests",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Search directories recursively",
    )
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()

    paths = args.paths
    if args.dir:
        paths = [args.dir]

    files = find_yaml_files(paths, args.recursive)

    if not files:
        print("No YAML files found", file=sys.stderr)
        return 1

    total_docs = 0
    total_errors = 0
    total_warnings = 0

    for file_path in files:
        doc_count, error_count, errors = validate_file(file_path)
        total_docs += doc_count
        total_errors += error_count
        total_warnings += sum(1 for e in errors if e.severity == "warning")

        if errors:
            print(f"\n{file_path}:")
            for error in errors:
                print(f"  {error}")

    # Summary
    print(f"\n{'='*50}")
    print(f"Files scanned: {len(files)}")
    print(f"Documents validated: {total_docs}")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {total_warnings}")

    if total_errors > 0:
        return 1
    if args.strict and total_warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
