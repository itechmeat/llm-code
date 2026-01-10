# CodeRabbit Skill

AI-powered code review workflow using CodeRabbit CLI: triage findings by severity, implement focused fixes, and verify with project checks.

## What This Skill Covers

- **CLI Usage**: Install, authenticate, run reviews (prompt-only mode for agents)
- **Triage**: Classify findings by severity (CRITICAL/HIGH/MEDIUM/LOW), decide fix/defer/skip
- **Fixing**: Implement minimal, root-cause oriented fixes one issue at a time
- **Verification**: Run code checkers and tests after each fix

## Quick Navigation

- [SKILL.md](SKILL.md) — router-style entry point for agents
- [references/](references/) — topic-specific playbooks

## When to Use

Activate this skill when you need to:
- Run a pre-PR code review to catch issues early
- Triage CodeRabbit findings into actionable tasks
- Implement fixes for flagged issues with minimal scope creep
