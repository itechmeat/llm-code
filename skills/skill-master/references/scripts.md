# Scripts in Skills

## When to Write Scripts

Scripts make sense when:
- An operation must be **deterministic** — critical validations, health checks, data extraction
- A **CLI tool needs to be wrapped** with proper argument handling, timeouts, and output capture
- A task would take many tool calls to do manually but is trivial in code
- The workflow involves **multiple steps that depend on each other** (fetch → transform → write)
- You need **reusable utilities** the agent can call repeatedly across a session

Don't write a script just to wrap one command. A bare `kubectl get` in instructions is fine. A script earns its place when it adds real logic.

## Language Choice

**Python (default)** — use unless there's a reason not to:
- Universal availability, no compilation, easy to read by agents and humans
- Best for: CLI wrappers, data processing, validation, scaffolding

**Go** — use when the skill's ecosystem is Go or Kubernetes-native:
- k8s-cluster-api is the canonical example: all scripts are Go programs sharing an `internal/` package with `go.mod` in `scripts/`
- Best for: tools that call `kubectl`, interact with cloud APIs, process YAML manifests

**JavaScript/TypeScript** — use when the skill is npm/Node-centric:
- Best for: skills around frontend tooling, Node APIs, or when the user's project is already JS

**Bash** — only for simple orchestration (a few commands chained); avoid for anything with logic

## Python Script Conventions

Based on the coderabbit and skill-master patterns:

```python
#!/usr/bin/env python3
"""Short description of what this script does.

Usage:
    python scripts/my-script.py [--option value]

Examples:
    python scripts/my-script.py --input data.csv
    python scripts/my-script.py --output report.txt --verbose
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", default="output.txt", help="Output file")
    args = parser.parse_args()

    # Check tool availability before doing anything
    tool_path = shutil.which("required-tool")
    if not tool_path:
        raise RuntimeError("required-tool not found in PATH. Install with: ...")

    # Do the work...

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        sys.exit(1)
```

Key conventions:
- `#!/usr/bin/env python3` shebang
- Docstring at top with Usage and Examples — agents read this
- `argparse` for all arguments (no hardcoded values)
- `shutil.which()` to check tool availability before use
- `subprocess` for CLI invocations, capture both stdout and stderr
- All exceptions caught at `main()` level, print to stderr, `sys.exit(1)`
- `Path` for all file operations (not string concatenation)

## Go Script Conventions

Based on the k8s-cluster-api pattern:

```
scripts/
├── go.mod                    # module: <skill-name>-tools
├── go.sum
├── internal/
│   └── kubectl/
│       └── kubectl.go        # shared utilities
├── check-cluster-health/
│   └── main.go
└── validate-manifests/
    └── main.go
```

Each script is its own directory with `main.go`. A usage comment at the top:

```go
// check-cluster-health analyzes CAPI conditions and reports cluster health.
//
// Usage:
//
//	go run ./check-cluster-health <cluster-name> [flags]
//
// Examples:
//
//	go run ./check-cluster-health my-cluster
//	go run ./check-cluster-health my-cluster --json
package main
```

Invoked with: `go run ./scripts/check-cluster-health <args>`

Shared logic goes in `internal/` to avoid duplication across scripts.

## Script Patterns

### Single-tool wrapper (coderabbit pattern)
One script wraps a CLI tool: handles invocation, timeout, output capture, and writes result to a file.

```python
def run_tool(output_path: Path, timeout: int) -> int:
    tool = shutil.which("mytool")
    if not tool:
        raise RuntimeError("mytool not found")
    process = subprocess.Popen([tool, "--flag"], stdout=subprocess.PIPE, ...)
    try:
        stdout, _ = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        ...
    output_path.write_text(stdout or "")
    return process.returncode
```

### Validator (skill-master pattern)
Checks structure/content and exits non-zero with a clear error message on failure.

```python
def validate(skill_path: Path) -> list[str]:
    errors = []
    if not (skill_path / "SKILL.md").exists():
        errors.append("Missing SKILL.md")
    # ... more checks
    return errors
```

### Data extractor / report generator
Fetches data (via CLI or API), processes it, writes structured output (JSON, YAML, Markdown) to a file for the agent to read.

## How to Reference Scripts in SKILL.md

Be explicit about invocation, arguments, and expected output:

```markdown
## Step 2: Validate

Run `python scripts/validate.py --input {filename}`.
Expected output: "Validation passed" or a list of errors to fix.

Common errors:
- "Missing required field X" → add the field
- "Invalid format for Y" → use format Z
```

For Go scripts:
```markdown
Run `go run ./scripts/check-cluster-health <cluster-name>`.
Requires: kubectl configured with access to the target cluster.
```

## What Scripts Should NOT Do

- No hardcoded paths, secrets, or environment-specific config
- No side effects without clear documentation (no silent writes to arbitrary locations)
- No network calls to external services unless clearly stated
- Avoid requiring packages not in the standard library without documenting the install command
