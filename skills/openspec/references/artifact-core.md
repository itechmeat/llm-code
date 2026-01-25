# Artifact Graph Core (OPSX)

## Key Principles

- The system is an artifact tracker with dependency awareness, not a workflow engine.
- Dependencies are enablers: they indicate what can be created next, not what must be done.
- Completion is inferred from filesystem state (file existence), not stored in a database.

## Terminology

- **Change**: A unit of work (feature, refactor, migration) tracked under a change directory.
- **Schema**: A graph definition for artifacts and dependencies.
- **Artifact**: A node in the graph, usually a document to produce.
- **Template**: Instructions for creating a specific artifact.

## Schema Resolution (XDG)

Resolution order:

1. User override: ${XDG_DATA_HOME}/openspec/schemas/<name>/schema.yaml
2. Built-in: <package>/schemas/<name>/schema.yaml

Notes:

- Use XDG data locations for schema data, not config.
- Built-ins are not auto-copied; users override by creating files in the data dir.

## Template Resolution (Two Levels)

Resolution order:

1. User override: ${XDG_DATA_HOME}/openspec/schemas/<schema>/templates/<artifact>.md
2. Built-in: <package>/schemas/<schema>/templates/<artifact>.md

Rules:

- No inheritance between schemas.
- Templates are always co-located with their schema.
- If missing, return an error instead of silently falling back elsewhere.

## Core Engine Behaviors

- Graph construction: artifacts are nodes with `requires` dependencies.
- Ready artifacts: all dependencies are complete.
- Blocked artifacts: dependencies are missing.
- Build order: topological sort of the DAG.
- Glob artifacts: patterns like `specs/*.md` count as complete when at least one file matches.

## CLI Contract (Deterministic)

- Commands must be explicit about the change context.
- CLI behavior is deterministic; agent may infer the change and pass it explicitly.
- Avoid ambiguous defaults for `--change` or `--schema` in CLI layer.

## Design Constraints

- Stateless by design; each command scans the filesystem.
- Avoid hidden or cached state that can drift.
- Always surface the resolved schema and template paths in diagnostics.
