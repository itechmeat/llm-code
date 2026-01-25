"""Generate a Beads bulk-create Markdown file for `bd create -f`.

This helper is intentionally stored inside a Copilot skill folder so the
workflow is self-contained and discoverable by agents.

Upstream bd markdown parser format:
- Each issue starts with an H2 header: `## Title`
- Fields live under H3 sections: `### Description`, `### Design`,
  `### Acceptance Criteria`, etc.

See upstream implementation:
https://github.com/steveyegge/beads/blob/main/cmd/bd/markdown.go
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class IssueSpec:
    title: str
    priority: int
    issue_type: str
    description: str
    design: str
    acceptance_criteria: str
    labels: tuple[str, ...]
    dependencies: tuple[str, ...]


def _require_str(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _require_int(value: Any, *, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _require_str_list(value: Any, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    items = tuple(item.strip() for item in value if item.strip())
    return items


def _parse_issue(obj: Any) -> IssueSpec:
    if not isinstance(obj, dict):
        raise ValueError("Each issue must be an object")

    title = _require_str(obj.get("title"), field_name="title")
    priority = _require_int(obj.get("priority"), field_name="priority")
    if priority < 0 or priority > 4:
        raise ValueError("priority must be in range 0..4")

    issue_type = _require_str(obj.get("type"), field_name="type")
    description = _require_str(obj.get("description"), field_name="description")

    # Repo rule: keep Beads self-contained.
    design = _require_str(obj.get("design"), field_name="design")
    acceptance_criteria = _require_str(
        obj.get("acceptance_criteria"), field_name="acceptance_criteria"
    )

    labels = _require_str_list(obj.get("labels"), field_name="labels")
    dependencies = _require_str_list(obj.get("dependencies"), field_name="dependencies")

    return IssueSpec(
        title=title,
        priority=priority,
        issue_type=issue_type,
        description=description,
        design=design,
        acceptance_criteria=acceptance_criteria,
        labels=labels,
        dependencies=dependencies,
    )


def _render_section(name: str, content: str) -> str:
    content = content.strip("\n")
    if not content.strip():
        return ""
    return f"### {name}\n{content}\n\n"


def render_markdown(issues: Iterable[IssueSpec]) -> str:
    parts: list[str] = []

    for issue in issues:
        parts.append(f"## {issue.title}\n\n")
        parts.append(_render_section("Priority", str(issue.priority)))
        parts.append(_render_section("Type", issue.issue_type))
        parts.append(_render_section("Description", issue.description))
        parts.append(_render_section("Design", issue.design))
        parts.append(_render_section("Acceptance Criteria", issue.acceptance_criteria))

        if issue.labels:
            parts.append(_render_section("Labels", ", ".join(issue.labels)))
        if issue.dependencies:
            parts.append(_render_section("Dependencies", ", ".join(issue.dependencies)))

    return "".join(parts).rstrip() + "\n"


def _validate_out_path(path: str) -> str:
    if os.path.isdir(path):
        raise ValueError("--out must be a file path, not a directory")
    if not path.lower().endswith((".md", ".markdown")):
        raise ValueError("--out must end with .md or .markdown")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown file suitable for `bd create -f` from a JSON plan."
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        required=True,
        help='Path to JSON plan file with shape: {"issues": [ ... ]}',
    )
    parser.add_argument(
        "--out",
        dest="out_path",
        default=None,
        help="Write Markdown to this path. If omitted, a temporary file is created.",
    )
    parser.add_argument(
        "--print-path",
        action="store_true",
        help="Print only the output markdown path (for scripting).",
    )

    args = parser.parse_args()

    with open(args.in_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, dict) or "issues" not in raw:
        raise SystemExit("Input JSON must be an object with key 'issues'")

    raw_issues = raw.get("issues")
    if not isinstance(raw_issues, list):
        raise SystemExit("'issues' must be a list")

    issues = [_parse_issue(item) for item in raw_issues]
    markdown = render_markdown(issues)

    if args.out_path is None:
        fd, out_path = tempfile.mkstemp(prefix="bd-plan-", suffix=".md")
        os.close(fd)
    else:
        out_path = _validate_out_path(args.out_path)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    if args.print_path:
        print(out_path)
    else:
        print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
