# CodeRabbit CLI Usage

## Installation

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

Restart shell after installation:

```bash
source ~/.zshrc  # or source ~/.bashrc
```

## Authentication

```bash
coderabbit auth login
# Short alias
cr auth login
```

Follow browser redirect, sign in, copy token back to CLI.

Check status:

```bash
coderabbit auth status
```

## Prerequisites

CodeRabbit CLI requires:
1. **Initialized git repo** — must be run from within a git repository
2. **At least one commit** — the CLI uses git diff internally and will crash with `GitError` on repos with no commits
3. **Valid base branch** — defaults to `main`; use `--base` if your branch is named differently (e.g., `master`, `develop`)

## Review Commands

The `review` subcommand is the default — `coderabbit --plain` and `coderabbit review --plain` are equivalent.

### Output Modes

| Mode        | Command                            | Use Case                               |
| ----------- | ---------------------------------- | -------------------------------------- |
| Interactive | `coderabbit review`                | Browsable findings, apply fixes inline |
| Plain text  | `coderabbit review --plain`        | Detailed feedback with suggestions     |
| Prompt-only | `coderabbit review --prompt-only`  | Optimized for AI agents                |

### Review Types

| Type        | Command                                 | Description                              |
| ----------- | --------------------------------------- | ---------------------------------------- |
| All changes | `coderabbit review --type all`          | Both committed and uncommitted (default) |
| Uncommitted | `coderabbit review --type uncommitted`  | Working directory only                   |
| Committed   | `coderabbit review --type committed`    | Committed changes only                   |

### Base Branch

```bash
# Default assumes 'main' branch — override if needed
coderabbit review --base master
coderabbit review --base develop
```

### Combined Examples

```bash
# AI agent workflow: uncommitted changes, non-interactive
coderabbit review --prompt-only --type uncommitted --base master --no-color

# Compare feature branch against develop
coderabbit review --prompt-only --base develop --no-color

# Human-readable review
coderabbit review --plain --type uncommitted --no-color
```

## Command Reference

| Command                        | Description                              |
| ------------------------------ | ---------------------------------------- |
| `coderabbit review`            | Run code review (interactive by default) |
| `coderabbit review --plain`    | Plain text output                        |
| `coderabbit review --prompt-only` | Minimal AI-optimized output           |
| `coderabbit auth login`        | Authenticate with CodeRabbit             |
| `coderabbit auth status`       | Check authentication status              |
| `coderabbit update`            | Update CLI to latest version             |
| `cr`                           | Short alias for all commands             |

## Additional Options

| Option                    | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| `-t, --type <type>`       | Review type: all, committed, uncommitted               |
| `-c, --config <files...>` | Additional instruction files (claude.md, .cursorrules) |
| `--base <branch>`         | Base branch for comparison (default: main)             |
| `--base-commit <commit>`  | Base commit on current branch                          |
| `--cwd <path>`            | Working directory path                                 |
| `--no-color`              | Disable colored output (recommended for agents)        |
| `--api-key <key>`         | API key for authentication (usage-based billing)       |

## Timing Notes

- Reviews take 7-30+ minutes depending on scope
- Use `--type uncommitted` for faster feedback
- Background execution recommended for AI agent workflows
- Use `--no-color` when capturing output programmatically

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `[error] stopping cli` + `GitError` in logs | No commits in repo | Create at least one commit |
| `Failed to get commit SHA for branch main` | Base branch doesn't exist | Use `--base master` or appropriate branch |
| `Raw mode is not supported` | Interactive mode without TTY | Use `--prompt-only` or `--plain` |
| Silent failure, empty output | Auth expired | Re-run `coderabbit auth login` |

Debug mode: `DEBUG=* coderabbit review --prompt-only 2>&1`
Logs: `~/.coderabbit/logs/`

## Uninstall

```bash
# If installed via script
rm $(which coderabbit)

# If installed via Homebrew
brew remove coderabbit
```
