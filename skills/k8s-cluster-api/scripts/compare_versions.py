#!/usr/bin/env python3
"""Compare CAPI version specifications and API changes.

Helps identify differences between CAPI versions, including API changes,
deprecated fields, and migration requirements.

Usage:
    python compare_versions.py <from-version> <to-version>

Examples:
    python compare_versions.py v1.6.0 v1.7.0
    python compare_versions.py v1beta1 v1beta2 --api-only
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any


# Version change database
VERSION_CHANGES: dict[str, dict[str, Any]] = {
    "v1.6.0": {
        "release_date": "2024-04-23",
        "kubernetes": {"min": "v1.25.0", "max": "v1.29.x"},
        "go_version": "1.21",
        "api_version": "v1beta1",
        "features": [
            "ClusterClass topology variables",
            "MachinePool support improved",
            "In-place propagation for topology",
        ],
        "deprecations": [],
        "breaking_changes": [],
    },
    "v1.7.0": {
        "release_date": "2024-07-23",
        "kubernetes": {"min": "v1.26.0", "max": "v1.30.x"},
        "go_version": "1.22",
        "api_version": "v1beta1",
        "features": [
            "v1beta2 conditions (preview)",
            "Improved topology reconciliation",
            "Better error messages",
        ],
        "deprecations": [
            "UseExperimentalRetryJoin deprecated",
        ],
        "breaking_changes": [],
    },
    "v1.8.0": {
        "release_date": "2024-10-08",
        "kubernetes": {"min": "v1.27.0", "max": "v1.31.x"},
        "go_version": "1.22",
        "api_version": "v1beta1",
        "features": [
            "v1beta2 API (alpha)",
            "ClusterClass runtimeSDK hooks",
            "MachineSet preflight checks",
        ],
        "deprecations": [
            "status.phase fields deprecated in favor of conditions",
            "Legacy object references (Kind+APIVersion)",
        ],
        "breaking_changes": [],
    },
    "v1.9.0": {
        "release_date": "2025-01-14",
        "kubernetes": {"min": "v1.28.0", "max": "v1.32.x"},
        "go_version": "1.23",
        "api_version": "v1beta1",
        "features": [
            "v1beta2 API (beta)",
            "Improved ClusterClass patching",
            "MachineDeployment rollout strategy",
        ],
        "deprecations": [
            "duration fields with int type (use string)",
            "TypedObjectReference without suffix",
        ],
        "breaking_changes": [
            "Go 1.23 required",
        ],
    },
    "v1.10.0": {
        "release_date": "2025-04-08",
        "kubernetes": {"min": "v1.29.0", "max": "v1.33.x"},
        "go_version": "1.23",
        "api_version": "v1beta1",
        "features": [
            "SSA migration support",
            "ClusterClass dry-run",
            "Improved machine deletion",
        ],
        "deprecations": [
            "ControlPlaneRef/InfrastructureRef without Ref suffix",
        ],
        "breaking_changes": [],
    },
    "v1.11.0": {
        "release_date": "2025-07-08",
        "kubernetes": {"min": "v1.30.0", "max": "v1.34.x"},
        "go_version": "1.24",
        "api_version": "v1beta1",
        "features": [
            "ClusterClass variable discovery",
            "Improved rollout controls",
        ],
        "deprecations": [],
        "breaking_changes": [
            "Go 1.24 required",
        ],
    },
    "v1.12.0": {
        "release_date": "2025-10-07",
        "kubernetes": {"min": "v1.31.0", "max": "v1.35.x"},
        "go_version": "1.24",
        "api_version": "v1beta1",
        "features": [
            "v1beta2 conditions GA",
            "Enhanced topology validation",
            "Improved observability",
        ],
        "deprecations": [
            "v1beta1 conditions (use v1beta2)",
        ],
        "breaking_changes": [],
    },
}

# API field changes between v1beta1 and v1beta2
API_CHANGES: dict[str, list[dict[str, str]]] = {
    "v1beta1->v1beta2": [
        {
            "type": "field_rename",
            "kind": "Cluster",
            "old": "spec.infrastructureRef",
            "new": "spec.infrastructureRef (TypedObjectReference)",
            "description": "InfrastructureRef now uses TypedObjectReference type",
        },
        {
            "type": "field_rename",
            "kind": "Cluster",
            "old": "spec.controlPlaneRef",
            "new": "spec.controlPlaneRef (TypedObjectReference)",
            "description": "ControlPlaneRef now uses TypedObjectReference type",
        },
        {
            "type": "field_change",
            "kind": "Machine",
            "old": "status.phase",
            "new": "status.conditions",
            "description": "Phase deprecated; use conditions for state",
        },
        {
            "type": "field_add",
            "kind": "Cluster",
            "old": "",
            "new": "status.v1beta2.conditions",
            "description": "New v1beta2 conditions location",
        },
        {
            "type": "field_add",
            "kind": "MachineDeployment",
            "old": "",
            "new": "spec.strategy.rollingUpdate.deletePolicy",
            "description": "New delete policy for rollouts",
        },
        {
            "type": "behavior_change",
            "kind": "All",
            "old": "Integer durations (seconds)",
            "new": "String durations (e.g., '10m')",
            "description": "Duration fields now use string format",
        },
    ],
}


@dataclass
class VersionComparison:
    """Comparison between two versions."""

    from_version: str
    to_version: str
    kubernetes_change: dict[str, str] = field(default_factory=dict)
    go_change: dict[str, str] = field(default_factory=dict)
    new_features: list[str] = field(default_factory=list)
    deprecations: list[str] = field(default_factory=list)
    breaking_changes: list[str] = field(default_factory=list)
    api_changes: list[dict[str, str]] = field(default_factory=list)
    versions_between: list[str] = field(default_factory=list)


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse version string to tuple."""
    # Handle v1.X.Y format
    v = version.lstrip("v")
    parts = v.split(".")
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except ValueError:
        return (0, 0, 0)


