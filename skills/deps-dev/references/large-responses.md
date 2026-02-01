# Large responses: safe extraction of the default version

## Problem

`GetPackage` can return hundreds of versions. Tooling that truncates output or relies on text search (`grep`) will often miss `isDefault=true` and lead to guessed versions.

## Rule

Always parse JSON with a proper parser and extract only the `isDefault=true` entry.

## Minimal patterns (safe)

### Python (stdin JSON)

- Load JSON
- Find `versions[]` item with `isDefault` true
- Return `versionKey.version`

### Node.js (stdin JSON)

- Load JSON
- `versions.find(v => v.isDefault)`
- Return `versionKey.version`

## If output is truncated

- Re-run the request and parse the JSON directly in-process.
- Do not rely on terminal output capture.
- Do not extract version numbers from partial output.

## Anti-patterns

- Guessing versions from memory
- Sorting version strings without explicit rule
- Grep-ing for "version" or "isDefault" in a truncated response
