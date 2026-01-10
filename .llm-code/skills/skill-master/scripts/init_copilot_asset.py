#!/usr/bin/env python3
"""Initialize GitHub Copilot-specific assets.

This script scaffolds Copilot-specific assets:
- Instruction: <instructions-dir>/<topic>.instructions.md (with applyTo)
- Agent: <agents-dir>/<role>.agent.md

For universal Agent Skills (agentskills.io), use init_skill.py instead.

Usage:
    python init_copilot_asset.py instruction <topic> --apply-to '<glob>' [--instructions-dir <path>]
    python init_copilot_asset.py agent <role> [--agents-dir <path>]

Examples:
    python init_copilot_asset.py instruction db-rls --apply-to 'src/**/*.py'
    python init_copilot_asset.py agent backend --agents-dir .github/agents
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_INSTRUCTION_TOPIC_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_AGENT_ROLE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _find_repo_root(start: Path) -> Path:
    """Walk up until we find a .git directory or reach filesystem root."""
    current = start.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


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


def _validate_instruction_topic(topic: str) -> None:
    if len(topic) < 1 or len(topic) > 64:
        raise ValueError("topic must be 1..64 characters")
    if not _INSTRUCTION_TOPIC_RE.fullmatch(topic):
        raise ValueError("topic must be lower-kebab-case: a-z0-9 plus single hyphens")


def _validate_agent_role(role: str) -> None:
    if len(role) < 1 or len(role) > 64:
        raise ValueError("role must be 1..64 characters")
    if not _AGENT_ROLE_RE.fullmatch(role):
        raise ValueError("role must be lower-kebab-case: a-z0-9 plus single hyphens")


def init_instruction(instructions_root: Path, topic: str, apply_to: str) -> Path:
    _validate_instruction_topic(topic)

    if not apply_to:
        raise ValueError("--apply-to is required")

    instruction_path = instructions_root / f"{topic}.instructions.md"

    content = (
        "---\n"
        "description: \"[TODO] Briefly describe the norms/standards enforced for files matched by applyTo.\"\n"
        f"applyTo: \"{apply_to}\"\n"
        "---\n\n"
        f"# {_title_from_kebab(topic)}\n\n"
        "## MUST\n\n"
        "- [TODO]\n\n"
        "## MUST NOT\n\n"
        "- [TODO]\n\n"
        "## Examples\n\n"
        "[TODO]\n"
    )

    _write_file_if_missing(instruction_path, content)
    return instruction_path


def init_agent(agents_root: Path, role: str) -> Path:
    _validate_agent_role(role)

    agent_path = agents_root / f"{role}.agent.md"

    content = (
        "---\n"
        f"description: \"[TODO] When to choose the {role} agent and what it is responsible for.\"\n"
        "---\n\n"
        f"# {_title_from_kebab(role)} Agent\n\n"
        "## When to use\n\n"
        "- [TODO]\n\n"
        "## What it does\n\n"
        "- [TODO]\n\n"
        "## Hard prohibitions\n\n"
        "- [TODO]\n\n"
        "## Links\n\n"
        "- [TODO] Link to relevant skills\n"
    )

    _write_file_if_missing(agent_path, content)
    return agent_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="init_copilot_asset.py",
        description="Initialize Copilot-specific assets (instructions, agents)",
    )
    subparsers = parser.add_subparsers(dest="kind", required=True)

    instr_p = subparsers.add_parser("instruction", help="Scaffold a new instruction")
    instr_p.add_argument("topic", help="lower-kebab-case")
    instr_p.add_argument("--apply-to", required=True, dest="apply_to", help="Glob for applyTo")
    instr_p.add_argument(
        "--instructions-dir",
        dest="instructions_dir",
        default=None,
        help="Directory for instructions (default: .github/instructions from repo root)",
    )

    agent_p = subparsers.add_parser("agent", help="Scaffold a new agent")
    agent_p.add_argument("role", help="lower-kebab-case")
    agent_p.add_argument(
        "--agents-dir",
        dest="agents_dir",
        default=None,
        help="Directory for agents (default: .github/agents from repo root)",
    )

    args = parser.parse_args(argv)

    try:
        if args.kind == "instruction":
            if args.instructions_dir:
                instructions_root = Path(args.instructions_dir)
                if not instructions_root.is_absolute():
                    instructions_root = Path.cwd() / args.instructions_dir
            else:
                repo_root = _find_repo_root(Path.cwd())
                instructions_root = repo_root / ".github" / "instructions"

            created = init_instruction(instructions_root, args.topic, args.apply_to)
            print(f"✅ Created instruction: {created}")
            return 0

        if args.kind == "agent":
            if args.agents_dir:
                agents_root = Path(args.agents_dir)
                if not agents_root.is_absolute():
                    agents_root = Path.cwd() / args.agents_dir
            else:
                repo_root = _find_repo_root(Path.cwd())
                agents_root = repo_root / ".github" / "agents"

            created = init_agent(agents_root, args.role)
            print(f"✅ Created agent: {created}")
            return 0

        raise RuntimeError(f"Unknown kind: {args.kind}")
    except Exception as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
