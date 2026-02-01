# Package naming + URL encoding (deps.dev API v3)

## Systems (ecosystems)

Use these exact identifiers in the URL:

- `GO`, `RUBYGEMS`, `NPM`, `CARGO`, `MAVEN`, `PYPI`, `NUGET`

## Naming gotchas

- Maven package names use the form `<groupId>:<artifactId>`.
- PyPI names are normalized per PEP 503 (the API may canonicalize the name).
- NuGet names are normalized by lowercasing, per NuGet Package Content API naming rules; versions are normalized per NuGet 3.4+ rules.

## URL encoding rules (practical)

The package name is part of the URL path, so you must percent-encode it as a path segment:

- npm scoped names contain `@` and `/` (encode both)
- Maven names contain `:` (encode it)

Implementation guidance:

- JavaScript: use `encodeURIComponent(packageName)`
- Python: use `urllib.parse.quote(packageName, safe="")`

Do not partially encode or hand-roll encoding.
