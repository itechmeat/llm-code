# Backup & Restore

Beads keeps two independent safety nets:

- **Dolt-native backups** (`bd backup …`) — point-in-time snapshots of the database under `.beads/backup`, taken by the command hook when it detects a change.
- **JSONL export/import** (`bd export` / `bd import`) — a portable dump for off-machine recovery, migration and audit tooling.

They are not interchangeable: the Dolt-native family is the fast, in-workspace safety net, while JSONL is the slow, transportable one.

## Backup Family (v1.3.1)

| Command             | Action                                                   |
| ------------------- | -------------------------------------------------------- |
| `bd backup init`    | Register the backup source for this workspace             |
| `bd backup sync`    | Take a new snapshot of the current database               |
| `bd backup remove`  | Remove a registered backup                                |
| `bd backup status`  | Show registered backups and whether auto-backup is active |
| `bd backup restore` | Restore the database from a backup                        |

```bash
bd backup init
bd backup sync
bd backup status
bd backup restore
```

`bd backup restore` replaces the database. On a proxied-server workspace it stops the proxy and its Dolt child first, so the next `bd` command relaunches against the restored data instead of the old one.

Treat restore as a bootstrap/recovery tool, not a routine operation: validate Dolt connectivity afterwards (`bd dolt test`, `bd doctor`).

## Where the family works — and where it is refused

| Workspace topology                          | `bd backup …`                          |
| ------------------------------------------- | -------------------------------------- |
| Embedded / direct                           | Supported                              |
| Proxied server that bd runs itself          | Supported (since v1.3.1)               |
| External host                               | Refused — `proxy.backup.unsupported`   |
| Socket                                      | Refused — `proxy.backup.unsupported`   |
| Team-server database                        | Refused — `proxy.backup.unsupported`   |

The refusal carries `"reason": "design"`. It is a deliberate limitation, not a transient failure:

- `CALL DOLT_BACKUP('add', …)` would register the remote **on the server**, so every client pointing at that host would inherit the registration.
- A `file://` destination would resolve on the **server's** filesystem, not on the client's.

The command refuses instead of silently backing up somebody else's database. If you hit this, you are pointing at a shared/external database — take your safety net with `bd export` instead.

## Auto-backup (opt-in)

Auto-backup is **off by default** — in direct mode and on every server-mode workspace. Nothing is written to `.beads/backup` until you opt in:

```bash
bd config set backup.enabled true
```

```bash
BD_BACKUP_ENABLED=1 bd <command>
```

Once enabled, the post-command hook takes the same change-detected Dolt-native backup into `.beads/backup` that it takes in direct mode: it writes only when it detects a change, so a no-op command costs nothing.

Auto-backup deliberately does nothing when:

- the workspace points at an external host, socket, or team-server database
- the command runs under strict `--readonly`
- the command is `bd serve`
- the command runs with `--dry-run` or `--inspect`
- a migration freeze is active

### Checking the mode

`bd backup status` reports the auto mode explicitly. On a proxied-server workspace that has not opted in it prints:

```
auto: off in proxied-server mode; set backup.enabled=true to opt in
```

Older builds blamed a missing git remote here. That message was wrong and is gone — if you still see a git-remote complaint, you are on a pre-1.3.1 binary.

### Locking

A per-workspace `.beads/backup.lock` serializes auto-backup against `bd backup sync`: the two never run at the same time in the same workspace. Do not hand-delete the lock while a backup is in flight — the serialization guarantee only holds while bd owns it.

## Suppressing backups in automation

```bash
BD_BACKUP_ENABLED=false bd <command>
```

Use this when automation must suppress backup commits, for example in a CI job that shares a workspace with an interactive session.

## JSONL Portability

```bash
bd export -o backup.jsonl
bd import -i backup.jsonl
```

Export defaults are deliberately narrow:

- `bd export` excludes memories by default.
- `bd export` excludes ephemeral wisps by default.

If your migration or audit tooling assumed "everything goes into export", re-test those flows and opt back in intentionally.

`bd import` supports incremental JSONL replay and avoids duplicating already-imported comment history.

## Related

- `references/sync.md` — Dolt sync modes, remotes, federation
- `references/workflow.md` — the daily loop and purge/maintenance commands
