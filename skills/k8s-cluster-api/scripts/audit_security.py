#!/usr/bin/env python3
"""Audit security posture of CAPI clusters.

Checks Pod Security Standards compliance, security-related conditions,
and configuration against best practices.

Usage:
    python audit_security.py [options]

Examples:
    python audit_security.py --cluster my-cluster
    python audit_security.py --namespace clusters --output report.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    """Security finding."""

    severity: str  # high, medium, low, info
    category: str
    resource: str
    message: str
    recommendation: str = ""


@dataclass
class AuditReport:
    """Audit report."""

    cluster_name: str
    findings: list[Finding] = field(default_factory=list)

    def add(
        self,
        severity: str,
        category: str,
        resource: str,
        message: str,
        recommendation: str = "",
    ) -> None:
        self.findings.append(
            Finding(severity, category, resource, message, recommendation)
        )

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "high")

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "medium")

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "low")


def find_kubectl() -> str | None:
    """Find kubectl binary."""
    return shutil.which("kubectl")


def run_kubectl_json(
    resource: str,
    namespace: str | None = None,
    all_namespaces: bool = False,
) -> list[dict[str, Any]]:
    """Run kubectl get and return items."""
    kubectl = find_kubectl()
    if not kubectl:
        return []

    cmd = [kubectl, "get", resource, "-o", "json"]
    if all_namespaces:
        cmd.append("--all-namespaces")
    elif namespace:
        cmd.extend(["-n", namespace])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        items = data.get("items", [])
        if not items and "kind" in data and "List" not in data.get("kind", ""):
            return [data]
        return items
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return []


def check_pss_configuration(
    cluster: dict[str, Any],
    report: AuditReport,
) -> None:
    """Check Pod Security Standards configuration."""
    spec = cluster.get("spec", {})
    topology = spec.get("topology", {})
    variables = topology.get("variables", [])

    name = cluster.get("metadata", {}).get("name", "unknown")
    namespace = cluster.get("metadata", {}).get("namespace", "default")
    resource = f"Cluster/{namespace}/{name}"

    # Check for podSecurityStandard variable
    pss_var = None
    for var in variables:
        if var.get("name") == "podSecurityStandard":
            pss_var = var.get("value", {})
            break

    if not pss_var:
        report.add(
            severity="medium",
            category="Pod Security",
            resource=resource,
            message="No podSecurityStandard variable configured",
            recommendation="Set podSecurityStandard variable with enforce level",
        )
        return

    # Check enforcement level
    enforce = pss_var.get("enforce", "")
    if not enforce or enforce == "privileged":
        report.add(
            severity="high",
            category="Pod Security",
            resource=resource,
            message=f"PSS enforce level is '{enforce or 'not set'}' (should be baseline or restricted)",
            recommendation="Set podSecurityStandard.enforce to 'baseline' or 'restricted'",
        )
    elif enforce == "baseline":
        report.add(
            severity="low",
            category="Pod Security",
            resource=resource,
            message="PSS enforce level is 'baseline' (consider 'restricted' for production)",
            recommendation="Consider 'restricted' level for higher security",
        )

    # Check audit logging
    audit = pss_var.get("audit", "")
    if not audit:
        report.add(
            severity="low",
            category="Pod Security",
            resource=resource,
            message="PSS audit level not configured",
            recommendation="Set podSecurityStandard.audit for violation logging",
        )


def check_kubeadm_security(
    kcp: dict[str, Any],
    report: AuditReport,
) -> None:
    """Check KubeadmControlPlane security settings."""
    name = kcp.get("metadata", {}).get("name", "unknown")
    namespace = kcp.get("metadata", {}).get("namespace", "default")
    resource = f"KubeadmControlPlane/{namespace}/{name}"

    spec = kcp.get("spec", {})
    kcs = spec.get("kubeadmConfigSpec", {})

    # Check for encryption configuration
    cluster_config = kcs.get("clusterConfiguration", {})
    api_server = cluster_config.get("apiServer", {})
    extra_args = api_server.get("extraArgs", {})

    if "encryption-provider-config" not in extra_args:
        report.add(
            severity="medium",
            category="Encryption",
            resource=resource,
            message="etcd encryption at rest not configured",
            recommendation="Configure encryption-provider-config for secret encryption",
        )

    # Check audit policy
    if "audit-policy-file" not in extra_args:
        report.add(
            severity="medium",
            category="Audit",
            resource=resource,
            message="Kubernetes audit policy not configured",
            recommendation="Configure audit-policy-file for API audit logging",
        )

    # Check RBAC
    auth_mode = extra_args.get("authorization-mode", "")
    if "RBAC" not in auth_mode:
        report.add(
            severity="high",
            category="Authorization",
            resource=resource,
            message="RBAC not explicitly enabled in authorization-mode",
            recommendation="Ensure authorization-mode includes RBAC",
        )

    # Check for anonymous auth
    if extra_args.get("anonymous-auth") == "true":
        report.add(
            severity="high",
            category="Authentication",
            resource=resource,
            message="Anonymous authentication is enabled",
            recommendation="Set anonymous-auth=false",
        )

    # Check kubelet HTTPS
    kubelet_args = cluster_config.get("kubeletConfiguration", {})
    if kubelet_args.get("serverTLSBootstrap") is not True:
        report.add(
            severity="low",
            category="TLS",
            resource=resource,
            message="Kubelet server TLS bootstrap not enabled",
            recommendation="Enable serverTLSBootstrap for automatic certificate management",
        )


def check_machine_security(
    machine: dict[str, Any],
    report: AuditReport,
) -> None:
    """Check Machine security settings."""
    name = machine.get("metadata", {}).get("name", "unknown")
    namespace = machine.get("metadata", {}).get("namespace", "default")
    resource = f"Machine/{namespace}/{name}"

    spec = machine.get("spec", {})

    # Check if bootstrap data is exposed
    bootstrap = spec.get("bootstrap", {})
    if "dataSecretName" not in bootstrap:
        report.add(
            severity="low",
            category="Secrets",
            resource=resource,
            message="Bootstrap data secret reference not found",
            recommendation="Ensure bootstrap data is stored in Secret",
        )


def check_network_security(
    cluster: dict[str, Any],
    report: AuditReport,
) -> None:
    """Check network security configuration."""
    name = cluster.get("metadata", {}).get("name", "unknown")
    namespace = cluster.get("metadata", {}).get("namespace", "default")
    resource = f"Cluster/{namespace}/{name}"

    spec = cluster.get("spec", {})
    network = spec.get("clusterNetwork", {})

    # Check for network policies mention
    # This is a general recommendation, actual enforcement depends on CNI
    if not network:
        report.add(
            severity="info",
            category="Network",
            resource=resource,
            message="No explicit clusterNetwork configuration",
            recommendation="Define clusterNetwork with appropriate CIDR ranges",
        )

    # Check for CNI configuration in topology
    topology = spec.get("topology", {})
    variables = topology.get("variables", [])

    cni_configured = any(
        var.get("name") in ["cni", "networkPlugin", "calico", "cilium"]
        for var in variables
    )

    if not cni_configured:
        report.add(
            severity="info",
            category="Network",
            resource=resource,
            message="CNI configuration not found in cluster variables",
            recommendation="Ensure CNI plugin is configured (calico, cilium, etc.)",
        )


def check_secret_exposure(
    secrets: list[dict[str, Any]],
    report: AuditReport,
) -> None:
    """Check for potentially exposed secrets."""
    for secret in secrets:
        name = secret.get("metadata", {}).get("name", "")
        namespace = secret.get("metadata", {}).get("namespace", "default")
        resource = f"Secret/{namespace}/{name}"

        secret_type = secret.get("type", "")

        # Check kubeconfig secrets
        if "kubeconfig" in name.lower():
            labels = secret.get("metadata", {}).get("labels", {})
            if not labels.get("cluster.x-k8s.io/cluster-name"):
                report.add(
                    severity="medium",
                    category="Secrets",
                    resource=resource,
                    message="Kubeconfig secret without cluster label (may be orphaned)",
                    recommendation="Verify secret ownership and clean up if orphaned",
                )


def check_replicas(
    cluster: dict[str, Any],
    report: AuditReport,
) -> None:
    """Check control plane and worker replica counts."""
    name = cluster.get("metadata", {}).get("name", "unknown")
    namespace = cluster.get("metadata", {}).get("namespace", "default")
    resource = f"Cluster/{namespace}/{name}"

    spec = cluster.get("spec", {})
    topology = spec.get("topology", {})

    # Control plane replicas
    cp = topology.get("controlPlane", {})
    cp_replicas = cp.get("replicas", 1)

    if cp_replicas < 3:
        report.add(
            severity="medium" if cp_replicas == 1 else "low",
            category="Availability",
            resource=resource,
            message=f"Control plane has {cp_replicas} replica(s) (recommend 3 for HA)",
            recommendation="Use 3 control plane replicas for production HA",
        )

    if cp_replicas % 2 == 0:
        report.add(
            severity="low",
            category="Availability",
            resource=resource,
            message=f"Control plane has even number of replicas ({cp_replicas})",
            recommendation="Use odd number of replicas for proper etcd quorum",
        )


def run_audit(
    cluster_name: str | None,
    namespace: str | None,
    all_namespaces: bool,
) -> list[AuditReport]:
    """Run security audit."""
    reports = []

    # Get clusters
    if cluster_name:
        clusters = run_kubectl_json(
            f"clusters.cluster.x-k8s.io/{cluster_name}",
            namespace=namespace,
        )
    else:
        clusters = run_kubectl_json(
            "clusters.cluster.x-k8s.io",
            namespace=namespace,
            all_namespaces=all_namespaces,
        )

    for cluster in clusters:
        cluster_name = cluster.get("metadata", {}).get("name", "unknown")
        cluster_ns = cluster.get("metadata", {}).get("namespace", "default")
        report = AuditReport(cluster_name=f"{cluster_ns}/{cluster_name}")

        # Run checks
        check_pss_configuration(cluster, report)
        check_network_security(cluster, report)
        check_replicas(cluster, report)

        # Get related resources for this cluster
        kcps = run_kubectl_json(
            "kubeadmcontrolplanes.controlplane.cluster.x-k8s.io",
            namespace=cluster_ns,
        )
        for kcp in kcps:
            owner_refs = kcp.get("metadata", {}).get("ownerReferences", [])
            if any(ref.get("name") == cluster_name for ref in owner_refs):
                check_kubeadm_security(kcp, report)

        machines = run_kubectl_json(
            "machines.cluster.x-k8s.io",
            namespace=cluster_ns,
        )
        for machine in machines:
            labels = machine.get("metadata", {}).get("labels", {})
            if labels.get("cluster.x-k8s.io/cluster-name") == cluster_name:
                check_machine_security(machine, report)

        # Check secrets
        secrets = run_kubectl_json("secrets", namespace=cluster_ns)
        cluster_secrets = [
            s
            for s in secrets
            if s.get("metadata", {}).get("labels", {}).get("cluster.x-k8s.io/cluster-name")
            == cluster_name
        ]
        check_secret_exposure(cluster_secrets, report)

        reports.append(report)

    return reports


def print_report(report: AuditReport) -> None:
    """Print audit report."""
    print(f"\n{'='*60}")
    print(f"Security Audit: {report.cluster_name}")
    print("=" * 60)

    if not report.findings:
        print("\n✓ No security findings!")
        return

    print(f"\nSummary: {report.high_count} high, {report.medium_count} medium, {report.low_count} low")

    # Group by severity
    for severity in ["high", "medium", "low", "info"]:
        findings = [f for f in report.findings if f.severity == severity]
        if not findings:
            continue

        icon = {"high": "🔴", "medium": "🟠", "low": "🟡", "info": "🔵"}.get(severity, "·")
        print(f"\n{icon} {severity.upper()} ({len(findings)})")
        print("-" * 40)

        for f in findings:
            print(f"\n  [{f.category}] {f.resource}")
            print(f"    {f.message}")
            if f.recommendation:
                print(f"    → {f.recommendation}")


def export_json(reports: list[AuditReport]) -> str:
    """Export reports to JSON."""
    output = []
    for report in reports:
        output.append(
            {
                "cluster": report.cluster_name,
                "summary": {
                    "high": report.high_count,
                    "medium": report.medium_count,
                    "low": report.low_count,
                },
                "findings": [
                    {
                        "severity": f.severity,
                        "category": f.category,
                        "resource": f.resource,
                        "message": f.message,
                        "recommendation": f.recommendation,
                    }
                    for f in report.findings
                ],
            }
        )
    return json.dumps(output, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit security posture of CAPI clusters",
    )
    parser.add_argument(
        "--cluster",
        "-c",
        default=None,
        help="Specific cluster to audit",
    )
    parser.add_argument(
        "--namespace",
        "-n",
        default=None,
        help="Namespace to audit",
    )
    parser.add_argument(
        "--all-namespaces",
        "-A",
        action="store_true",
        help="Audit all namespaces",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write JSON report to file",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    if not find_kubectl():
        print("Error: kubectl not found in PATH", file=sys.stderr)
        return 1

    print("Running security audit...")
    reports = run_audit(args.cluster, args.namespace, args.all_namespaces)

    if not reports:
        print("No clusters found to audit")
        return 0

    if args.format == "json" or args.output:
        json_output = export_json(reports)
        if args.output:
            with open(args.output, "w") as f:
                f.write(json_output)
            print(f"Report written to: {args.output}")
        else:
            print(json_output)
    else:
        for report in reports:
            print_report(report)

    # Return 1 if any high findings
    has_high = any(r.high_count > 0 for r in reports)
    return 1 if has_high else 0


if __name__ == "__main__":
    sys.exit(main())