def get_versions_between(from_v: str, to_v: str) -> list[str]:
    """Get list of versions between from and to."""
    from_tuple = parse_version(from_v)
    to_tuple = parse_version(to_v)

    versions = []
    for v in sorted(VERSION_CHANGES.keys(), key=parse_version):
        v_tuple = parse_version(v)
        if from_tuple < v_tuple <= to_tuple:
            versions.append(v)

    return versions


def compare_versions(from_v: str, to_v: str) -> VersionComparison:
    """Compare two CAPI versions."""
    comparison = VersionComparison(from_version=from_v, to_version=to_v)

    # Get all versions in range
    versions = get_versions_between(from_v, to_v)
    comparison.versions_between = versions

    # Aggregate changes
    for v in versions:
        info = VERSION_CHANGES.get(v, {})

        comparison.new_features.extend(info.get("features", []))
        comparison.deprecations.extend(info.get("deprecations", []))
        comparison.breaking_changes.extend(info.get("breaking_changes", []))

    # Kubernetes version changes
    from_info = VERSION_CHANGES.get(from_v, {})
    to_info = VERSION_CHANGES.get(to_v, {})

    if from_info and to_info:
        from_k8s = from_info.get("kubernetes", {})
        to_k8s = to_info.get("kubernetes", {})

        comparison.kubernetes_change = {
            "from_min": from_k8s.get("min", ""),
            "from_max": from_k8s.get("max", ""),
            "to_min": to_k8s.get("min", ""),
            "to_max": to_k8s.get("max", ""),
        }

        comparison.go_change = {
            "from": from_info.get("go_version", ""),
            "to": to_info.get("go_version", ""),
        }

    # API changes
    comparison.api_changes = API_CHANGES.get("v1beta1->v1beta2", [])

    return comparison


def print_comparison(comp: VersionComparison) -> None:
    """Print version comparison."""
    print(f"\n{'='*60}")
    print(f"CAPI Version Comparison: {comp.from_version} → {comp.to_version}")
    print("=" * 60)

    if comp.versions_between:
        print(f"\nVersions in range: {', '.join(comp.versions_between)}")

    # Kubernetes version
    if comp.kubernetes_change:
        print("\n📦 Kubernetes Version Requirements:")
        print(f"   From: {comp.kubernetes_change['from_min']} - {comp.kubernetes_change['from_max']}")
        print(f"   To:   {comp.kubernetes_change['to_min']} - {comp.kubernetes_change['to_max']}")

    # Go version
    if comp.go_change and comp.go_change["from"] != comp.go_change["to"]:
        print("\n🔧 Go Version:")
        print(f"   {comp.go_change['from']} → {comp.go_change['to']}")

    # Breaking changes
    if comp.breaking_changes:
        print("\n🔴 Breaking Changes:")
        for change in comp.breaking_changes:
            print(f"   • {change}")

    # Deprecations
    if comp.deprecations:
        print("\n⚠️  Deprecations:")
        for dep in comp.deprecations:
            print(f"   • {dep}")

    # New features
    if comp.new_features:
        print("\n✨ New Features:")
        for feature in comp.new_features:
            print(f"   • {feature}")

    # API changes
    if comp.api_changes:
        print("\n📝 API Changes (v1beta1 → v1beta2):")
        for change in comp.api_changes:
            change_type = change.get("type", "")
            kind = change.get("kind", "")
            icon = {
                "field_rename": "↔️",
                "field_change": "🔄",
                "field_add": "➕",
                "field_remove": "➖",
                "behavior_change": "⚙️",
            }.get(change_type, "·")

            print(f"\n   {icon} [{kind}] {change.get('description', '')}")
            if change.get("old"):
                print(f"      Old: {change['old']}")
            if change.get("new"):
                print(f"      New: {change['new']}")


