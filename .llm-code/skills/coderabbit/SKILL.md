---
name: coderabbit
description: "CodeRabbit CLI review workflow: run reviews, triage findings by severity, implement focused fixes. Keywords: CodeRabbit, code review, triage, fix, prompt-only, CRITICAL, HIGH, MEDIUM, LOW."
---

# CodeRabbit (Skill Router)

This file routes you to the right reference based on your task.

## Choose by situation

### Running a review

- CLI installation and commands: `references/cli-usage.md`
- Configuration (.coderabbit.yaml): `references/configuration.md`
- Windows/WSL setup: `references/windows-wsl.md`

### Processing review output

- Triage workflow (classify and plan): `references/triage.md`
- Implement a single fix: `references/fix.md`
- End-to-end workflow overview: `references/end-to-end-workflow.md`

### Agent integration

- Prompt template for dispatching agents: `references/agent-prompt-template.md`
- GitHub PR commands (@coderabbitai): `references/github-pr-commands.md`

## Severity matrix

| Severity     | Action          | Examples                                               |
| ------------ | --------------- | ------------------------------------------------------ |
| **CRITICAL** | Fix immediately | Security, data loss, tenant isolation, fallbacks/mocks |
| **HIGH**     | Should fix      | Reliability, performance, architecture violations      |
| **MEDIUM**   | Judgment call   | Maintainability, type safety (quick wins)              |
| **LOW**      | Skip            | Style/formatting, subjective nits                      |

## Critical prohibitions

- Do not introduce fallbacks, mocks, or stubs in production code.
- Do not broaden scope beyond what CodeRabbit flagged.
- Do not "fix" style nits already handled by formatters/linters.
- Do not ignore CRITICAL findings; escalate if unclear.

## Links

- Official docs: https://docs.coderabbit.ai/
