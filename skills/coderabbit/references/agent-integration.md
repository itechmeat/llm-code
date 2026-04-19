# AI Agent Integration

CodeRabbit CLI integrates with AI coding agents (Claude Code, Cursor, Codex) for autonomous review-fix workflows.

## Core Workflow

1. Implement feature
2. **Run prerequisites check** (see below)
3. Run `coderabbit review --prompt-only` in background
4. AI agent evaluates findings
5. Fix critical issues
6. Re-run CodeRabbit to verify (max 2-3 iterations)

## Prerequisites (MUST CHECK BEFORE EVERY REVIEW)

```bash
# All of these must pass:
which coderabbit                           # CLI installed
coderabbit auth status 2>&1 | grep -q "Logged in"  # Authenticated
git rev-parse HEAD >/dev/null 2>&1         # Has at least one commit
git rev-parse main >/dev/null 2>&1         # Base branch exists (or use --base)
```

**Critical:** CodeRabbit CLI silently crashes with `[error] stopping cli` if:

- The repo has **no commits** (GitError)
- The **base branch** doesn't exist (defaults to `main`)

## Claude Code Integration

### Prerequisites

```bash
# Install CodeRabbit CLI
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
source ~/.zshrc

# Authenticate
coderabbit auth login
```

### Running Reviews

```bash
# Auto-detect base branch and run review
python3 ~/.claude/skills/coderabbit/scripts/run_coderabbit.py

# Or run CLI directly (specify base branch if not 'main'):
coderabbit review --prompt-only --type uncommitted --base master --no-color
```

### Key Components

- `review` — subcommand (optional, it's the default)
- `--prompt-only` — AI-optimized output format (implies `--plain`)
- `--no-color` — strip ANSI codes for clean parsing
- `--base <branch>` — specify base branch (default: `main`)
- `--type uncommitted` — only review working directory changes
- Background execution — reviews take 7-30+ minutes

### Configuration

CodeRabbit reads `claude.md` for coding standards (Pro feature).

## Cursor Integration

### Setup

```text
Let's verify you can run the CodeRabbit CLI.
Run the terminal command: coderabbit auth status and tell me the output.
```

### Usage Prompt

```text
Implement phase 7.3 - adding Withings smart scale integration.
Then run coderabbit review --prompt-only --type uncommitted --no-color.
Once it completes, fix any critical issues.
```

### Cursor Rules File

Add to `.cursorrules`:

```text
# Running the CodeRabbit CLI

CodeRabbit is already installed in the terminal. Run it as a way to review your code.
Run the command: cr review -h for details on commands available.
In general, I want you to run coderabbit with the `--prompt-only` flag.
To review uncommitted changes run:
`coderabbit review --prompt-only -t uncommitted --no-color`.

IMPORTANT: Before running CodeRabbit, verify the repo has at least one commit
(git rev-parse HEAD) and that the base branch exists.
Don't run CodeRabbit more than 3 times in a given set of changes.
```

## Codex Integration

CodeRabbit now has a dedicated Codex plugin in addition to the standalone CLI.

Setup flow:

1. Install Codex.
2. Install/authenticate CodeRabbit CLI.
3. Install the `coderabbit` plugin from the Codex plugin marketplace.
4. Trigger reviews with natural language or `@coderabbit` mentions.

Examples:

```text
Review my current changes with CodeRabbit
@coderabbit Review my current changes
```

Operational notes:

- The plugin verifies CLI installation and authentication before running.
- It summarizes the diff first, then reports findings with severity, file path, impact, and fix direction.
- Keep direct CLI usage for debugging/manual control; let the plugin drive normal Codex review loops.

## Structured agent output

- Prefer `coderabbit review --agent` when another agent needs machine-readable findings.
- Consume the output line by line and branch on event `type`; findings include severity, file path, and codegen guidance.

## Recommended Commands

```bash
# Review uncommitted changes (most common)
coderabbit review --prompt-only -t uncommitted --no-color

# Specify base branch (if not 'main')
coderabbit review --prompt-only --base master --no-color

# Review all changes
coderabbit review --prompt-only --type all --no-color
```

## Loop Limit Pattern

Prevent infinite iteration:

```text
Only run the loop twice. If on the second run you don't find any critical issues,
ignore the nits and you're complete. Give me a summary of everything that was
completed and why.
```

## Severity Prioritization

Instruct agent to prioritize:

```text
Evaluate the fixes and considerations. Fix major issues only, or fix any critical
issues and ignore the nits.
```

## Troubleshooting

### `[error] stopping cli` with no details

1. Check `git rev-parse HEAD` — repo must have at least one commit
2. Check `git rev-parse main` — base branch must exist (use `--base` to override)
3. Check `coderabbit auth status` — must be authenticated
4. Run with debug: `DEBUG=* coderabbit review --prompt-only 2>&1 | grep ERROR`
5. Check logs: `ls -t ~/.coderabbit/logs/ | head -1 | xargs -I{} cat ~/.coderabbit/logs/{}`

### Review Not Finding Issues

1. Check `coderabbit auth status`
2. Verify `git status` shows tracked changes
3. Use `--type uncommitted` for working directory
4. Specify `--base develop` if main branch differs

### Agent Not Applying Fixes

1. Ensure background execution in prompt
2. Use `--prompt-only` mode
3. Explicitly say "fix the issues found by CodeRabbit"
4. Check if review finished: "Is CodeRabbit finished running?"

### Managing Duration

- Use `--type uncommitted` for faster reviews
- Work on smaller feature branches
- Break large features into reviewable chunks
