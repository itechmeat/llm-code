# AI Agent Integration

CodeRabbit CLI integrates with AI coding agents (Claude Code, Cursor, Codex) for autonomous review-fix workflows.

## Core Workflow

1. Implement feature
2. Run `coderabbit --prompt-only` in background
3. AI agent evaluates findings
4. Fix critical issues
5. Re-run CodeRabbit to verify

## Claude Code Integration

### Prerequisites

```bash
# Install CodeRabbit CLI
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
source ~/.zshrc
```

### Authenticate Inside Claude Code

```text
Run: coderabbit auth login
```

Follow browser redirect, paste token back to Claude.

### Usage Prompt

```text
Please implement phase 7.3 of the planning doc and then run coderabbit --prompt-only,
let it run as long as it needs (run it in the background) and fix any issues.
```

### Key Components

- `--prompt-only` — AI-optimized output format
- Background execution — Reviews take 7-30+ minutes
- Explicit fix instructions — "fix any critical issues, ignore nits"

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
Then run coderabbit. Once it completes, let it take as long as
it needs to fix any issues it might find.
```

### Cursor Rules File

Add to `.cursorrules`:

```text
# Running the CodeRabbit CLI

CodeRabbit is already installed in the terminal. Run it as a way to review your code.
Run the command: cr -h for details on commands available.
In general, I want you to run coderabbit with the `--prompt-only` flag.
To review uncommitted changes (this is what we'll use most of the time) run:
`coderabbit --prompt-only -t uncommitted`.

IMPORTANT: When running CodeRabbit to review code changes, don't run it more than 3 times
in a given set of changes.
```

## Codex Integration

Same pattern as Claude Code:

```text
Please implement phase 7.3 of the planning doc and then run coderabbit --prompt-only,
let it run as long as it needs and fix any issues.
```

## Recommended Commands

```bash
# Review uncommitted changes (most common)
coderabbit --prompt-only -t uncommitted

# Specify base branch
coderabbit --prompt-only --base develop

# Review all changes
coderabbit --prompt-only --type all
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
