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

## Review Commands

### Output Modes

| Mode        | Command                    | Use Case                               |
| ----------- | -------------------------- | -------------------------------------- |
| Interactive | `coderabbit`               | Browsable findings, apply fixes inline |
| Plain text  | `coderabbit --plain`       | Detailed feedback with suggestions     |
| Prompt-only | `coderabbit --prompt-only` | Optimized for AI agents                |

### Review Types

| Type        | Command                         | Description                              |
| ----------- | ------------------------------- | ---------------------------------------- |
| All changes | `coderabbit --type all`         | Both committed and uncommitted (default) |
| Uncommitted | `coderabbit --type uncommitted` | Working directory only                   |
| Committed   | `coderabbit --type committed`   | Committed changes only                   |

### Base Branch

```bash
# Default assumes 'main' branch
coderabbit --base develop
coderabbit --base master
```

### Combined Examples

```bash
# AI agent workflow: uncommitted changes only
coderabbit --prompt-only --type uncommitted

# Compare feature branch against develop
coderabbit --prompt-only --base develop

# Full options
coderabbit --prompt-only -t uncommitted --base develop
```

## Command Reference

| Command                    | Description                              |
| -------------------------- | ---------------------------------------- |
| `coderabbit`               | Run code review (interactive by default) |
| `coderabbit --plain`       | Plain text output                        |
| `coderabbit --prompt-only` | Minimal AI-optimized output              |
| `coderabbit auth login`    | Authenticate with CodeRabbit             |
| `coderabbit auth status`   | Check authentication status              |
| `cr`                       | Short alias for all commands             |

## Additional Options

| Option                    | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| `-t, --type <type>`       | Review type: all, committed, uncommitted               |
| `-c, --config <files...>` | Additional instruction files (claude.md, .cursorrules) |
| `--base <branch>`         | Base branch for comparison                             |
| `--base-commit <commit>`  | Base commit on current branch                          |
| `--cwd <path>`            | Working directory path                                 |
| `--no-color`              | Disable colored output                                 |

## Timing Notes

- Reviews take 7-30+ minutes depending on scope
- Use `--type uncommitted` for faster feedback
- Background execution recommended for AI agent workflows

## Uninstall

```bash
# If installed via script
rm $(which coderabbit)

# If installed via Homebrew
brew remove coderabbit
```
