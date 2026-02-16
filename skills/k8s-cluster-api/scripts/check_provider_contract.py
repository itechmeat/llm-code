#!/usr/bin/env python3
"""Verify provider CRD compliance with CAPI contracts.

Checks that infrastructure, bootstrap, and control plane providers
implement required fields and behaviors per CAPI contract specifications.

Usage:
    python check_provider_contract.py [options]

Examples:
    python check_provider_contract.py --provider aws
    python check_provider_contract.py --type infrastructure
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any


# Contract requirements from CAPI documentation
INFRASTRUCTURE_CLUSTER_CONTRACT = {
    "required_spec_fields": [
        "controlPlaneEndpoint",  # Must expose API endpoint
    ],
    "required_status_fields": [
        "ready",  # Boolean ready status
    ],
    "optional_status_fields": [
        "failureReason",
        "failureMessage",
        "conditions",
    ],
    "required_behaviors": [
        "Must set OwnerReference to Cluster",
        "Must report Ready=true when infrastructure provisioned",
        "Must populate controlPlaneEndpoint when available",
    ],
}

INFRASTRUCTURE_MACHINE_CONTRACT = {
    "required_spec_fields": [
        "providerID",  # Cloud provider instance ID
    ],
    "required_status_fields": [
        "ready",
        "addresses",  # Node addresses
    ],
    "optional_status_fields": [
        "failureReason",
        "failureMessage",
        "conditions",
    ],
    "required_behaviors": [
        "Must set OwnerReference to Machine",
        "Must report Ready=true when instance provisioned",
        "Must populate providerID when instance created",
        "Must report addresses for node registration",
    ],
}

BOOTSTRAP_CONFIG_CONTRACT = {
    "required_spec_fields": [],
    "required_status_fields": [
        "ready",
        "dataSecretName",  # Secret with bootstrap data
    ],
    "optional_status_fields": [
        "failureReason",
        "failureMessage",
        "conditions",
    ],
    "required_behaviors": [
        "Must create Secret with bootstrap data",
        "Must set dataSecretName when data ready",
        "Must report Ready=true when bootstrap data available",
    ],
}

CONTROL_PLANE_CONTRACT = {
    "required_spec_fields": [
        "version",  # Kubernetes version
        "replicas",  # Number of control plane nodes
    ],
    "required_status_fields": [
        "ready",
        "initialized",  # Control plane bootstrapped
        "replicas",
        "readyReplicas",
        "updatedReplicas",
    ],
    "optional_status_fields": [
        "unavailableReplicas",
        "version",
        "conditions",
        "externalManagedControlPlane",  # For managed k8s
    ],
    "required_behaviors": [
        "Must set OwnerReference to Cluster",
        "Must manage control plane Machines",
        "Must report initialized=true after first control plane node",
        "Must populate kubeconfig Secret",
        "Must support rolling updates",
    ],
}

IPAM_CONTRACT = {
    "required_spec_fields": [],
    "required_status_fields": [],
    "required_behaviors": [
        "Must watch IPAddressClaim resources",
        "Must create IPAddress for claims",
        "Must set claim.status.addressRef when IP allocated",
    ],
}


@dataclass
class ContractViolation:
    """Contract violation finding."""

    severity: str  # error, warning, info
    category: str
    crd: str
    message: str
    requirement: str = ""


@dataclass
class ContractReport:
    """Contract compliance report."""

    provider: str
    provider_type: str
    violations: list[ContractViolation] = field(default_factory=list)
    checked_crds: list[str] = field(default_factory=list)

    def add_violation(
        self,
        severity: str,
        category: str,
        crd: str,
        message: str,
        requirement: str = "",
    ) -> None:
        self.violations.append(
            ContractViolation(severity, category, crd, message, requirement)
        )

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "error")

    @property
    def is_compliant(self) -> bool:
        return self.error_count == 0


def find_kubectl() -> str | None:
    """Find kubectl binary."""
    return shutil.which("kubectl")


def run_kubectl(args: list[str]) -> tuple[bool, str, str]:
    """Run kubectl command."""
    kubectl = find_kubectl()
    if not kubectl:
        return False, "", "kubectl not found"

    cmd = [kubectl] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"


def get_crds(api_group: str) -> list[dict[str, Any]]:
    """Get CRDs for an API group."""
    success, stdout, _ = run_kubectl(
        ["get", "crds", "-o", "json"]
    )
    if not success:
        return []

    try:
        data = json.loads(stdout)
        items = data.get("items", [])
        # Filter by API group
        return [
            crd
            for crd in items
            if crd.get("spec", {}).get("group", "").endswith(api_group)
        ]
    except json.JSONDecodeError:
        return []


def get_crd_schema(crd: dict[str, Any]) -> dict[str, Any]:
    """Extract OpenAPI schema from CRD."""
    versions = crd.get("spec", {}).get("versions", [])
    for version in versions:
        if version.get("served"):
            schema = version.get("schema", {}).get("openAPIV3Schema", {})
            return schema
    return {}


def check_schema_fields(
    schema: dict[str, Any],
    required_fields: list[str],
    path: str,
) -> list[str]:
    """Check if schema contains required fields."""
    missing = []

    # Navigate to the correct path (spec or status)
    current = schema
    for part in path.split("."):
        if part:
            properties = current.get("properties", {})
            if part in properties:
                current = properties[part]
            else:
                return required_fields  # Path not found, all fields missing

    properties = current.get("properties", {})
    for field_name in required_fields:
        # Handle nested fields
        parts = field_name.split(".")
        if parts[0] not in properties:
            missing.append(field_name)

    return missing


def check_infrastructure_cluster(
    crd: dict[str, Any],
    report: ContractReport,
) -> None:
    """Check infrastructure cluster CRD compliance."""
    crd_name = crd.get("metadata", {}).get("name", "unknown")
    schema = get_crd_schema(crd)

    if not schema:
        report.add_violation(
            "error",
            "Schema",
            crd_name,
            "No OpenAPI schema found in CRD",
        )
        return

    contract = INFRASTRUCTURE_CLUSTER_CONTRACT

    # Check spec fields
    missing_spec = check_schema_fields(schema, contract["required_spec_fields"], "spec")
    for field_name in missing_spec:
        report.add_violation(
            "error",
            "Spec",
            crd_name,
            f"Missing required spec field: {field_name}",
            f"Contract requires spec.{field_name}",
        )

    # Check status fields
    missing_status = check_schema_fields(schema, contract["required_status_fields"], "status")
    for field_name in missing_status:
        report.add_violation(
            "error",
            "Status",
            crd_name,
            f"Missing required status field: {field_name}",
            f"Contract requires status.{field_name}",
        )

    # Check for conditions support
    status_props = schema.get("properties", {}).get("status", {}).get("properties", {})
    if "conditions" not in status_props:
        report.add_violation(
            "warning",
            "Conditions",
            crd_name,
            "No conditions field in status",
            "Conditions recommended for observability",
        )


def check_infrastructure_machine(
    crd: dict[str, Any],
    report: ContractReport,
) -> None:
    """Check infrastructure machine CRD compliance."""
    crd_name = crd.get("metadata", {}).get("name", "unknown")
    schema = get_crd_schema(crd)

    if not schema:
        report.add_violation(
            "error",
            "Schema",
            crd_name,
            "No OpenAPI schema found in CRD",
        )
        return

    contract = INFRASTRUCTURE_MACHINE_CONTRACT

    # Check spec fields
    spec_props = schema.get("properties", {}).get("spec", {}).get("properties", {})
    if "providerID" not in spec_props:
        report.add_violation(
            "error",
            "Spec",
            crd_name,
            "Missing providerID field in spec",
            "Contract requires spec.providerID for node correlation",
        )

    # Check status fields
    status_props = schema.get("properties", {}).get("status", {}).get("properties", {})

    if "ready" not in status_props:
        report.add_violation(
            "error",
            "Status",
            crd_name,
            "Missing ready field in status",
        )

    if "addresses" not in status_props:
        report.add_violation(
            "error",
            "Status",
            crd_name,
            "Missing addresses field in status",
            "Contract requires status.addresses for node registration",
        )


def check_bootstrap_config(
    crd: dict[str, Any],
    report: ContractReport,
) -> None:
    """Check bootstrap config CRD compliance."""
    crd_name = crd.get("metadata", {}).get("name", "unknown")
    schema = get_crd_schema(crd)

    if not schema:
        report.add_violation(
            "error",
            "Schema",
            crd_name,
            "No OpenAPI schema found in CRD",
        )
        return

    status_props = schema.get("properties", {}).get("status", {}).get("properties", {})

    if "ready" not in status_props:
        report.add_violation(
            "error",
            "Status",
            crd_name,
            "Missing ready field in status",
        )

    if "dataSecretName" not in status_props:
        report.add_violation(
            "error",
            "Status",
            crd_name,
            "Missing dataSecretName field in status",
            "Contract requires status.dataSecretName pointing to bootstrap data Secret",
        )


def check_control_plane(
    crd: dict[str, Any],
    report: ContractReport,
) -> None:
    """Check control plane CRD compliance."""
    crd_name = crd.get("metadata", {}).get("name", "unknown")
    schema = get_crd_schema(crd)

    if not schema:
        report.add_violation(
            "error",
            "Schema",
            crd_name,
            "No OpenAPI schema found in CRD",
        )
        return

    contract = CONTROL_PLANE_CONTRACT

    # Check spec fields
    spec_props = schema.get("properties", {}).get("spec", {}).get("properties", {})

    for field_name in contract["required_spec_fields"]:
        if field_name not in spec_props:
            report.add_violation(
                "error",
                "Spec",
                crd_name,
                f"Missing required spec field: {field_name}",
            )

    # Check status fields
    status_props = schema.get("properties", {}).get("status", {}).get("properties", {})

    for field_name in contract["required_status_fields"]:
        if field_name not in status_props:
            report.add_violation(
                "error",
                "Status",
                crd_name,
                f"Missing required status field: {field_name}",
            )


def detect_provider_type(crd_name: str) -> str:
    """Detect provider type from CRD name."""
    if "cluster" in crd_name.lower() and "infrastructure" in crd_name.lower():
        return "infrastructure-cluster"
    if "machine" in crd_name.lower() and "infrastructure" in crd_name.lower():
        return "infrastructure-machine"
    if "bootstrap" in crd_name.lower():
        return "bootstrap"
    if "controlplane" in crd_name.lower():
        return "controlplane"
    return "unknown"


def run_compliance_check(
    provider_filter: str | None,
    type_filter: str | None,
) -> list[ContractReport]:
    """Run compliance checks on installed providers."""
    reports = []

    # API groups to check
    api_groups = [
        "infrastructure.cluster.x-k8s.io",
        "bootstrap.cluster.x-k8s.io",
        "controlplane.cluster.x-k8s.io",
    ]

    for api_group in api_groups:
        crds = get_crds(api_group)

        for crd in crds:
            crd_name = crd.get("metadata", {}).get("name", "")

            # Extract provider name (e.g., "aws" from "awsclusters.infrastructure...")
            kind = crd.get("spec", {}).get("names", {}).get("kind", "")
            provider_name = kind.lower().replace("cluster", "").replace("machine", "").replace("config", "").replace("controlplane", "")

            # Apply filters
            if provider_filter and provider_filter.lower() not in provider_name:
                continue

            crd_type = detect_provider_type(crd_name)
            if type_filter and type_filter not in crd_type:
                continue

            report = ContractReport(
                provider=provider_name or "core",
                provider_type=crd_type,
            )
            report.checked_crds.append(crd_name)

            # Run appropriate check
            if crd_type == "infrastructure-cluster":
                check_infrastructure_cluster(crd, report)
            elif crd_type == "infrastructure-machine":
                check_infrastructure_machine(crd, report)
            elif crd_type == "bootstrap":
                check_bootstrap_config(crd, report)
            elif crd_type == "controlplane":
                check_control_plane(crd, report)

            # Only add report if we checked something
            if report.checked_crds:
                reports.append(report)

    return reports


def print_report(report: ContractReport) -> None:
    """Print compliance report."""
    status = "✓ COMPLIANT" if report.is_compliant else "✗ NON-COMPLIANT"
    print(f"\n{'='*60}")
    print(f"Provider: {report.provider} ({report.provider_type})")
    print(f"Status: {status}")
    print("=" * 60)

    print(f"\nChecked CRDs:")
    for crd in report.checked_crds:
        print(f"  - {crd}")

    if not report.violations:
        print("\n✓ All contract requirements satisfied")
        return

    # Group by severity
    for severity in ["error", "warning", "info"]:
        violations = [v for v in report.violations if v.severity == severity]
        if not violations:
            continue

        icon = {"error": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(severity, "·")
        print(f"\n{icon} {severity.upper()} ({len(violations)})")

        for v in violations:
            print(f"\n  [{v.category}] {v.message}")
            if v.requirement:
                print(f"    Requirement: {v.requirement}")


def print_summary(reports: list[ContractReport]) -> None:
    """Print overall summary."""
    total = len(reports)
    compliant = sum(1 for r in reports if r.is_compliant)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total providers checked: {total}")
    print(f"Compliant: {compliant}")
    print(f"Non-compliant: {total - compliant}")

    if any(not r.is_compliant for r in reports):
        print("\nNon-compliant providers:")
        for r in reports:
            if not r.is_compliant:
                print(f"  - {r.provider} ({r.provider_type}): {r.error_count} errors")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify provider CRD compliance with CAPI contracts",
    )
    parser.add_argument(
        "--provider",
        "-p",
        default=None,
        help="Filter by provider name (e.g., aws, azure)",
    )
    parser.add_argument(
        "--type",
        "-t",
        choices=["infrastructure", "bootstrap", "controlplane"],
        default=None,
        help="Filter by provider type",
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

    if not find_kubectl():
        print("Error: kubectl not found in PATH", file=sys.stderr)
        return 1

    print("Checking provider contract compliance...")
    reports = run_compliance_check(args.provider, args.type)

    if not reports:
        print("No provider CRDs found to check")
        return 0

    if args.format == "json" or args.output:
        output = json.dumps(
            [
                {
                    "provider": r.provider,
                    "type": r.provider_type,
                    "compliant": r.is_compliant,
                    "crds": r.checked_crds,
                    "violations": [
                        {
                            "severity": v.severity,
                            "category": v.category,
                            "crd": v.crd,
                            "message": v.message,
                            "requirement": v.requirement,
                        }
                        for v in r.violations
                    ],
                }
                for r in reports
            ],
            indent=2,
        )
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Report written to: {args.output}")
        else:
            print(output)
    else:
        for report in reports:
            print_report(report)
        print_summary(reports)

    # Exit code based on compliance
    has_errors = any(not r.is_compliant for r in reports)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
