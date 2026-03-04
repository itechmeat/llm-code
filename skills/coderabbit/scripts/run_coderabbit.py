#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def detect_base_branch() -> str:
    """Auto-detect the base branch (main, master, or current)."""
    for branch in ("main", "master"):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", branch],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return branch
    # fallback: use current branch
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() or "main"


def check_prerequisites() -> list[str]:
    """Check all prerequisites and return list of errors."""
    errors = []

    # 1. CLI installed?
    if not shutil.which("coderabbit"):
        errors.append(
            "coderabbit CLI not found in PATH. "
            "Install: curl -fsSL https://cli.coderabbit.ai/install.sh | sh"
        )

    # 2. Inside a git repo?
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        errors.append("Not inside a git repository.")
        return errors  # no point checking further

    # 3. At least one commit? (CRITICAL — CLI crashes with GitError otherwise)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        errors.append(
            "Repository has no commits. "
            "CodeRabbit CLI requires at least one commit to compute diffs. "
            "Create an initial commit first."
        )

    return errors


def run_coderabbit(output_path: Path, timeout_seconds: int, base_branch: str) -> int:
    coderabbit_path = shutil.which("coderabbit")
    if not coderabbit_path:
        raise RuntimeError("coderabbit CLI not found in PATH")

    cmd = [
        coderabbit_path, "review",
        "--prompt-only", "--type", "uncommitted",
        "--base", base_branch, "--no-color",
    ]

    print(f"Running: {' '.join(cmd)}", file=sys.stderr)
    print(f"Base branch: {base_branch}", file=sys.stderr)
    print(f"Output: {output_path}", file=sys.stderr)
    print(f"Timeout: {timeout_seconds}s", file=sys.stderr)

    process = subprocess.Popen(
        cmd,
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

    if process.returncode != 0:
        # Check for common errors in output
        if stdout and "GitError" in stdout:
            raise RuntimeError(
                f"coderabbit GitError — check that base branch '{base_branch}' exists "
                "and repo has commits."
            )
        if stdout and "[error] stopping cli" in stdout:
            raise RuntimeError(
                f"coderabbit failed with '[error] stopping cli'. "
                f"Run 'DEBUG=* coderabbit review --prompt-only --type uncommitted "
                f"--base {base_branch}' for details. "
                f"Check ~/.coderabbit/logs/ for the full log."
            )

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
    parser.add_argument(
        "--base",
        default=None,
        help="Base branch for comparison (default: auto-detect main/master)",
    )
    args = parser.parse_args()

    # Check prerequisites
    errors = check_prerequisites()
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    # Detect base branch
    base_branch = args.base or detect_base_branch()

    # Verify base branch exists
    result = subprocess.run(
        ["git", "rev-parse", "--verify", base_branch],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(
            f"ERROR: Base branch '{base_branch}' not found. "
            f"Use --base <branch> to specify a valid branch.",
            file=sys.stderr,
        )
        return 1

    repo_root = resolve_repo_root(Path.cwd())
    code_review_dir = ensure_code_review_dir(repo_root)
    output_name = Path(args.output).name
    output_path = (code_review_dir / output_name).resolve()
    exit_code = run_coderabbit(output_path, args.timeout, base_branch)

    if exit_code != 0:
        raise RuntimeError(f"coderabbit exited with status {exit_code}")

    print(f"Review saved to: {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        sys.exit(1)
