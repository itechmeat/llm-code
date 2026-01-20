# CodeRabbit Skill

AI-powered code review for pull requests and local changes using CodeRabbit.

## What This Skill Covers

- **CLI Usage**: Install, authenticate, run reviews (interactive, plain, prompt-only modes)
- **Configuration**: .coderabbit.yaml settings, path instructions, tool configuration
- **PR Commands**: @coderabbitai commands for GitHub/GitLab PR interaction
- **Tools**: Integration with 40+ linters and security scanners
- **Platform Integration**: GitHub, GitLab, Azure DevOps, Bitbucket setup
- **AI Agent Workflow**: Claude Code, Cursor, Codex integration patterns
- **Triage**: Classify findings by severity (CRITICAL/HIGH/MEDIUM/LOW)
- **Fixing**: Implement minimal, root-cause oriented fixes

## Quick Navigation

- [SKILL.md](SKILL.md) — Router with quick start and severity matrix
- [references/](references/) — Detailed topic references

## Local Capture Script

Run the capture script with Python 3 to save the prompt-only report:

```bash
# From repository root:
python3 .llm-code/skills/coderabbit/scripts/run_coderabbit.py --output coderabbit-report.txt

# From .llm-code/skills/coderabbit:
python3 scripts/run_coderabbit.py --output coderabbit-report.txt
```

## When to Use

Activate this skill when you need to:

- Run pre-PR code reviews to catch issues early
- Configure CodeRabbit for your repository
- Integrate CodeRabbit with AI coding agents
- Triage and fix CodeRabbit findings

## Source

Based on official documentation: https://docs.coderabbit.ai/
