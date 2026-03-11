#!/usr/bin/env python3
"""Compatibility wrapper for the legacy quick validation interface.

Usage:
    python quick_validate.py <skill-directory>
"""

from __future__ import annotations

import sys
from pathlib import Path

from quick_validate_skill import validate_skill_dir


def validate_skill(skill_path: str) -> tuple[bool, str]:
    try:
        validate_skill_dir(Path(skill_path))
        return True, "Skill is valid!"
    except Exception as exc:
        return False, str(exc)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("Usage: python quick_validate.py <skill-directory>", file=sys.stderr)
        return 1

    valid, message = validate_skill(argv[0])
    stream = sys.stdout if valid else sys.stderr
    print(message, file=stream)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
