#!/usr/bin/env python3
"""Analyze conditions from all CAPI objects in a cluster.

This script parses and reports conditions from Cluster API resources,
identifying False/Unknown conditions and providing a summary view.

Usage:
    python analyze_conditions.py [-n <namespace>]
    python analyze_conditions.py --cluster <cluster-name>

Examples:
    python analyze_conditions.py -n clusters
    python analyze_conditions.py --cluster my-cluster --format table
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Any


def find_kubectl() -> str | None:
    """Find kubectl binary in PATH."""
    return shutil.which("kubectl")


def run_kubectl_json(
    resource: str,
    namespace: str | None = None,
    label_selector: str | None = None,
    all_namespaces: bool = False,
) -> list[dict[str, Any]]:
    """Run kubectl get and return items list."""
    kubectl = find_kubectl()
    if not kubectl:
        return []

    cmd = [kubectl, "get", resource, "-o", "json"]

    if all_namespaces:
        cmd.append("--all-namespaces")
    elif namespace:
        cmd.extend(["-n", namespace])

    if label_selector:
        cmd.extend(["-l", label_selector])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        return data.get("items", [data] if "kind" in data and "List" not in data.get("kind", "") else [])
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return []


class ConditionInfo:
    def __init__(
        self,
        resource_kind: str,
        resource_name: str,
        resource_namespace: str,
        condition_type: str,
        status: str,
        reason: str,
        message: str,
        last_transition: str,
    ):
        self.resource_kind = resource_kind
        self.resource_name = resource_name
        self.resource_namespace = resource_namespace
        self.condition_type = condition_type
        self.status = status
        self.reason = reason
        self.message = message
        self.last_transition = last_transition

    @property
    def is_healthy(self) -> bool:
        """Check if condition indicates healthy state."""
        positive_conditions = [
            "Ready",
            "Available",
            "InfrastructureReady",
            "ControlPlaneReady",
            "BootstrapReady",
            "Provisioned",
            "Initialized",
            "UpToDate",
            "MachinesReady",
            "RemediationAllowed",
        ]
        negative_conditions = [
            "Stalled",
            "Deleting",
            "Paused",
        ]

        if self.condition_type in positive_conditions:
            return self.status == "True"
        if self.condition_type in negative_conditions:
            return self.status == "False"
        return True  # Unknown conditions assumed healthy

    def to_row(self) -> list[str]:
        """Convert to table row."""
        status_icon = {"True": "✓", "False": "✗", "Unknown": "?"}.get(self.status, "?")
        return [
            self.resource_kind,
            f"{self.resource_namespace}/{self.resource_name}",
            self.condition_type,
            f"{status_icon} {self.status}",
            self.reason or "-",
        ]


def extract_conditions(item: dict[str, Any]) -> list[ConditionInfo]:
    """Extract all conditions from a resource."""
    conditions = []

    kind = item.get("kind", "Unknown")
    metadata = item.get("metadata", {})
    name = metadata.get("name", "unknown")
    namespace = metadata.get("namespace", "default")
    status = item.get("status", {})

    # Try v1beta2 conditions first
    conds = status.get("conditions", [])

    # Fallback to nested v1beta2
    if not conds:
        v1beta2 = status.get("v1beta2", {})
        conds = v1beta2.get("conditions", [])

    for cond in conds:
        conditions.append(
            ConditionInfo(
                resource_kind=kind,
                resource_name=name,
                resource_namespace=namespace,
                condition_type=cond.get("type", ""),
                status=cond.get("status", "Unknown"),
                reason=cond.get("reason", ""),
                message=cond.get("message", ""),
                last_transition=cond.get("lastTransitionTime", ""),
            )
        )

    return conditions


def collect_all_conditions(
    namespace: str | None,
    cluster_name: str | None,
    all_namespaces: bool,
) -> list[ConditionInfo]:
    """Collect conditions from all CAPI resources."""
    all_conditions = []

    resources = [
        "clusters.cluster.x-k8s.io",
        "machines.cluster.x-k8s.io",
        "machinesets.cluster.x-k8s.io",
        "machinedeployments.cluster.x-k8s.io",
        "machinepools.cluster.x-k8s.io",
        "machinehealthchecks.cluster.x-k8s.io",
        "kubeadmconfigs.bootstrap.cluster.x-k8s.io",
        "kubeadmcontrolplanes.controlplane.cluster.x-k8s.io",
    ]

    label_selector = None
    if cluster_name:
        label_selector = f"cluster.x-k8s.io/cluster-name={cluster_name}"

    for resource in resources:
        items = run_kubectl_json(
            resource,
            namespace=namespace,
            label_selector=label_selector,
            all_namespaces=all_namespaces and not namespace,
        )

        for item in items:
            conditions = extract_conditions(item)
            all_conditions.extend(conditions)

    # Also get Cluster directly if filtering by name
    if cluster_name:
        clusters = run_kubectl_json(
            f"clusters.cluster.x-k8s.io/{cluster_name}",
            namespace=namespace,
        )
        for item in clusters:
            if item.get("kind") == "Cluster":
                conditions = extract_conditions(item)
                all_conditions.extend(conditions)

    return all_conditions


def print_table(conditions: list[ConditionInfo], show_all: bool) -> None:
    """Print conditions as formatted table."""
    # Filter to show only unhealthy by default
    if not show_all:
        conditions = [c for c in conditions if not c.is_healthy]

    if not conditions:
        print("No unhealthy conditions found ✅")
        return

    # Table headers
    headers = ["KIND", "RESOURCE", "CONDITION", "STATUS", "REASON"]

    # Calculate column widths
    rows = [c.to_row() for c in conditions]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    # Print header
    header_line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))


def print_summary(conditions: list[ConditionInfo]) -> None:
    """Print conditions summary."""
    total = len(conditions)
    healthy = sum(1 for c in conditions if c.is_healthy)
    unhealthy = total - healthy

    by_kind: dict[str, dict[str, int]] = {}
    for c in conditions:
        kind = c.resource_kind
        if kind not in by_kind:
            by_kind[kind] = {"total": 0, "healthy": 0, "unhealthy": 0}
        by_kind[kind]["total"] += 1
        if c.is_healthy:
            by_kind[kind]["healthy"] += 1
        else:
            by_kind[kind]["unhealthy"] += 1

    print("\n" + "=" * 50)
    print("CONDITIONS SUMMARY")
    print("=" * 50)
    print(f"Total conditions: {total}")
    print(f"  Healthy: {healthy} ✓")
    print(f"  Unhealthy: {unhealthy} ✗")

    print("\nBy resource type:")
    for kind, stats in sorted(by_kind.items()):
        status = "✓" if stats["unhealthy"] == 0 else "✗"
        print(f"  {kind}: {stats['healthy']}/{stats['total']} healthy {status}")

    # List unhealthy condition types
    unhealthy_types = set(c.condition_type for c in conditions if not c.is_healthy)
    if unhealthy_types:
        print("\nUnhealthy condition types:")
        for ct in sorted(unhealthy_types):
            print(f"  - {ct}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze conditions from CAPI resources",
    )
    parser.add_argument(
        "--namespace",
        "-n",
        default=None,
        help="Namespace to analyze",
    )
    parser.add_argument(
        "--cluster",
        "-c",
        default=None,
        help="Filter by cluster name",
    )
    parser.add_argument(
        "--all-namespaces",
        "-A",
        action="store_true",
        help="Analyze all namespaces",
    )
    parser.add_argument(
        "--show-all",
        "-a",
        action="store_true",
        help="Show all conditions, not just unhealthy",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "summary"],
        default="table",
        help="Output format (default: table)",
    )
    args = parser.parse_args()

    if not find_kubectl():
        print("Error: kubectl not found in PATH", file=sys.stderr)
        return 1

    print("Collecting conditions from CAPI resources...")
    conditions = collect_all_conditions(
        args.namespace,
        args.cluster,
        args.all_namespaces,
    )

    if not conditions:
        print("No CAPI resources found")
        return 0

    if args.format == "json":
        output = [
            {
                "resource": f"{c.resource_kind}/{c.resource_namespace}/{c.resource_name}",
                "condition": c.condition_type,
                "status": c.status,
                "reason": c.reason,
                "message": c.message,
                "healthy": c.is_healthy,
            }
            for c in conditions
        ]
        print(json.dumps(output, indent=2))
    elif args.format == "summary":
        print_summary(conditions)
    else:
        print_table(conditions, args.show_all)
        print_summary(conditions)

    # Exit code based on health
    unhealthy = [c for c in conditions if not c.is_healthy]
    return 1 if unhealthy else 0


if __name__ == "__main__":
    sys.exit(main())
