#!/usr/bin/env python3
"""Package a skill directory into a zip archive.

This is intended for sharing skills outside the repo.

Behavior:
- Validates the skill directory using quick_validate_skill.py
- Creates a zip in the specified output directory (default: ./dist)
- Zip root contains the skill folder itself (e.g., skill-master/SKILL.md ...)

Usage:
    python package_skill.py <skill-directory> [--out dist]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
import zipfile
from pathlib import Path

try:
    from quick_validate_skill import validate_skill_dir
except ModuleNotFoundError:
    _SCRIPT_DIR = Path(__file__).resolve().parent
    sys.path.insert(0, _SCRIPT_DIR.as_posix())
    from quick_validate_skill import validate_skill_dir


def _iter_files(skill_dir: Path) -> list[Path]:
    skill_dir_resolved = skill_dir.resolve()
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if path.is_dir():
            continue
        if path.is_symlink():
            continue
        if path.name == ".DS_Store":
            continue

        resolved = path.resolve()
        try:
            resolved.relative_to(skill_dir_resolved)
        except ValueError:
            continue

        files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--out", dest="out_dir", type=Path, default=Path("dist"))
    args = parser.parse_args()

    skill_dir = args.skill_dir.resolve()
    validate_skill_dir(skill_dir)

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    zip_path = out_dir / f"{skill_dir.name}.zip"
    if zip_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing archive: {zip_path}. "
            "Delete it or choose a different --out directory."
        )

    files = _iter_files(skill_dir)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            arcname = Path(skill_dir.name) / file_path.relative_to(skill_dir)
            zf.write(file_path, arcname.as_posix())

    print(f"✅ Packaged: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
