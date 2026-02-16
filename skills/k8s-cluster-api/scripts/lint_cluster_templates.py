#!/usr/bin/env python3
"""Lint and validate Cluster API manifests.

Validates YAML manifests for Cluster API resources with checks for:
- Required fields (apiVersion, kind, metadata)
- Known deprecated fields and API versions
- Schema compliance for common CAPI types
- Best practice warnings

Usage:
    python lint_cluster_templates.py <file.yaml> [file2.yaml ...]
    python lint_cluster_templates.py --dir ./manifests/
    python lint_cluster_templates.py --assets  # Lint all asset templates

Examples:
    python lint_cluster_templates.py cluster.yaml
    python lint_cluster_templates.py --dir ./clusters/ --strict
    python lint_cluster_templates.py --assets --fix
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintIssue:
    severity: Severity
    message: str
    file: str
    line: int | None = None
    suggestion: str | None = None

    def __str__(self) -> str:
        loc = f"{self.file}"
        if self.line:
            loc += f":{self.line}"
        prefix = {
            Severity.ERROR: "ERROR",
            Severity.WARNING: "WARN ",
            Severity.INFO: "INFO ",
        }[self.severity]
        msg = f"[{prefix}] {loc}: {self.message}"
        if self.suggestion:
            msg += f"\n         Suggestion: {self.suggestion}"
        return msg


@dataclass
class LintResult:
    file: str
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)


# Known CAPI API versions
CAPI_API_VERSIONS = {
    "cluster.x-k8s.io/v1alpha3": {"deprecated": True, "replacement": "v1beta1"},
    "cluster.x-k8s.io/v1alpha4": {"deprecated": True, "replacement": "v1beta1"},
    "cluster.x-k8s.io/v1beta1": {"deprecated": False},
}

# Known CAPI kinds with required fields
CAPI_KINDS = {
    "Cluster": {
        "required_spec": ["infrastructureRef", "controlPlaneRef"],
        "optional_spec": ["clusterNetwork", "topology"],
    },
    "Machine": {
        "required_spec": ["clusterName", "bootstrap", "infrastructureRef"],
    },
    "MachineDeployment": {
        "required_spec": ["clusterName", "template"],
    },
    "MachineSet": {
        "required_spec": ["clusterName", "template"],
    },
    "ClusterClass": {
        "required_spec": ["infrastructure", "controlPlane"],
    },
    "MachineHealthCheck": {
        "required_spec": ["clusterName", "selector", "unhealthyConditions"],
    },
    "MachinePool": {
        "required_spec": ["clusterName", "template"],
    },
}

# Deprecated fields by kind
DEPRECATED_FIELDS = {
    "Cluster": {
        "spec.paused": {
            "since": "v1.4.0",
            "message": "Use spec.topology.controlPlane/workers for managed clusters",
        },
    },
    "Machine": {
        "spec.version": {
            "since": "v1.5.0",
            "message": "Version is now inherited from control plane or topology",
        },
    },
}

# Best practice checks
BEST_PRACTICES = {
    "no_hardcoded_credentials": {
        "patterns": [
            r"password:\s*['\"]?[^${\s]+['\"]?",
            r"secret:\s*['\"]?[^${\s]+['\"]?",
            r"token:\s*['\"]?[a-zA-Z0-9+/=]{20,}['\"]?",
        ],
        "message": "Possible hardcoded credential detected",
        "severity": Severity.WARNING,
    },
    "namespace_specified": {
        "check": lambda doc: doc.get("metadata", {}).get("namespace") is not None,
        "message": "No namespace specified - will use default",
        "severity": Severity.INFO,
    },
}


def parse_yaml_documents(content: str) -> list[tuple[dict[str, Any], int]]:
    """Parse YAML content into documents with line numbers."""
    if not HAS_YAML:
        # Fallback: basic parsing without yaml
        docs = []
        current_doc = {}
        current_line = 1

        for i, line in enumerate(content.split("\n"), 1):
            if line.strip() == "---":
                if current_doc:
                    docs.append((current_doc, current_line))
                current_doc = {}
                current_line = i + 1
            elif line.strip() and not line.strip().startswith("#"):
                # Very basic key-value parsing
                if ":" in line:
                    key = line.split(":")[0].strip()
                    value = ":".join(line.split(":")[1:]).strip()
                    if key and not key.startswith("-"):
                        current_doc[key] = value

        if current_doc:
            docs.append((current_doc, current_line))

        return docs

    # Use yaml library
    docs = []
    lines = content.split("\n")
    doc_start_lines = [0]

    for i, line in enumerate(lines):
        if line.strip() == "---":
            doc_start_lines.append(i + 1)

    try:
        parsed = list(yaml.safe_load_all(content))
        for i, doc in enumerate(parsed):
            if doc is not None:
                line_num = doc_start_lines[i] + 1 if i < len(doc_start_lines) else 1
                docs.append((doc, line_num))
    except yaml.YAMLError:
        pass

    return docs


def lint_document(
    doc: dict[str, Any], file_path: str, start_line: int = 1
) -> list[LintIssue]:
    """Lint a single YAML document."""
    issues = []

    # Check required top-level fields
    if "apiVersion" not in doc:
        issues.append(
            LintIssue(
                severity=Severity.ERROR,
                message="Missing required field: apiVersion",
                file=file_path,
                line=start_line,
            )
        )

    if "kind" not in doc:
        issues.append(
            LintIssue(
                severity=Severity.ERROR,
                message="Missing required field: kind",
                file=file_path,
                line=start_line,
            )
        )

    if "metadata" not in doc:
        issues.append(
            LintIssue(
                severity=Severity.ERROR,
                message="Missing required field: metadata",
                file=file_path,
                line=start_line,
            )
        )
    elif "name" not in doc.get("metadata", {}):
        issues.append(
            LintIssue(
                severity=Severity.ERROR,
                message="Missing required field: metadata.name",
                file=file_path,
                line=start_line,
            )
        )

    # Check API version
    api_version = doc.get("apiVersion", "")
    if api_version in CAPI_API_VERSIONS:
        version_info = CAPI_API_VERSIONS[api_version]
        if version_info.get("deprecated"):
            replacement = version_info.get("replacement", "v1beta1")
            issues.append(
                LintIssue(
                    severity=Severity.WARNING,
                    message=f"Deprecated API version: {api_version}",
                    file=file_path,
                    line=start_line,
                    suggestion=f"Use cluster.x-k8s.io/{replacement}",
                )
            )

    # Check kind-specific requirements
    kind = doc.get("kind", "")
    if kind in CAPI_KINDS:
        kind_info = CAPI_KINDS[kind]
        spec = doc.get("spec", {})

        for required_field in kind_info.get("required_spec", []):
            # For topology-based clusters, some fields are optional
            if kind == "Cluster" and "topology" in spec:
                if required_field in ["infrastructureRef", "controlPlaneRef"]:
                    continue

            if required_field not in spec:
                issues.append(
                    LintIssue(
                        severity=Severity.ERROR,
                        message=f"Missing required spec field for {kind}: {required_field}",
                        file=file_path,
                        line=start_line,
                    )
                )

    # Check deprecated fields
    if kind in DEPRECATED_FIELDS:
        for field_path, deprecation_info in DEPRECATED_FIELDS[kind].items():
            # Navigate to field
            parts = field_path.split(".")
            current = doc
            found = True
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    found = False
                    break

            if found:
                issues.append(
                    LintIssue(
                        severity=Severity.WARNING,
                        message=f"Deprecated field '{field_path}' (since {deprecation_info['since']})",
                        file=file_path,
                        line=start_line,
                        suggestion=deprecation_info.get("message"),
                    )
                )

    return issues


def lint_content(content: str, file_path: str) -> LintResult:
    """Lint YAML content."""
    result = LintResult(file=file_path)

    # Check for YAML syntax errors
    if HAS_YAML:
        try:
            list(yaml.safe_load_all(content))
        except yaml.YAMLError as e:
            result.issues.append(
                LintIssue(
                    severity=Severity.ERROR,
                    message=f"YAML syntax error: {e}",
                    file=file_path,
                )
            )
            return result

    # Best practice checks on raw content
    for check_name, check_info in BEST_PRACTICES.items():
        if "patterns" in check_info:
            for pattern in check_info["patterns"]:
                for i, line in enumerate(content.split("\n"), 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        result.issues.append(
                            LintIssue(
                                severity=check_info["severity"],
                                message=check_info["message"],
                                file=file_path,
                                line=i,
                            )
                        )

    # Parse and lint each document
    docs = parse_yaml_documents(content)

    for doc, start_line in docs:
        if doc:
            # Document-level best practice checks
            for check_name, check_info in BEST_PRACTICES.items():
                if "check" in check_info:
                    if not check_info["check"](doc):
                        result.issues.append(
                            LintIssue(
                                severity=check_info["severity"],
                                message=check_info["message"],
                                file=file_path,
                                line=start_line,
                            )
                        )

            result.issues.extend(lint_document(doc, file_path, start_line))

    return result


def lint_file(file_path: str) -> LintResult:
    """Lint a single file."""
    try:
        content = Path(file_path).read_text()
        return lint_content(content, file_path)
    except FileNotFoundError:
        result = LintResult(file=file_path)
        result.issues.append(
            LintIssue(
                severity=Severity.ERROR,
                message="File not found",
                file=file_path,
            )
        )
        return result
    except PermissionError:
        result = LintResult(file=file_path)
        result.issues.append(
            LintIssue(
                severity=Severity.ERROR,
                message="Permission denied",
                file=file_path,
            )
        )
        return result


def get_assets_dir() -> Path:
    """Get path to assets directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "assets"


