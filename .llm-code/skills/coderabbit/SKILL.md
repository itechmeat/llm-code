---
name: coderabbit
description: "CodeRabbit AI code review: CLI usage, configuration, PR commands, triage workflow, AI agent integration. Keywords: CodeRabbit, code review, CLI, @coderabbitai, triage, CRITICAL, HIGH, MEDIUM, LOW, Claude Code, Cursor."
---

# CodeRabbit

AI-powered code review for pull requests and local changes.

## Quick Navigation

| Task                          | Reference                                                   |
| ----------------------------- | ----------------------------------------------------------- |
| Install & run CLI             | [cli-usage.md](references/cli-usage.md)                     |
| Configure .coderabbit.yaml    | [configuration.md](references/configuration.md)             |
| Supported tools (40+ linters) | [tools.md](references/tools.md)                             |
| Git platform setup            | [platforms.md](references/platforms.md)                     |
| PR commands (@coderabbitai)   | [pr-commands.md](references/pr-commands.md)                 |
| Claude/Cursor/Codex workflow  | [agent-integration.md](references/agent-integration.md)     |
| Triage findings               | [triage.md](references/triage.md)                           |
| Fix single issue              | [fix.md](references/fix.md)                                 |
| End-to-end workflow           | [end-to-end-workflow.md](references/end-to-end-workflow.md) |
| Windows/WSL setup             | [windows-wsl.md](references/windows-wsl.md)                 |

## Quick Start

### Install

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
source ~/.zshrc
coderabbit auth login
```

### Run Review

```bash
# AI agent workflow (most common)
coderabbit --prompt-only --type uncommitted

# Interactive mode
coderabbit

# Plain text output
coderabbit --plain
```

### PR Commands

```text
@coderabbitai review          # Incremental review
@coderabbitai full review     # Complete review
@coderabbitai pause           # Stop auto-reviews
@coderabbitai resume          # Resume auto-reviews
@coderabbitai resolve         # Mark comments resolved
```

## Severity Matrix

| Severity     | Action          | Examples                                          |
| ------------ | --------------- | ------------------------------------------------- |
| **CRITICAL** | Fix immediately | Security, data loss, tenant isolation             |
| **HIGH**     | Should fix      | Reliability, performance, architecture violations |
| **MEDIUM**   | Judgment call   | Maintainability, type safety (quick wins)         |
| **LOW**      | Skip            | Style/formatting, subjective nits                 |

## AI Agent Workflow Pattern

```text
Implement [feature] and then run coderabbit --prompt-only -t uncommitted,
let it run in the background and fix any critical issues. Ignore nits.
```

Key points:

- Use `--prompt-only` for AI-optimized output
- Reviews take 7-30+ minutes
- Run in background, check periodically
- Limit to 2-3 iterations maximum

## Minimal Configuration

```yaml
# .coderabbit.yaml
language: en-US
reviews:
  profile: chill
  high_level_summary: true
  tools:
    gitleaks:
      enabled: true
    ruff:
      enabled: true
```

## Critical Prohibitions

- Do not introduce fallbacks, mocks, or stubs in production code
- Do not broaden scope beyond what CodeRabbit flagged
- Do not "fix" style nits handled by formatters/linters
- Do not ignore CRITICAL findings; escalate if unclear
- Stop and resolve CLI errors (auth/network) before fixing code

## Links

- Official docs: https://docs.coderabbit.ai/
- Schema: https://coderabbit.ai/integrations/schema.v2.json

## Templates

- [coderabbit.minimal.yaml](assets/coderabbit.minimal.yaml) — Minimal configuration
- [coderabbit.full.yaml](assets/coderabbit.full.yaml) — Full example with all options
- [agent-prompts.md](assets/agent-prompts.md) — Ready-to-use AI agent prompts
