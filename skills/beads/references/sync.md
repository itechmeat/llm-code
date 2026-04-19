# Sync & Integration

Beads v0.58.0 uses Dolt as the primary backend and supports multiple sync strategies.

## TL;DR

- Prefer `bd sync` for the “do the right thing” sync loop.
- Use `bd dolt push` / `bd dolt pull` when operating directly with Dolt remotes.
- Use JSONL export/import for portability, migration, and off-machine backups.

## Recommended Loop (Most Teams)

```bash
bd sync
```

At a high level, `bd sync`:

1. Ensures local DB state is consistent
2. Pulls updates from the configured sync channel
3. Applies merges/conflict strategy
4. Pushes if configured (or if you didn’t opt out)

If you need to skip pushing (e.g. read-only environments):

```bash
bd sync --no-push
```

## Init / Bootstrap Auto-Detection (v0.61.0)

`bd init` and `bd bootstrap` can now auto-detect the Beads database from the repository's git origin.

- Prefer this when reconnecting an existing clone or repairing a miswired workspace.
- It reduces manual remote/database discovery during bootstrap and recovery flows.

`1.0.x` adds non-interactive init/bootstrap flows for CI and improves bootstrap recovery in fresh clones and shared-server scenarios.

## Sync Modes

Beads supports different sync modes depending on your backend and workflow.
The exact knobs live in `.beads/config.yaml` / `~/.config/bd/config.yaml`.

- `dolt-native` (recommended): Dolt remotes handle sync; cell-level merge.
- `git-portable` (legacy portability): JSONL export/import during sync operations.
- `belt-and-suspenders`: Dolt remotes + JSONL backups for extra redundancy.

## Dolt Remotes

Use `bd dolt remote` commands to manage remotes without editing config files:

```bash
bd dolt remote list
bd dolt remote add origin <url>
bd dolt remote remove origin

bd dolt pull
bd dolt push
```

Notes:

- For git-protocol remotes, Beads may fall back to the Dolt CLI for transfer.
- `bd dolt show` and `bd dolt test` help validate configuration and connectivity.
- In server mode and federation flows, Beads now routes CLI credentials through push/pull/fetch operations more consistently.
- `bd context` now reports the actual runtime Dolt port instead of assuming the default port.
- Credentials-file support is also available for Dolt server passwords in newer `1.0.x` setups.

## Multiple Clones / Worktrees: `.beads/redirect`

To make multiple clones share one database, create `.beads/redirect` containing a
single relative or absolute path to the target `.beads` directory.

```bash
mkdir -p .beads
echo "../main-clone/.beads" > .beads/redirect

bd where
bd where --json
```

Constraints:

- Redirects are single-level (A → B works; A → B → C does not)
- Target must exist and contain a valid database

## Backup / Portability (JSONL)

Use JSONL as an off-machine recovery path and migration/portability tool.

```bash
bd export -o backup.jsonl
bd import -i backup.jsonl
```

If auto-backup is enabled, you can trigger it manually:

```bash
bd backup
bd backup status
```

Set `BD_BACKUP_ENABLED=false` when automation must suppress backup commits.

## Upgrades & Migrations

For upgrades, prefer inspecting first:

```bash
bd migrate --inspect --json
bd migrate --to-dolt --dry-run
bd migrate --to-dolt
```

Recent releases also merge user-level config under project config instead of discarding it.

## External Integrations

Integrations (GitLab/Linear/Jira/etc.) are separate from database sync: sync keeps
Beads’ local issue database consistent; integrations exchange data with external
trackers.

For automation, prefer structured/JSON-aware error handling when integration commands fail instead of scraping human-readable error text.

`1.0.x` also tightened integration safety: external tracker content is sanitized for terminal display, response sizes are bounded, and sync warnings are surfaced more explicitly.

`bd doctor` also has stronger server-mode behavior, including cold-start Dolt detection and committed runtime/sensitive-file detection.

### GitLab Sync

```bash
bd gitlab sync
bd gitlab status
```

Recent updates improved GitLab dedup behavior, type filtering, and epic → milestone mapping.

### GitHub Issues Sync (v0.60.0)

```bash
bd github sync
bd github status
```

Use this when your coordination loop lives in GitHub Issues instead of GitLab, Linear, or Jira.

### Linear Sync

```bash
bd linear sync --project-id=<id>
```

### Jira Import

```bash
bd jira import --project=KEY
```

### Azure DevOps sync notes (1.0.x)

- ADO push flows now respect `--types`, `--states`, and `--no-create` filters more consistently.
- New work items are created in the initial state and then transitioned to the target state when needed.
