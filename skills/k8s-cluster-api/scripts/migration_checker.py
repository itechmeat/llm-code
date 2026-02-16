#!/usr/bin/env python3
"""Check v1beta1 to v1beta2 migration readiness.

This script analyzes Cluster API manifests and deployed resources
to identify deprecated fields and migration requirements.

Usage:
    python migration_checker.py [--file <manifest.yaml>]
    python migration_checker.py [--live] [-n <namespace>]

Examples:
    python migration_checker.py --file cluster.yaml
    python migration_checker.py --live -n clusters
    python migration_checker.py --dir ./manifests/
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# Deprecated fields in v1beta1 that are removed/changed in v1beta2
DEPRECATED_FIELDS = {
    "Cluster": {
        "spec.topology.rolloutAfter": {
            "reason": "Never implemented, removed in v1beta2",
            "action": "Remove this field",
        },
        "spec.topology.class": {
            "reason": "Renamed to spec.topology.classRef.name",
            "action": "Move to spec.topology.classRef.name",
        },
        "spec.topology.classNamespace": {
            "reason": "Renamed to spec.topology.classRef.namespace",
            "action": "Move to spec.topology.classRef.namespace",
        },
        "status.failureReason": {
            "reason": "Moved to status.deprecated.v1beta1.failureReason",
            "action": "Update status handling code",
        },
        "status.failureMessage": {
            "reason": "Moved to status.deprecated.v1beta1.failureMessage",
            "action": "Update status handling code",
        },
    },
    "Machine": {
        "spec.nodeDeletionTimeout": {
            "reason": "Renamed to spec.deletion.nodeDeletionTimeoutSeconds",
            "action": "Move to spec.deletion.nodeDeletionTimeoutSeconds (as int32)",
        },
        "spec.nodeDrainTimeout": {
            "reason": "Renamed to spec.deletion.nodeDrainTimeoutSeconds",
            "action": "Move to spec.deletion.nodeDrainTimeoutSeconds (as int32)",
        },
        "spec.nodeVolumeDetachTimeout": {
            "reason": "Renamed to spec.deletion.nodeVolumeDetachTimeoutSeconds",
            "action": "Move to spec.deletion.nodeVolumeDetachTimeoutSeconds (as int32)",
        },
    },
    "MachineDeployment": {
        "spec.progressDeadlineSeconds": {
            "reason": "Deprecated since v1.9, removed in v1beta2",
            "action": "Remove this field",
        },
        "spec.revisionHistoryLimit": {
            "reason": "Removed, controller now cleans up all MachineSets without replicas",
            "action": "Remove this field",
        },
        "spec.strategy.rollingUpdate.deletePolicy": {
            "reason": "Renamed to spec.deletion.order",
            "action": "Move to spec.deletion.order",
        },
        "spec.machineNamingStrategy": {
            "reason": "Renamed to spec.machineNaming",
            "action": "Rename to spec.machineNaming",
        },
    },
    "MachineSet": {
        "spec.deletePolicy": {
            "reason": "Renamed to spec.deletion.order",
            "action": "Move to spec.deletion.order",
        },
        "spec.machineNamingStrategy": {
            "reason": "Renamed to spec.machineNaming",
            "action": "Rename to spec.machineNaming",
        },
    },
    "KubeadmControlPlane": {
        "spec.kubeadmConfigSpec.clusterConfiguration.clusterName": {
            "reason": "Inferred from top level, removed to avoid confusion",
            "action": "Remove this field",
        },
    },
}

# Object reference changes: apiVersion → apiGroup
OBJECT_REF_FIELDS = [
    "spec.infrastructureRef",
    "spec.controlPlaneRef",
    "spec.bootstrap.configRef",
    "spec.template.spec.infrastructureRef",
    "spec.template.spec.bootstrap.configRef",
]


class MigrationIssue:
    def __init__(
        self,
        path: str,
        field: str,
        reason: str,
        action: str,
        severity: str = "warning",
    ):
        self.path = path
        self.field = field
        self.reason = reason
        self.action = action
        self.severity = severity

    def __str__(self) -> str:
        icon = "⚠️" if self.severity == "warning" else "ℹ️"
        return f"{icon} {self.field}\n   Reason: {self.reason}\n   Action: {self.action}"


def get_nested(data: dict, path: str) -> Any:
    """Get nested value from dict using dot notation."""
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return None
    return current


def check_deprecated_fields(doc: dict[str, Any], file_path: str) -> list[MigrationIssue]:
    """Check for deprecated fields in document."""
    issues = []
    kind = doc.get("kind", "")

    if kind not in DEPRECATED_FIELDS:
        return issues

    for field, info in DEPRECATED_FIELDS[kind].items():
        value = get_nested(doc, field)
        if value is not None:
            issues.append(
                MigrationIssue(
                    path=file_path,
                    field=field,
                    reason=info["reason"],
                    action=info["action"],
                )
            )

    return issues


def check_object_references(doc: dict[str, Any], file_path: str) -> list[MigrationIssue]:
    """Check for object references that need migration from apiVersion to apiGroup."""
    issues = []

    for ref_path in OBJECT_REF_FIELDS:
        ref = get_nested(doc, ref_path)
        if ref and isinstance(ref, dict):
            if "apiVersion" in ref and "apiGroup" not in ref:
                issues.append(
                    MigrationIssue(
                        path=file_path,
                        field=f"{ref_path}.apiVersion",
                        reason="v1beta2 uses apiGroup instead of apiVersion in object references",
                        action=f"Replace apiVersion with apiGroup (e.g., 'infrastructure.cluster.x-k8s.io')",
                        severity="info",
                    )
                )
            # Check for namespace field that will be removed
            if "namespace" in ref:
                issues.append(
                    MigrationIssue(
                        path=file_path,
                        field=f"{ref_path}.namespace",
                        reason="namespace field removed from object references in v1beta2",
                        action="Remove namespace field from object reference",
                    )
                )

    return issues


def check_duration_fields(doc: dict[str, Any], file_path: str) -> list[MigrationIssue]:
    """Check for duration fields that need conversion to int32 seconds."""
    issues = []

    duration_fields = [
        ("spec.nodeDeletionTimeout", "spec.deletion.nodeDeletionTimeoutSeconds"),
        ("spec.nodeDrainTimeout", "spec.deletion.nodeDrainTimeoutSeconds"),
        ("spec.nodeVolumeDetachTimeout", "spec.deletion.nodeVolumeDetachTimeoutSeconds"),
        (
            "spec.template.spec.nodeDeletionTimeout",
            "spec.template.spec.deletion.nodeDeletionTimeoutSeconds",
        ),
        (
            "spec.topology.controlPlane.nodeDeletionTimeout",
            "spec.topology.controlPlane.deletion.nodeDeletionTimeoutSeconds",
        ),
    ]

    for old_path, new_path in duration_fields:
        value = get_nested(doc, old_path)
        if value is not None:
            # Check if it's a duration string (e.g., "10s", "5m")
            if isinstance(value, str) and any(c.isalpha() for c in value):
                issues.append(
                    MigrationIssue(
                        path=file_path,
                        field=old_path,
                        reason="Duration fields changed from string to int32 seconds",
                        action=f"Convert to integer seconds and rename to {new_path}",
                    )
                )

    return issues


def check_api_version(doc: dict[str, Any], file_path: str) -> list[MigrationIssue]:
    """Check API version for migration status."""
    issues = []
    api_version = doc.get("apiVersion", "")

    if "v1beta1" in api_version:
        issues.append(
            MigrationIssue(
                path=file_path,
                field="apiVersion",
                reason="v1beta1 is deprecated, will be removed in August 2026",
                action="Migrate to v1beta2 API version",
                severity="warning",
            )
        )
    elif "v1alpha" in api_version:
        issues.append(
            MigrationIssue(
                path=file_path,
                field="apiVersion",
                reason="v1alpha versions are deprecated",
                action="Migrate to v1beta2 API version",
                severity="warning",
            )
        )

    return issues


def analyze_document(doc: dict[str, Any], file_path: str) -> list[MigrationIssue]:
    """Analyze single document for migration issues."""
    issues = []

    issues.extend(check_api_version(doc, file_path))
    issues.extend(check_deprecated_fields(doc, file_path))
    issues.extend(check_object_references(doc, file_path))
    issues.extend(check_duration_fields(doc, file_path))

    return issues


def analyze_file(file_path: Path) -> list[MigrationIssue]:
    """Analyze YAML file for migration issues."""
    all_issues = []

    try:
        content = file_path.read_text(encoding="utf-8")
        documents = list(yaml.safe_load_all(content))

        for doc in documents:
            if doc is None:
                continue
            issues = analyze_document(doc, str(file_path))
            all_issues.extend(issues)

    except yaml.YAMLError as e:
        print(f"YAML parse error in {file_path}: {e}", file=sys.stderr)
    except OSError as e:
        print(f"File read error {file_path}: {e}", file=sys.stderr)

    return all_issues


def analyze_live_resources(namespace: str | None) -> list[MigrationIssue]:
    """Analyze live cluster resources for migration issues."""
    kubectl = shutil.which("kubectl")
    if not kubectl:
        print("kubectl not found, skipping live analysis", file=sys.stderr)
        return []

    all_issues = []
    resource_types = [
        "clusters.cluster.x-k8s.io",
        "machines.cluster.x-k8s.io",
        "machinesets.cluster.x-k8s.io",
        "machinedeployments.cluster.x-k8s.io",
        "machinepools.cluster.x-k8s.io",
        "kubeadmconfigs.bootstrap.cluster.x-k8s.io",
        "kubeadmcontrolplanes.controlplane.cluster.x-k8s.io",
    ]

    for resource_type in resource_types:
        cmd = [kubectl, "get", resource_type, "-o", "json"]
        if namespace:
            cmd.extend(["-n", namespace])
        else:
            cmd.append("--all-namespaces")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                continue

            data = json.loads(result.stdout)
            items = data.get("items", [])

            for item in items:
                name = item.get("metadata", {}).get("name", "unknown")
                ns = item.get("metadata", {}).get("namespace", "default")
                path = f"{resource_type}/{ns}/{name}"
                issues = analyze_document(item, path)
                all_issues.extend(issues)

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            print(f"Error analyzing {resource_type}: {e}", file=sys.stderr)

    return all_issues


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


def print_summary(issues: list[MigrationIssue]) -> None:
    """Print migration summary."""
    warnings = [i for i in issues if i.severity == "warning"]
    info = [i for i in issues if i.severity == "info"]

    print("\n" + "=" * 60)
    print("MIGRATION READINESS SUMMARY")
    print("=" * 60)
    print(f"Total issues: {len(issues)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Info: {len(info)}")

    if warnings:
        print("\nRequired changes before v1beta2 migration:")
        for issue in warnings:
            print(f"  - {issue.field}")

    print("\nDeadlines:")
    print("  - v1beta1 deprecated: NOW")
    print("  - v1beta1 removal: August 2026")
    print("  - Contract compatibility removal: August 2026")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check v1beta1 to v1beta2 migration readiness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="Single file to analyze",
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
        "--live",
        "-l",
        action="store_true",
        help="Analyze live cluster resources",
    )
    parser.add_argument(
        "--namespace",
        "-n",
        default=None,
        help="Namespace for live analysis (default: all namespaces)",
    )
    args = parser.parse_args()

    all_issues = []

    # Analyze files
    if args.file:
        all_issues.extend(analyze_file(args.file))
    elif args.dir:
        files = find_yaml_files([args.dir], args.recursive)
        for f in files:
            all_issues.extend(analyze_file(f))

    # Analyze live resources
    if args.live:
        print("Analyzing live cluster resources...")
        all_issues.extend(analyze_live_resources(args.namespace))

    if not all_issues and not args.live and not args.file and not args.dir:
        parser.print_help()
        return 0

    # Group issues by path
    by_path: dict[str, list[MigrationIssue]] = {}
    for issue in all_issues:
        by_path.setdefault(issue.path, []).append(issue)

    # Print issues
    for path, issues in by_path.items():
        print(f"\n{path}:")
        for issue in issues:
            print(f"  {issue}")

    print_summary(all_issues)

    # Return non-zero if there are warnings
    warnings = [i for i in all_issues if i.severity == "warning"]
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
