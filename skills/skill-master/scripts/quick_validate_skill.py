#!/usr/bin/env python3
"""Quick validation for SKILL.md per agentskills.io specification.

This is a lightweight validator intended for fast local checks.
It does NOT replace project-level checks.

Validates per https://agentskills.io/specification:
- SKILL.md exists
- YAML frontmatter exists with required fields (name, description)
- name: 1-64 chars, lowercase a-z0-9-, no --, no leading/trailing -
- name matches directory name
- description: 1-1024 chars, non-empty
- description must not contain angle brackets

Usage:
    python quick_validate_skill.py <skill-directory>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# agentskills.io spec: lowercase alphanumeric + hyphens, no consecutive hyphens
_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _extract_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("No YAML frontmatter found (expected starting '---')")

    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("Invalid YAML frontmatter (missing closing '---')")

    return text[4:end]


def validate_skill_dir(skill_dir: Path) -> None:
    skill_dir = skill_dir.resolve()

    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    if not skill_dir.is_dir():
        raise ValueError(f"Not a directory: {skill_dir}")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found: {skill_md}")

    content = skill_md.read_text(encoding="utf-8")
    frontmatter = _extract_frontmatter(content)

    name_match = re.search(r"^name:\s*(.+)\s*$", frontmatter, re.MULTILINE)
    if not name_match:
        raise ValueError("Missing 'name:' in YAML frontmatter")

    name = name_match.group(1).strip().strip('"').strip("'")

    # agentskills.io spec: 1-64 characters
    if len(name) < 1 or len(name) > 64:
        raise ValueError(f"name must be 1-64 characters (got {len(name)})")

    if not _NAME_RE.fullmatch(name):
        raise ValueError(
            "name must be lowercase a-z0-9 plus single hyphens (no --, no leading/trailing -)"
        )

    if name != skill_dir.name:
        raise ValueError(
            f"Frontmatter name '{name}' must match directory name '{skill_dir.name}'"
        )

    desc_match = re.search(r"^description:\s*(.+)\s*$", frontmatter, re.MULTILINE)
    if not desc_match:
        raise ValueError("Missing 'description:' in YAML frontmatter")

    description = desc_match.group(1).strip().strip('"').strip("'")

    # agentskills.io spec: 1-1024 characters
    if len(description) < 1:
        raise ValueError("description must not be empty")
    if len(description) > 1024:
        raise ValueError(f"description must be max 1024 characters (got {len(description)})")

    if "<" in description or ">" in description:
        raise ValueError("description must not contain angle brackets (< or >)")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(
            "Usage: python quick_validate_skill.py <skill-directory>",
            file=sys.stderr,
        )
        return 1

    try:
        validate_skill_dir(Path(argv[0]))
        print("✅ Skill is valid")
        return 0
    except Exception as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
