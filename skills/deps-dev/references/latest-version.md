# Get the latest/default version (deps.dev API v3)

## Use this when

- You have `{system, packageName}` and want a single-request answer.

## Inputs

- `SYSTEM`: one of `GO`, `RUBYGEMS`, `NPM`, `CARGO`, `MAVEN`, `PYPI`, `NUGET`
- `packageName`: ecosystem-specific identifier

## Procedure (minimal)

1. Percent-encode the package name for use in a **path segment** (e.g. use `encodeURIComponent` in JS).
2. Call:
   - `GET https://api.deps.dev/v3/systems/{SYSTEM}/packages/{ENCODED_PACKAGE_NAME}`
3. Parse JSON with a real JSON parser (not `grep`) and locate `versions[]`.
4. Select the item where `isDefault` is `true`.
5. Return `versions[i].versionKey.version`.

## Expected failure modes (handle explicitly)

- HTTP 404: package not found (double-check ecosystem + name normalization).
- No `versions[]`: treat as an error; do not assume “no versions”.
- No version has `isDefault=true`: stop and ask for a selection rule.
  - deps.dev describes `isDefault` as system-specific, commonly “greatest version number ignoring pre-releases”.
  - If you need a different rule (e.g. include pre-releases, or pick by `publishedAt`), state it explicitly.

## Large responses (common)

The `versions[]` list can be very large. Do **not** truncate, stream to text, or parse via `grep`.

Use a JSON parser and extract only the default version:

- Python (stdin):
  - read JSON, then `next(v for v in versions if v.get("isDefault"))`
- Node.js (stdin):
  - parse JSON, then `versions.find(v => v.isDefault)`

If your toolchain truncates output, re-run the request and parse the JSON directly in-process.

## Examples

### npm scoped package

- System: `NPM`
- Name: `@colors/colors`
- Request path uses URL-encoding: `%40colors%2Fcolors`

### Maven package

- System: `MAVEN`
- Name format: `<groupId>:<artifactId>` (must be encoded when placed in the URL path)

## Output contract (suggested)

Return a small JSON object:

- `system`
- `package` (canonicalized name from response, if different)
- `version` (the selected default/latest)
- `publishedAt` (if present for the selected version)
