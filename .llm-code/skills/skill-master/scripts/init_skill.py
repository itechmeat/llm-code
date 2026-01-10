#!/usr/bin/env python3
"""Initialize Agent Skill per agentskills.io specification.

This script scaffolds a new Agent Skill that works with any skills-compatible
agent (Claude, GitHub Copilot, Cursor, etc.).

Usage:
    python init_skill.py <skill-name> [--skills-dir <path>]

Examples:
    python init_skill.py pdf-processing
    python init_skill.py pdf-processing --skills-dir .llm-code/skills
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# agentskills.io spec: lowercase alphanumeric + hyphens, no consecutive hyphens
_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def _find_repo_root(start: Path) -> Path:
    """Walk up until we find a .git directory or reach filesystem root."""
    current = start.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    # Fallback: 4 levels up from script location
    return _script_dir().parents[3]


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_file_if_missing(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"File already exists: {path}")
    _ensure_parent_dir(path)
    path.write_text(content, encoding="utf-8")


def _mkdir_if_missing(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Path already exists: {path}")
    path.mkdir(parents=True, exist_ok=False)


def _title_from_kebab(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def _validate_skill_name(name: str) -> None:
    """Validate skill name per agentskills.io specification."""
    if len(name) < 1 or len(name) > 64:
        raise ValueError("skill-name must be 1-64 characters")
    if not _SKILL_NAME_RE.fullmatch(name):
        raise ValueError(
            "skill-name must be lowercase a-z0-9 plus single hyphens "
            "(no --, no leading/trailing -)"
        )


def init_skill(skill_name: str, skills_root: Path) -> Path:
    """Create a new Agent Skill following agentskills.io specification.

    Args:
        skill_name: Skill identifier (lowercase, hyphens allowed)
        skills_root: Directory where skills are stored

    Returns:
        Path to created skill directory
    """
    _validate_skill_name(skill_name)

    skill_dir = skills_root / skill_name
    _mkdir_if_missing(skill_dir)

    skill_md = skill_dir / "SKILL.md"
    title = _title_from_kebab(skill_name)

    # Template follows agentskills.io specification
    # https://agentskills.io/specification
    content = (
        "---\n"
        f"name: {skill_name}\n"
        "description: \"[TODO] Describe what this skill does and when to use it. Include discovery keywords.\"\n"
        "---\n\n"
        f"# {title}\n\n"
        "## When to Use\n\n"
        "- [TODO] Situations and triggers\n\n"
        "## Quick Navigation\n\n"
        "- Topic A: `references/topic-a.md`\n\n"
        "## Steps / Recipes\n\n"
        "1. [TODO]\n\n"
        "## Critical Prohibitions\n\n"
        "- [TODO]\n\n"
        "## Links\n\n"
        "- [TODO] External references\n"
    )

    _write_file_if_missing(skill_md, content)

    # Create references directory per agentskills.io progressive disclosure pattern
    (skill_dir / "references").mkdir(exist_ok=True)

    # Create README.md for human readers
    readme_content = (
        f"# {title}\n\n"
        "[TODO] Brief description for human readers.\n\n"
        "## Quick Navigation\n\n"
        "- [SKILL.md](SKILL.md) — Entry point for agents\n"
        "- [references/](references/) — Detailed documentation\n"
    )
    readme_path = skill_dir / "README.md"
    if not readme_path.exists():
        readme_path.write_text(readme_content, encoding="utf-8")

    return skill_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="init_skill.py",
        description="Initialize Agent Skill per agentskills.io specification",
    )
    parser.add_argument(
        "skill_name",
        help="Skill identifier (lowercase, a-z0-9 and hyphens only)",
    )
    parser.add_argument(
        "--skills-dir",
        dest="skills_dir",
        default=None,
        help="Directory for skills (default: current directory)",
    )

    args = parser.parse_args(argv)

    # Determine skills directory
    if args.skills_dir:
        skills_root = Path(args.skills_dir)
        if not skills_root.is_absolute():
            skills_root = Path.cwd() / args.skills_dir
    else:
        # Default: current working directory
        skills_root = Path.cwd()

    try:
        created = init_skill(args.skill_name, skills_root)
        print(f"✅ Created skill: {created}")
        return 0
    except Exception as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
