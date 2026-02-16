#!/usr/bin/env python3
"""Run clusterctl describe and save diagnostic report.

This script wraps clusterctl describe to generate diagnostic reports
for Cluster API clusters.

Usage:
    python run_clusterctl_diagnose.py <cluster-name>
    python run_clusterctl_diagnose.py <cluster-name> -n <namespace>

Examples:
    python run_clusterctl_diagnose.py my-cluster
    python run_clusterctl_diagnose.py my-cluster -n clusters --output report.txt
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def find_clusterctl() -> str | None:
    """Find clusterctl binary in PATH."""
    return shutil.which("clusterctl")


def resolve_repo_root(start_path: Path) -> Path:
    """Find repository root by looking for .git or .project."""
    for parent in [start_path, *start_path.parents]:
        if (parent / ".git").exists() or (parent / ".project").exists():
            return parent
    raise RuntimeError("Unable to locate repo root (missing .git or .project)")


def ensure_output_dir(repo_root: Path) -> Path:
    """Ensure .cluster-diagnostics directory exists."""
    diag_dir = repo_root / ".cluster-diagnostics"
    diag_dir.mkdir(parents=True, exist_ok=True)

    gitignore = diag_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")

    return diag_dir


def run_clusterctl_describe(
    cluster_name: str,
    namespace: str | None,
    kubeconfig: str | None,
    timeout: int,
) -> tuple[str, int]:
    """Run clusterctl describe cluster command."""
    clusterctl = find_clusterctl()
    if not clusterctl:
        raise RuntimeError(
            "clusterctl not found in PATH. Install from: "
            "https://cluster-api.sigs.k8s.io/user/quick-start#install-clusterctl"
        )

    cmd = [clusterctl, "describe", "cluster", cluster_name]

    if namespace:
        cmd.extend(["--namespace", namespace])
    if kubeconfig:
        cmd.extend(["--kubeconfig", kubeconfig])

    # Add show-conditions for detailed output
    cmd.append("--show-conditions=all")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n\nSTDERR:\n{result.stderr}"
        return output, result.returncode
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"clusterctl timed out after {timeout}s")
    except FileNotFoundError:
        raise RuntimeError(f"clusterctl not found: {clusterctl}")


def run_additional_diagnostics(
    cluster_name: str,
    namespace: str | None,
    kubeconfig: str | None,
) -> str:
    """Run additional diagnostic commands."""
    clusterctl = find_clusterctl()
    if not clusterctl:
        return ""

    sections = []

    # Get cluster topology if using ClusterClass
    cmd_topology = [clusterctl, "describe", "cluster", cluster_name, "--show-topology"]
    if namespace:
        cmd_topology.extend(["--namespace", namespace])
    if kubeconfig:
        cmd_topology.extend(["--kubeconfig", kubeconfig])

    try:
        result = subprocess.run(cmd_topology, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            sections.append("=== CLUSTER TOPOLOGY ===\n" + result.stdout)
    except (subprocess.TimeoutExpired, Exception):
        pass

    # Get cluster move dry-run to check for issues
    cmd_move = [
        clusterctl,
        "move",
        "--dry-run",
        "-v",
        "0",
        "--filter-cluster",
        cluster_name,
    ]
    if namespace:
        cmd_move.extend(["--namespace", namespace])
    if kubeconfig:
        cmd_move.extend(["--kubeconfig", kubeconfig])

    try:
        result = subprocess.run(cmd_move, capture_output=True, text=True, timeout=60)
        if result.stdout.strip():
            sections.append("=== MOVE DRY-RUN (objects) ===\n" + result.stdout)
    except (subprocess.TimeoutExpired, Exception):
        pass

    return "\n\n".join(sections)


def generate_report(
    cluster_name: str,
    namespace: str | None,
    describe_output: str,
    additional_output: str,
) -> str:
    """Generate full diagnostic report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = [
        "=" * 60,
        "CLUSTER API DIAGNOSTIC REPORT",
        "=" * 60,
        f"Cluster: {cluster_name}",
        f"Namespace: {namespace or 'default'}",
        f"Generated: {timestamp}",
        "=" * 60,
        "",
        "=== CLUSTER DESCRIPTION ===",
        describe_output,
    ]

    if additional_output:
        report.extend(["", additional_output])

    report.extend(
        [
            "",
            "=" * 60,
            "END OF REPORT",
            "=" * 60,
        ]
    )

    return "\n".join(report)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run clusterctl describe and save diagnostic report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "cluster_name",
        help="Name of the cluster to diagnose",
    )
    parser.add_argument(
        "--namespace",
        "-n",
        default=None,
        help="Namespace of the cluster (default: current context namespace)",
    )
    parser.add_argument(
        "--kubeconfig",
        "-k",
        default=None,
        help="Path to kubeconfig file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output filename (default: <cluster>-diagnostic.txt)",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=120,
        help="Timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--skip-additional",
        action="store_true",
        help="Skip additional diagnostics (topology, move dry-run)",
    )
    args = parser.parse_args()

    try:
        # Run main describe command
        print(f"Running clusterctl describe for cluster '{args.cluster_name}'...")
        describe_output, exit_code = run_clusterctl_describe(
            args.cluster_name,
            args.namespace,
            args.kubeconfig,
            args.timeout,
        )

        # Run additional diagnostics
        additional_output = ""
        if not args.skip_additional:
            print("Running additional diagnostics...")
            additional_output = run_additional_diagnostics(
                args.cluster_name,
                args.namespace,
                args.kubeconfig,
            )

        # Generate report
        report = generate_report(
            args.cluster_name,
            args.namespace,
            describe_output,
            additional_output,
        )

        # Save to file
        repo_root = resolve_repo_root(Path(__file__).resolve())
        output_dir = ensure_output_dir(repo_root)

        output_name = args.output or f"{args.cluster_name}-diagnostic.txt"
        output_path = output_dir / output_name
        output_path.write_text(report, encoding="utf-8")

        print(f"\n✅ Diagnostic report saved to: {output_path}")

        if exit_code != 0:
            print(f"⚠️  clusterctl exited with code {exit_code}", file=sys.stderr)

        return exit_code

    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
