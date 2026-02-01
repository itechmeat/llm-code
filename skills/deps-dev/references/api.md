# deps.dev API v3: endpoints you’ll use

Base: `https://api.deps.dev/v3`

## GetPackage (best for “latest/default version”)

`GET /systems/{system}/packages/{name}`

Key response fields:

- `packageKey.system`, `packageKey.name` (may be canonicalized)
- `versions[]` (available versions)
  - `versions[].versionKey.version` (string)
  - `versions[].publishedAt` (optional)
  - `versions[].isDefault` (boolean; marks the default version)

## GetVersion (details for a specific version)

`GET /systems/{system}/packages/{name}/versions/{version}`

Useful when you need licenses/advisories/links:

- `licenses[]` (SPDX expressions or "non-standard")
- `advisoryKeys[]` (OSV IDs)
- `links[]`
- `attestations[]`

## Query (lookup by version key or content hash)

`GET /query?...`

Supports:

- `versionKey.system`, `versionKey.name`, `versionKey.version`
- `hash.type`, `hash.value`

Notes:

- Up to 1000 results.
- Use Query when you already know the version and want “GetVersion-like” details in batch-ish form.