def print_migration_checklist(comp: VersionComparison) -> None:
    """Print migration checklist."""
    print("\n" + "=" * 60)
    print("MIGRATION CHECKLIST")
    print("=" * 60)

    print("\n□ Pre-migration:")
    print(f"   □ Verify Kubernetes version meets {comp.kubernetes_change.get('to_min', 'N/A')}+ requirement")
    if comp.go_change and comp.go_change["from"] != comp.go_change["to"]:
        print(f"   □ Update Go to {comp.go_change['to']}")
    print("   □ Backup cluster state (clusterctl move or export)")
    print("   □ Review release notes for all versions in range")

    if comp.breaking_changes:
        print("\n□ Breaking changes to address:")
        for i, change in enumerate(comp.breaking_changes, 1):
            print(f"   □ {i}. {change}")

    if comp.deprecations:
        print("\n□ Deprecated features to migrate:")
        for i, dep in enumerate(comp.deprecations, 1):
            print(f"   □ {i}. {dep}")

    print("\n□ Post-migration:")
    print("   □ Run clusterctl upgrade plan")
    print("   □ Verify all clusters Ready")
    print("   □ Check conditions for any warnings")
    print("   □ Update provider versions if needed")


def list_versions() -> None:
    """List all known versions."""
    print("\nKnown CAPI Versions:")
    print("-" * 60)
    print(f"{'Version':<10} {'Release':<12} {'K8s Min':<10} {'K8s Max':<10} {'Go':<6}")
    print("-" * 60)

    for version in sorted(VERSION_CHANGES.keys(), key=parse_version):
        info = VERSION_CHANGES[version]
        k8s = info.get("kubernetes", {})
        print(
            f"{version:<10} {info.get('release_date', ''):<12} "
            f"{k8s.get('min', ''):<10} {k8s.get('max', ''):<10} "
            f"{info.get('go_version', ''):<6}"
        )


def export_json(comp: VersionComparison) -> str:
    """Export comparison to JSON."""
    return json.dumps(
        {
            "from_version": comp.from_version,
            "to_version": comp.to_version,
            "versions_between": comp.versions_between,
            "kubernetes_change": comp.kubernetes_change,
            "go_change": comp.go_change,
            "breaking_changes": comp.breaking_changes,
            "deprecations": comp.deprecations,
            "new_features": comp.new_features,
            "api_changes": comp.api_changes,
        },
        indent=2,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare CAPI version specifications",
    )
    parser.add_argument(
        "from_version",
        nargs="?",
        help="Source version (e.g., v1.6.0)",
    )
    parser.add_argument(
        "to_version",
        nargs="?",
        help="Target version (e.g., v1.7.0)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all known versions",
    )
    parser.add_argument(
        "--checklist",
        action="store_true",
        help="Include migration checklist",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write output to file",
    )
    args = parser.parse_args()

    if args.list:
        list_versions()
        return 0

    if not args.from_version or not args.to_version:
        print("Error: Both from_version and to_version required", file=sys.stderr)
        print("Use --list to see available versions", file=sys.stderr)
        return 1

    # Normalize versions
    from_v = args.from_version if args.from_version.startswith("v") else f"v{args.from_version}"
    to_v = args.to_version if args.to_version.startswith("v") else f"v{args.to_version}"

    # Validate versions exist
    if from_v not in VERSION_CHANGES:
        print(f"Warning: Version {from_v} not in database", file=sys.stderr)
    if to_v not in VERSION_CHANGES:
        print(f"Warning: Version {to_v} not in database", file=sys.stderr)

    comparison = compare_versions(from_v, to_v)

    if args.format == "json" or args.output:
        output = export_json(comparison)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Comparison written to: {args.output}")
        else:
            print(output)
    else:
        print_comparison(comparison)
        if args.checklist:
            print_migration_checklist(comparison)

    return 0


if __name__ == "__main__":
    sys.exit(main())
