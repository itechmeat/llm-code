---
name: changelog
description: "Keep a Changelog format specification: structure, change types, versioning, best practices. Keywords: CHANGELOG.md, changelog, Added, Changed, Deprecated, Removed, Fixed, Security, Semantic Versioning."
---

# Changelog

Format specification for CHANGELOG.md based on Keep a Changelog 1.1.0.

## Quick Reference

### File Header

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

### Section Structure

```markdown
## [Unreleased]

### Added

- New feature description

## [1.0.0] - 2024-01-15

### Added

- Feature A
- Feature B

### Changed

- Modified behavior X

### Fixed

- Bug fix Y
```

## Types of Changes

| Type         | Purpose                           |
| ------------ | --------------------------------- |
| `Added`      | New features                      |
| `Changed`    | Changes in existing functionality |
| `Deprecated` | Soon-to-be removed features       |
| `Removed`    | Now removed features              |
| `Fixed`      | Bug fixes                         |
| `Security`   | Vulnerabilities                   |

## Format Rules

### Version Header

```markdown
## [X.Y.Z] - YYYY-MM-DD
```

- Version in brackets, linked to comparison
- Date in ISO 8601 format (YYYY-MM-DD)
- Unreleased section at top: `## [Unreleased]`

### Yanked Releases

```markdown
## [0.0.5] - 2014-12-13 [YANKED]
```

Use when version was pulled due to serious bug or security issue.

### Comparison Links (at file end)

```markdown
[unreleased]: https://github.com/user/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/repo/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/user/repo/releases/tag/v0.9.0
```

## Guiding Principles

1. **For humans, not machines** — Write clear, readable entries
2. **Entry for every version** — Document all releases
3. **Group same types** — Keep Added/Changed/Fixed together
4. **Linkable versions** — Use comparison links
5. **Latest first** — Reverse chronological order
6. **Show release dates** — Use ISO 8601 format
7. **State versioning scheme** — Mention Semantic Versioning if used

## Complete Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New authentication method

## [1.2.0] - 2024-01-20

### Added

- User profile page
- Export to CSV functionality

### Changed

- Improved loading performance by 40%

### Deprecated

- Legacy API endpoint `/api/v1/users` (use `/api/v2/users`)

### Fixed

- Login timeout issue on slow connections

## [1.1.0] - 2024-01-10

### Added

- Dark mode support

### Security

- Fixed XSS vulnerability in comment field

## [1.0.0] - 2024-01-01

### Added

- Initial release with core features
- User registration and login
- Dashboard with analytics

[unreleased]: https://github.com/user/project/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/project/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/project/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/project/releases/tag/v1.0.0
```

## Bad Practices

### Commit log diffs

**Don't** dump git log into changelog:

- Full of noise (merge commits, obscure titles)
- Not human-readable
- Mixes important and trivial changes

### Ignoring deprecations

**Don't** skip deprecation notices:

- Users need to know what will break
- Document deprecations before removals
- List breaking changes clearly

### Confusing dates

**Don't** use regional date formats:

- Use ISO 8601: `YYYY-MM-DD`
- Avoids ambiguity (is 01/02/2024 Jan 2 or Feb 1?)

### Inconsistent changes

**Don't** document only some changes:

- Changelog should be single source of truth
- Important changes must be mentioned
- Consistently updated

## Writing Tips

### Good Entry Examples

```markdown
### Added

- OAuth2 authentication with Google and GitHub providers
- Rate limiting for API endpoints (100 req/min)

### Changed

- Database queries now use prepared statements for better security
- Upgraded dependency `lodash` from 4.17.20 to 4.17.21

### Fixed

- Memory leak in WebSocket connection handler
- Race condition in concurrent file uploads
```

### Entry Guidelines

- Start with verb or noun describing the change
- Be specific (mention affected component/endpoint)
- Reference issue/PR numbers when relevant: `(#123)`
- Keep entries concise but informative

## File Naming

Recommended: `CHANGELOG.md`

Alternatives (less common):

- `HISTORY.md`
- `NEWS.md`
- `RELEASES.md`

## GitHub Releases vs CHANGELOG.md

| Aspect          | GitHub Releases | CHANGELOG.md      |
| --------------- | --------------- | ----------------- |
| Portability     | GitHub-only     | Universal         |
| Discoverability | Less visible    | Standard location |
| Version control | Separate UI     | In repository     |
| Diff links      | Manual setup    | Easy to add       |

GitHub Releases can complement but shouldn't replace CHANGELOG.md.

## Conventional Commits Integration

Changelogs work best with [Conventional Commits](../commits/SKILL.md) format:

| Commit Type       | Changelog Section    |
| ----------------- | -------------------- |
| `feat:`           | Added                |
| `fix:`            | Fixed                |
| `perf:`           | Changed              |
| `refactor:`       | Changed              |
| `docs:`           | (often omitted)      |
| `BREAKING CHANGE` | Highlight in Changed |
| Security fix      | Security             |
| `revert:`         | Removed or Fixed     |

### Automated Generation

Tools that parse Conventional Commits and generate changelogs:

- [conventional-changelog](https://github.com/conventional-changelog/conventional-changelog)
- [semantic-release](https://semantic-release.gitbook.io/)
- [release-please](https://github.com/googleapis/release-please)

See [commits skill](../commits/SKILL.md) for commit message format.

## Workflow Integration

### Unreleased Section Pattern

1. Add changes to `## [Unreleased]` during development
2. At release time, rename to `## [X.Y.Z] - YYYY-MM-DD`
3. Create new empty `## [Unreleased]` section
4. Add comparison link for new version

### Pre-commit Checklist

Before release:

- [ ] All notable changes documented
- [ ] Unreleased section moved to version
- [ ] Date added in ISO 8601 format
- [ ] Comparison link added
- [ ] Breaking changes highlighted
- [ ] Deprecations documented

## Critical Prohibitions

- Do not use git log as changelog
- Do not omit breaking changes or deprecations
- Do not use ambiguous date formats
- Do not leave changelog inconsistently updated
- Do not forget to update Unreleased → version at release

## Links

- Official specification: https://keepachangelog.com/en/1.1.0/
- Semantic Versioning: https://semver.org/spec/v2.0.0.html
- Related: [commits skill](../commits/SKILL.md) — Conventional Commits format

## Templates

- [CHANGELOG.template.md](assets/CHANGELOG.template.md) — Empty template to start
- [CHANGELOG.example.md](assets/CHANGELOG.example.md) — Complete working example
