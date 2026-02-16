#!/usr/bin/env python3
"""Check cluster health by analyzing conditions across all CAPI objects.

This script analyzes conditions from Cluster API resources to identify
health issues and provide actionable recommendations.

Usage:
    python check_cluster_health.py <cluster-name>
    python check_cluster_health.py <cluster-name> -n <namespace>

Examples:
    python check_cluster_health.py my-cluster
    python check_cluster_health.py my-cluster -n clusters --output health.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def find_kubectl() -> str | None:
    """Find kubectl binary in PATH."""
    return shutil.which("kubectl")


def run_kubectl(
    args: list[str],
    namespace: str | None = None,
    timeout: int = 30,
) -> dict[str, Any] | None:
    """Run kubectl command and return JSON output."""
    kubectl = find_kubectl()
    if not kubectl:
        raise RuntimeError("kubectl not found in PATH")

    cmd = [kubectl] + args + ["-o", "json"]
    if namespace:
        cmd.extend(["-n", namespace])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


class HealthIssue:
    def __init__(
        self,
        resource: str,
        name: str,
        condition_type: str,
        status: str,
        reason: str,
        message: str,
        severity: str = "warning",
    ):
        self.resource = resource
        self.name = name
        self.condition_type = condition_type
        self.status = status
        self.reason = reason
        self.message = message
        self.severity = severity

    def to_dict(self) -> dict[str, str]:
        return {
            "resource": self.resource,
            "name": self.name,
            "condition_type": self.condition_type,
            "status": self.status,
            "reason": self.reason,
            "message": self.message,
            "severity": self.severity,
        }

    def __str__(self) -> str:
        icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(self.severity, "•")
        return (
            f"{icon} {self.resource}/{self.name}\n"
            f"   Condition: {self.condition_type} = {self.status}\n"
            f"   Reason: {self.reason}\n"
            f"   Message: {self.message}"
        )


# Conditions that indicate unhealthy state when False or Unknown
CRITICAL_CONDITIONS = {
    "Ready": "error",
    "Available": "warning",
    "InfrastructureReady": "error",
    "ControlPlaneReady": "error",
    "BootstrapReady": "warning",
    "Provisioned": "error",
    "Initialized": "warning",
}

# Expected True conditions
EXPECTED_TRUE = [
    "Ready",
    "Available",
    "InfrastructureReady",
    "ControlPlaneReady",
    "BootstrapReady",
    "Provisioned",
    "Initialized",
    "UpToDate",
]


def analyze_conditions(
    resource_type: str,
    name: str,
    conditions: list[dict[str, Any]],
) -> list[HealthIssue]:
    """Analyze conditions list and return health issues."""
    issues = []

    for cond in conditions:
        cond_type = cond.get("type", "")
        status = cond.get("status", "")
        reason = cond.get("reason", "")
        message = cond.get("message", "")

        # Check conditions that should be True
        if cond_type in EXPECTED_TRUE and status != "True":
            severity = CRITICAL_CONDITIONS.get(cond_type, "warning")
            issues.append(
                HealthIssue(
                    resource=resource_type,
                    name=name,
                    condition_type=cond_type,
                    status=status,
                    reason=reason,
                    message=message,
                    severity=severity,
                )
            )

        # Check for specific error reasons
        error_reasons = [
            "ProvisioningFailed",
            "InvalidConfiguration",
            "WaitingForInfrastructure",
            "WaitingForControlPlane",
            "ScalingDown",
            "Deleting",
            "Failed",
            "ProviderError",
        ]
        if reason in error_reasons:
            issues.append(
                HealthIssue(
                    resource=resource_type,
                    name=name,
                    condition_type=cond_type,
                    status=status,
                    reason=reason,
                    message=message,
                    severity="warning",
                )
            )

    return issues


def get_cluster_resources(
    cluster_name: str,
    namespace: str | None,
) -> dict[str, list[dict[str, Any]]]:
    """Get all CAPI resources for a cluster."""
    resources: dict[str, list[dict[str, Any]]] = {}

    # Get Cluster
    cluster = run_kubectl(["get", "cluster", cluster_name], namespace)
    if cluster:
        resources["Cluster"] = [cluster]

    # Get Machines
    label_selector = f"cluster.x-k8s.io/cluster-name={cluster_name}"
    machines = run_kubectl(["get", "machines", "-l", label_selector], namespace)
    if machines and "items" in machines:
        resources["Machine"] = machines["items"]

    # Get MachineSets
    machinesets = run_kubectl(["get", "machinesets", "-l", label_selector], namespace)
    if machinesets and "items" in machinesets:
        resources["MachineSet"] = machinesets["items"]

    # Get MachineDeployments
    mds = run_kubectl(["get", "machinedeployments", "-l", label_selector], namespace)
    if mds and "items" in mds:
        resources["MachineDeployment"] = mds["items"]

    # Get KubeadmControlPlane (by owner reference)
    kcp_name = None
    if cluster:
        cp_ref = cluster.get("spec", {}).get("controlPlaneRef", {})
        if cp_ref.get("kind") == "KubeadmControlPlane":
            kcp_name = cp_ref.get("name")

    if kcp_name:
        kcp = run_kubectl(
            ["get", "kubeadmcontrolplanes", kcp_name],
            namespace,
        )
        if kcp:
            resources["KubeadmControlPlane"] = [kcp]

    return resources


def check_cluster_health(
    cluster_name: str,
    namespace: str | None,
) -> tuple[dict[str, Any], list[HealthIssue]]:
    """Check cluster health and return summary and issues."""
    resources = get_cluster_resources(cluster_name, namespace)
    all_issues = []

    summary = {
        "cluster_name": cluster_name,
        "namespace": namespace or "default",
        "timestamp": datetime.now().isoformat(),
        "resources": {},
    }

    for resource_type, items in resources.items():
        summary["resources"][resource_type] = len(items)

        for item in items:
            name = item.get("metadata", {}).get("name", "unknown")

            # Check status conditions
            status = item.get("status", {})

            # v1beta2 conditions location
            conditions = status.get("conditions", [])

            # Fallback to v1beta2 nested location
            if not conditions:
                v1beta2 = status.get("v1beta2", {})
                conditions = v1beta2.get("conditions", [])

            if conditions:
                issues = analyze_conditions(resource_type, name, conditions)
                all_issues.extend(issues)

    summary["total_issues"] = len(all_issues)
    summary["errors"] = sum(1 for i in all_issues if i.severity == "error")
    summary["warnings"] = sum(1 for i in all_issues if i.severity == "warning")

    return summary, all_issues


def print_health_report(
    summary: dict[str, Any],
    issues: list[HealthIssue],
) -> None:
    """Print formatted health report."""
    print("=" * 60)
    print("CLUSTER HEALTH REPORT")
    print("=" * 60)
    print(f"Cluster: {summary['cluster_name']}")
    print(f"Namespace: {summary['namespace']}")
    print(f"Timestamp: {summary['timestamp']}")
    print()

    print("Resources found:")
    for resource, count in summary.get("resources", {}).items():
        print(f"  {resource}: {count}")

    print()
    print(f"Health Status: ", end="")

    if summary["errors"] > 0:
        print("❌ UNHEALTHY")
    elif summary["warnings"] > 0:
        print("⚠️ DEGRADED")
    else:
        print("✅ HEALTHY")

    print(f"  Errors: {summary['errors']}")
    print(f"  Warnings: {summary['warnings']}")

    if issues:
        print()
        print("Issues:")
        print("-" * 40)
        for issue in issues:
            print(issue)
            print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check cluster health by analyzing CAPI conditions",
    )
    parser.add_argument(
        "cluster_name",
        help="Name of the cluster to check",
    )
    parser.add_argument(
        "--namespace",
        "-n",
        default=None,
        help="Namespace of the cluster",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON file for results",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON only",
    )
    args = parser.parse_args()

    try:
        if not find_kubectl():
            raise RuntimeError("kubectl not found in PATH")

        summary, issues = check_cluster_health(args.cluster_name, args.namespace)

        if args.json:
            output = {
                "summary": summary,
                "issues": [i.to_dict() for i in issues],
            }
            print(json.dumps(output, indent=2))
        else:
            print_health_report(summary, issues)

        if args.output:
            output = {
                "summary": summary,
                "issues": [i.to_dict() for i in issues],
            }
            args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
            print(f"\nResults saved to: {args.output}")

        # Exit code based on health
        if summary["errors"] > 0:
            return 2
        if summary["warnings"] > 0:
            return 1
        return 0

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