def lint_assets() -> list[LintResult]:
    """Lint all asset templates."""
    results = []
    assets_dir = get_assets_dir()

    if not assets_dir.exists():
        return results

    for yaml_file in assets_dir.glob("*.yaml"):
        results.append(lint_file(str(yaml_file)))

    return results


def print_results(results: list[LintResult], verbose: bool = False) -> tuple[int, int]:
    """Print lint results and return error/warning counts."""
    total_errors = 0
    total_warnings = 0

    for result in results:
        errors = sum(1 for i in result.issues if i.severity == Severity.ERROR)
        warnings = sum(1 for i in result.issues if i.severity == Severity.WARNING)
        total_errors += errors
        total_warnings += warnings

        if result.issues or verbose:
            if not result.issues:
                print(f"✓ {result.file}")
            else:
                for issue in result.issues:
                    print(str(issue))

    return total_errors, total_warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lint Cluster API manifests",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="YAML files to lint",
    )
    parser.add_argument(
        "--dir",
        "-d",
        help="Directory to lint (*.yaml files)",
    )
    parser.add_argument(
        "--assets",
        action="store_true",
        help="Lint all asset templates",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show passed files",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    args = parser.parse_args()

    if not args.files and not args.dir and not args.assets:
        parser.print_help()
        return 1

    results = []

    # Lint assets
    if args.assets:
        results.extend(lint_assets())

    # Lint directory
    if args.dir:
        dir_path = Path(args.dir)
        if dir_path.exists():
            for yaml_file in dir_path.glob("**/*.yaml"):
                results.append(lint_file(str(yaml_file)))
        else:
            print(f"Directory not found: {args.dir}", file=sys.stderr)
            return 1

    # Lint individual files
    for file_path in args.files:
        # Support glob patterns
        if "*" in file_path:
            for expanded in glob.glob(file_path, recursive=True):
                results.append(lint_file(expanded))
        else:
            results.append(lint_file(file_path))

    if not results:
        print("No files to lint", file=sys.stderr)
        return 1

    # Output
    if args.format == "json":
        import json

        output = []
        for result in results:
            output.append(
                {
                    "file": result.file,
                    "issues": [
                        {
                            "severity": i.severity.value,
                            "message": i.message,
                            "line": i.line,
                            "suggestion": i.suggestion,
                        }
                        for i in result.issues
                    ],
                }
            )
        print(json.dumps(output, indent=2))
    else:
        errors, warnings = print_results(results, args.verbose)

        # Summary
        total_files = len(results)
        passed = sum(1 for r in results if not r.has_errors)
        print(f"\n{passed}/{total_files} files passed")

        if errors:
            print(f"{errors} error(s)")
        if warnings:
            print(f"{warnings} warning(s)")

    # Exit code
    has_errors = any(r.has_errors for r in results)
    has_warnings = any(r.has_warnings for r in results)

    if has_errors:
        return 1
    if args.strict and has_warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
