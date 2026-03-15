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

## Upgrades & Migrations

For upgrades, prefer inspecting first:

```bash
bd migrate --inspect --json
bd migrate --to-dolt --dry-run
bd migrate --to-dolt
```

## External Integrations

Integrations (GitLab/Linear/Jira/etc.) are separate from database sync: sync keeps
Beads’ local issue database consistent; integrations exchange data with external
trackers.

For automation, prefer structured/JSON-aware error handling when integration commands fail instead of scraping human-readable error text.

### GitLab Sync

```bash
bd gitlab sync
bd gitlab status
```

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
