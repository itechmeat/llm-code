# Conventional Commits Skill

Specification for structured commit messages that enable automated changelog generation and semantic versioning.

## What This Skill Covers

- **Format Structure**: `<type>[scope]: <description>` with optional body and footer
- **Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- **Breaking Changes**: `!` suffix and `BREAKING CHANGE:` footer
- **SemVer Mapping**: How commits translate to version bumps
- **Changelog Integration**: Mapping commits to changelog sections

## Quick Navigation

- [SKILL.md](SKILL.md) — Complete specification and examples
- [assets/](assets/) — Templates and validation scripts

## When to Use

Activate this skill when you need to:

- Write commit messages following Conventional Commits
- Set up commit message validation
- Generate changelogs from commits
- Determine semantic version bumps

## Related Skills

- [changelog](../changelog/SKILL.md) — CHANGELOG.md format that commits feed into

## Source

Based on official specification: https://www.conventionalcommits.org/en/v1.0.0/
