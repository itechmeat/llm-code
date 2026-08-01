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
  - `versions[].isDeprecated` (boolean; true if this version was marked deprecated by the package author)
  - `versions[].deprecatedReason` (string; free-text reason given for the deprecation, may be empty even when deprecated)

A version can be both `isDefault` and `isDeprecated` at the same time — pick the default first, then check deprecation separately before recommending it.

## GetVersion (details for a specific version)

`GET /systems/{system}/packages/{name}/versions/{version}`

Useful when you need licenses/advisories/links:

- `licenses[]` (SPDX expressions or "non-standard")
- `advisoryKeys[]` (OSV IDs)
- `links[]`
- `attestations[]`
- `isDeprecated` (boolean), `deprecatedReason` (string) — same meaning as the `versions[]` entries above, for this single version
- `projectStatus` (object) — whether the project is actively maintained, deprecated, quarantined, etc.
  - `projectStatus.status` (string), `projectStatus.reason` (string)
  - **PyPI only**: populated from PyPA project-status markers (see the [project-status-markers spec](https://packaging.python.org/en/latest/specifications/project-status-markers/)). Not set for any other system — do not treat an absent `projectStatus` as "actively maintained" for non-PyPI packages.

## Query (lookup by version key or content hash)

`GET /query?...`

Supports:

- `versionKey.system`, `versionKey.name`, `versionKey.version`
- `hash.type`, `hash.value`

Notes:

- Up to 1000 results.
- Use Query when you already know the version and want “GetVersion-like” details in batch-ish form.
- Each `results[].version` carries the same `isDeprecated`, `deprecatedReason`, and (PyPI-only) `projectStatus` fields as GetVersion.

## GetRequirements (resolved dependency graph, per ecosystem)

`GET /systems/{system}/packages/{name}/versions/{version}:requirements`

Returns one system-specific requirements object (`nuget`, `maven`, `npm`, etc.) matching `versionKey.system`. Two ecosystems carry richer, resolved data worth calling out:

### NuGet (`nuget`)

- `nuget.dependencyGroups[]` — requirements grouped by target framework
  - `dependencyGroups[].targetFramework` (string)
  - `dependencyGroups[].dependencies[]` — each with `name`, `requirement`, `include`, `exclude`
- `nuget.targetFrameworks[]` (string[]) — every target framework the package as a whole supports (package-level, not per group)
- `nuget.developmentDependency` (boolean) — package-level flag; true for build/analyzer-only packages that should not flow to consumers
- `nuget.frameworkAssemblies[]` — legacy .NET Framework assembly references: `assemblyName`, `targetFramework`
- `nuget.frameworkReferences[]` — modern shared-framework references (e.g. `Microsoft.NETCore.App`): `name`, `targetFramework`

### Maven (`maven`)

`maven.dependencies[]` and `maven.dependencyManagement[]` each gained resolved counterparts to the raw `name`/`version`, since Maven POMs can reference properties (`${…}`) and inherit from parent/imported POMs:

- `dependencies[].resolvedVersion` / `dependencyManagement[].resolvedVersion` (string) — the interpolated version, with any Maven property substituted in
- `dependencies[].resolvedName` / `dependencyManagement[].resolvedName` (string) — the interpolated package name
- `dependencies[].origin` / `dependencyManagement[].origin` (string) — where the entry was declared:
  - `""` — the current package's own merged/effective POM
  - `"parent"` — inherited from the parent POM
  - `"management"` — from a local or inherited `<dependencyManagement>` section
  - `"import"` — from another BOM imported inside `<dependencyManagement>`
- `maven.repositories[].resolvedUrl` (string) — the repository URL with any Maven property interpolated in, alongside the raw `url`

Use `resolvedVersion`/`resolvedName`/`resolvedUrl` when you need the actual, usable value; use the plain `version`/`name`/`url` fields only when you specifically want to see the raw, pre-interpolation POM declaration.
