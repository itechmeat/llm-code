# Sync & Integration

Beads v0.56+ uses Dolt-native sync for the issue database.

## TL;DR

- Use `bd dolt pull` / `bd dolt commit` / `bd dolt push` to synchronize.
- `bd sync` is deprecated (no-op) in v0.56+ and will print a hint.

## Dolt Sync Workflow

```bash
# Get latest issue DB changes
bd dolt pull

# Work normally (create/update/close/etc)
bd ready

# Record your changes in the Dolt DB
bd dolt commit

# Share changes with others
bd dolt push
```

Useful helpers:

- `bd dolt show` — show current Dolt connection/remote settings
- `bd dolt test` — validate connectivity
- `bd doctor --server` — server-mode health checks
- `bd dolt remote` — manage remotes (v0.57.0)
- `bd dolt start` / `bd dolt stop` — Dolt server lifecycle helpers (v0.57.0)

## Dolt Remote Management (v0.57.0)

Beads adds CLI helpers to manage Dolt remotes without editing config files.

```bash
bd dolt remote
bd dolt remote list
bd dolt remote add
bd dolt remote remove
```

Notes:

- If `bd dolt push/pull` fails over HTTPS due to environment constraints, v0.57.0 adds SSH push/pull fallback support.

## Server Mode Requirement (v0.56+)

Embedded Dolt mode was removed; Beads requires Dolt SQL server mode.
If Beads can’t connect, start with:

```bash
bd dolt test
bd doctor --server
```

## Upgrading From Pre-0.56

If your older workflow relied on git/JSONL sync (`bd sync`), expect it to do
nothing after upgrading. Switch your runbooks and agent prompts to Dolt commands.

In newer versions, the first `bd` invocation may migrate a local SQLite store to Dolt automatically. If you have existing local state, take a backup before upgrading.

If you previously used an older wisp/ephemeral store, follow Beads’ upgrade hints;
you may be prompted to run `bd migrate wisps`.

## External Integrations

Integrations (GitLab/Linear/Jira/etc.) are separate from Dolt DB sync: Dolt sync
keeps Beads’ local issue database consistent; integration commands exchange data
with external trackers.

### GitLab Sync

```bash
bd gitlab sync
bd gitlab status
```

### Linear Sync

```bash
bd linear sync --project-id=<id>
```

### Jira Import

```bash
bd jira import --project=KEY
```
