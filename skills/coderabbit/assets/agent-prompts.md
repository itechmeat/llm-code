# CodeRabbit AI Agent Prompts

Ready-to-use prompts for integrating CodeRabbit with AI coding agents.

## Basic Review Prompt

```text
Run coderabbit --prompt-only --type uncommitted and fix any critical issues.
```

## Full Implementation + Review

```text
Implement [FEATURE DESCRIPTION] and then run coderabbit --prompt-only -t uncommitted,
let it run as long as it needs (run it in the background) and fix any critical issues.
Ignore style nits.
```

## Review with Severity Filter

```text
Run coderabbit --prompt-only and evaluate the findings:
- Fix all CRITICAL and HIGH severity issues
- Defer MEDIUM issues if not quick wins
- Skip LOW severity (style/formatting)

Provide a summary of what was fixed and what was deferred.
```

## Loop-Limited Review

```text
Run coderabbit --prompt-only --type uncommitted. Fix critical issues only.
Then run CodeRabbit again to verify.

Only run the loop twice. If on the second run you don't find any critical issues,
ignore remaining nits and report completion with a summary.
```

## Feature Branch Review

```text
I'm working on [FEATURE]. Run coderabbit --prompt-only --base develop
to compare against the develop branch. Focus on:
- Security vulnerabilities
- Breaking changes
- Performance regressions

Fix critical issues and document any architectural concerns.
```

## Cursor Rules Addition

Add to `.cursorrules`:

```text
# CodeRabbit Integration

CodeRabbit CLI is installed. Use it to review code changes.

Commands:
- `cr -h` for help
- `coderabbit --prompt-only -t uncommitted` for AI-optimized review

Rules:
- Run CodeRabbit with --prompt-only flag
- Don't run more than 3 times per change set
- Fix CRITICAL issues immediately
- Document MEDIUM issues if deferring
- Skip LOW (style) issues
```

## Claude.md Addition

Add to `claude.md` (Pro feature - CodeRabbit reads this):

```markdown
## Code Review Standards

When CodeRabbit reviews my code, apply these preferences:

### Focus Areas

- Security vulnerabilities (SQL injection, XSS, auth bypass)
- Data integrity (race conditions, transaction handling)
- Error handling (uncaught exceptions, missing validations)
- Performance (N+1 queries, memory leaks)

### Ignore

- Formatting (handled by Prettier/Black)
- Import ordering (handled by isort/eslint)
- Line length warnings

### Style Preferences

- Prefer explicit error handling over silent failures
- Use typed parameters and return values
- Keep functions under 50 lines
```
