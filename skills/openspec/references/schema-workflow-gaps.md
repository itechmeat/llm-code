# Schema Workflow Gaps and Proposed Fixes

## Current Gaps

- Schema is not bound to a change; users must remember `--schema`.
- No project-local schemas for version control.
- No schema management CLI for listing, copying, or diffing.
- No project default schema.

## Proposed Artifacts

### Change Metadata (change.yaml)

Store per-change schema:

- `schema`: selected workflow schema.
- `created`: timestamp (ISO8601).

### Project Config (openspec/config.yaml)

Store project default schema:

- `defaultSchema`: used when change metadata is missing.

### Project-Local Schemas

Resolution order proposal:

1. ./openspec/schemas/<name>/
2. ~/.local/share/openspec/schemas/<name>/
3. <package>/schemas/<name>/

## Selection Precedence

1. CLI `--schema` flag
2. Change metadata
3. Project default
4. Hardcoded fallback (spec-driven)

## Implementation Phases

- Phase 1: change.yaml creation and reading.
- Phase 2: project-local schemas.
- Phase 3: schema management CLI.
- Phase 4: init-time schema selection.

## Backwards Compatibility

- Missing change.yaml should default safely.
- Explicit `--schema` remains authoritative.
- No behavior break for existing changes.
