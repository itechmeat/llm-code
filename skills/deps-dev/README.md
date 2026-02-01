# deps-dev Skill

Agent Skill for using the deps.dev (Open Source Insights) API v3 to look up package metadata and quickly obtain the default/latest version.

## When to Use

- You already know a package name and the ecosystem (npm, PyPI, Maven, NuGet, Go, Cargo, RubyGems)
- You need the default/latest version with one HTTP request
- You want clear rules for URL-encoding package identifiers (scoped npm packages, Maven group:artifact, etc.)

## Files

| File                                                                   | Description                                     |
| ---------------------------------------------------------------------- | ----------------------------------------------- |
| [SKILL.md](SKILL.md)                                                   | Router + primary recipe                         |
| [references/latest-version.md](references/latest-version.md)           | Minimal steps to get the default/latest version |
| [references/large-responses.md](references/large-responses.md)         | Safe parsing of large version lists             |
| [references/api.md](references/api.md)                                 | Endpoint summary and response fields            |
| [references/naming-and-encoding.md](references/naming-and-encoding.md) | Package naming rules + URL encoding gotchas     |

## Links

- Documentation: https://docs.deps.dev/api/v3/
- API endpoint: https://api.deps.dev/v3/
