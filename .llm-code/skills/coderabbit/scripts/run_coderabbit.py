#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_coderabbit(output_path: Path, timeout_seconds: int) -> int:
    coderabbit_path = shutil.which("coderabbit")
    if not coderabbit_path:
        raise RuntimeError("coderabbit CLI not found in PATH")

    process = subprocess.Popen(
        [coderabbit_path, "--prompt-only", "--type", "uncommitted"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        stdout, _ = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, _ = process.communicate()
        output_path.write_text(stdout or "", encoding="utf-8")
        raise RuntimeError(f"coderabbit timed out after {timeout_seconds}s")

    output_path.write_text(stdout or "", encoding="utf-8")
    return process.returncode


def resolve_repo_root(start_path: Path) -> Path:
    for parent in [start_path, *start_path.parents]:
        if (parent / ".project").exists() or (parent / ".git").exists():
            return parent
    raise RuntimeError("Unable to locate repo root (missing .project or .git)")


def ensure_code_review_dir(repo_root: Path) -> Path:
    code_review_dir = repo_root / ".code-review"
    code_review_dir.mkdir(parents=True, exist_ok=True)
    gitignore_path = code_review_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("*", encoding="utf-8")
    return code_review_dir


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run CodeRabbit in prompt-only mode and save output to a file.",
    )
    parser.add_argument(
        "--output",
        default="coderabbit-report.txt",
        help="Output file name (default: coderabbit-report.txt)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Timeout in seconds (default: 1800)",
    )
    args = parser.parse_args()

    repo_root = resolve_repo_root(Path(__file__).resolve())
    code_review_dir = ensure_code_review_dir(repo_root)
    output_name = Path(args.output).name
    output_path = (code_review_dir / output_name).resolve()
    exit_code = run_coderabbit(output_path, args.timeout)

    if exit_code != 0:
        raise RuntimeError(f"coderabbit exited with status {exit_code}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        sys.exit(1)
