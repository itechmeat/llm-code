# Daily Workflow

Daily task operations with `bd` CLI.

## Non-interactive setup (v1.0.0)

Use the non-interactive flags when bootstrapping CI runners or cloud agents that cannot answer prompts.

```bash
bd init --non-interactive --role=<role>
bd bootstrap --non-interactive
```

Use `--role` to make the workspace intent explicit for agent automation.

Recent `1.0.4` setup/workflow additions:

- `bd init --remote` helps bootstrap against a remote-backed setup path more directly.
- `bd -C <dir> ...` changes directory before command execution, which is useful in automation that orchestrates multiple repos/workspaces from one parent shell.

## Daily Loop

```bash
# 0. Sync database state
bd sync

# 0b. Repair bootstrap/identity state when a workspace looks miswired
bd bootstrap

# 1. What can I work on?
bd ready                    # Unblocked tasks
bd ready --pretty           # Formatted output
bd ready --gated            # Tasks at gate checkpoints

# (Optional) see what is currently active
bd show --current

# 2. Pick and start work
bd update bd-xyz --status=in_progress

# 3. Complete work
bd close bd-xyz --reason "Implemented per spec"
bd close bd-xyz --reason "Implemented per spec" --claim-next

# 4. Share DB changes (when you want to share)
bd sync
```

If you are operating directly against Dolt remotes (advanced), you can also use:

```bash
bd dolt pull
bd dolt push
```

## Finding Work

### Workspace Context

```bash
bd context
bd context --json
```

Use this before planning or handoff when you need a concise snapshot of the current workspace/task state.

### Ready Tasks

```bash
bd ready                    # Tasks with no open blockers
bd ready --explain          # Explain dependency/blocker reasoning
bd ready --json             # JSON output for agents
bd ready --limit=10         # Limit results
```

### List Tasks

```bash
bd list                     # Default: 50 non-closed issues
bd list --all               # All issues
bd list --status=open       # Filter by status
bd list --status=open,in_progress  # Comma-separated status values
bd list --type=bug          # Filter by type
bd list --tree              # Tree view with hierarchy
bd list --tree --parent=bd-abc  # Subtree
```

### Show Details

```bash
bd show bd-xyz              # Full details + audit trail
bd show bd-xyz --short      # Compact output
bd view bd-xyz              # Alias for show
bd show --id bd-xyz         # Use when ID could be parsed as a flag
```

## Status Updates

```bash
# Update status
bd update bd-xyz --status=in_progress
bd update bd-xyz --status=done

# Update with fields
bd update bd-xyz --priority=0 --assignee="agent-1"

# Batch update
bd update bd-abc bd-def --status=in_progress

# Append notes
bd update bd-xyz --append-notes "New info"

# Ephemeral / persistent markers
bd update bd-xyz --ephemeral
bd update bd-xyz --persistent
```

### Compare-and-set updates (v1.3.0)

```bash
# Reassign only while the current assignee still holds the bead
bd update bd-xyz --if-assignee worker-1 -a mayor

# Transition only from the expected status
bd update bd-xyz --if-status=in_progress --status=done

# Inverse spelling for unclaim
bd unclaim bd-xyz --if-assignee worker-1
```

One atomic transaction; nothing is written on a mismatch. Exit code `13` means every failure in the run was a guard mismatch (a racer won — skip gracefully); exit `1` is any other failure. Under `--json`, each failed entry carries `"guard_mismatch": true`. `--if-assignee ''` means "expected unassigned". `claim.pools` (e.g. `bd config set claim.pools "fable-crew,night-crew"`) makes the listed aliases claimable by any actor through the same compare-and-swap, while beads assigned to a real actor keep their anti-steal protection.

### Status Values

| Status        | Meaning          |
| ------------- | ---------------- |
| `open`        | Not started      |
| `in_progress` | Work in progress |
| `done`        | Completed        |
| `hooked`      | Claimed by agent |

## Closing Tasks

```bash
# Close with reason (recommended)
bd close bd-xyz --reason "Implemented and tested"

# Close with a longer reason from file
bd close bd-xyz --reason-file ./close-reason.md

# Close and immediately claim the next ready task
bd close bd-xyz --reason "Implemented and tested" --claim-next

# Close multiple
bd close bd-abc bd-def --reason "Batch completion"

# Cannot close if blockers exist
# bd close bd-blocked  # Error: has open blockers
```

## Dependencies

```bash
# Add dependency (child blocks parent)
bd dep add bd-child bd-parent --blocks

# Add related link
bd dep add bd-a bd-b --related

# Remove dependency
bd dep rm bd-child bd-parent

# View dependency tree
bd dep tree bd-xyz
```

`1.0.x` also adds batch dependency listing for multiple issue IDs, which is useful when an agent is triaging several candidates at once.

Recent `1.0.4` automation paths also add JSONL bulk dependency add, which is useful when importing or repairing a larger dependency graph from generated/project data instead of issuing one `bd dep add` per edge.

## Labels

```bash
# Add labels
bd label add bd-xyz urgent backend

# Remove labels
bd label remove bd-xyz urgent

# List by label
bd list --label=urgent
```

## Activity Feed

```bash
bd activity                 # Recent activity
bd activity --watch         # Real-time feed
bd activity --town          # Cross-rig aggregated feed
bd activity --details       # Full issue details
```

### Durable events journal (v1.3.0)

Every committed bead mutation writes one ordered record in the same transaction as the mutation, carrying the operation, the mutated id, and the bead's full post-mutation snapshot (including `is_blocked`). `bd events` reads the journal, so history survives compaction and external readers can tail it.

## Agent Mode

For AI agents, use structured output:

```bash
BD_AGENT_MODE=1 bd ready --json
BD_AGENT_MODE=1 bd list --json
```

## HTTP API Server (v1.3.0)

`bd serve` exposes the whole work loop over HTTP: 41 OpenAPI-specified operations across 35 paths — ready/list/get/query/count/related, stats, dependencies (list, count, tree, blocking, cycles), config, memories, events, and the writes (claim, claimNext, release, close, reopen, PATCH, batchCreate/batchClose/batchApply, delete, sweep). Errors are RFC 9457 `problem+json` with a machine-readable `code` per HTTP status, so clients classify a claim conflict from a typed 409 instead of substring-matching prose. Listing pages use an opaque keyset cursor that survives restart; `GET /v0/beads/context` reports which operations the running build implements. The release also publishes a public Go API for embedding the engine.

Deployment model:

- `--auth-token-file` names a file of accepted bearer tokens (one per line); every operation except `GET /healthz` requires `Authorization: Bearer <token>`. The file is re-read while the server runs, so revocation is a file rewrite with no restart, and a failed re-read keeps the last-good set.
- There is deliberately no `--auth-token` flag (argv is readable from `ps`). `--allow-non-loopback` requires a token file; `--insecure-no-auth` is the explicit auditable opt-out; `--allowed-host` extends the DNS-rebinding allowlist.
- Read the omissions as contract: no TLS (the deployment supplies confidentiality), a token is a shared secret granting the whole surface rather than an identity, `actor` stays caller-asserted provenance, hooks do not fire on HTTP mutations, and the surface includes destructive operations (`issues:sweep`, `issues:delete`).

## Key-Value Store

Store arbitrary key-value data alongside issues:

```bash
bd kv set config.api_url "https://api.example.com"
bd kv get config.api_url
bd kv list                  # List all keys
bd kv delete config.api_url
```

Useful for storing agent configuration, session state, or project metadata.

## Batch config updates (v1.0.0)

Use `bd config set-many` when automation needs to apply several config changes together instead of mutating keys one by one.

## Backend Management

```bash
bd dolt show                # Show Dolt connection/remote settings
bd dolt test                # Validate connectivity
```

## Backup & Restore

Beads can produce JSONL backups for off-machine recovery and portability.

```bash
bd backup
bd backup status

bd export -o backup.jsonl
bd import -i backup.jsonl
```

Notes:

- Use `bd backup --help` to see the available options (location, format, automation).
- Treat restore as a bootstrap/recovery tool; validate Dolt connectivity after restoring.
- `bd import` supports incremental JSONL replay workflows and avoids duplicating already-imported comment history.

## Richer Task Creation (v0.61.0)

```bash
bd create "Task C" --context "Needs schema review" --skills "python,sql"
bd create "Scratch task" --no-history
```

- `--context` captures concise execution context at creation time.
- `--skills` records the intended skill/tooling surface for the task.
- `--no-history` skips the Dolt commit for that create operation without making the item GC-eligible.

## Maintenance

Standalone lifecycle helpers for keeping the Beads store healthy:

```bash
bd gc
bd compact
bd flatten
```

## Purge Closed Ephemeral Beads (v0.58.0)

Delete closed ephemeral beads (wisps) to reclaim storage:

```bash
bd purge
```

## Persistent Agent Memory (v0.58.0)

For knowledge that should survive sessions:

```bash
bd remember "key" "value"
bd memories
bd recall "key"
bd forget "key"
```

## Claiming Work

```bash
bd update bd-xyz --claim    # Mark as claimed by current agent
```

### Work leases (v1.3.0)

Claims carry a lease (`lease_expires_at`, default TTL 5m, plus `heartbeat_at`; schema v54), so a worker that dies mid-task no longer strands its bead `in_progress` forever:

```bash
bd heartbeat bd-xyz            # Extend the lease while working
bd reclaim --older-than 10m    # Revert expired leases back to ready
bd unclaim bd-xyz              # Give a claim back
```

Every ownership-mutating path rewrites a shared `row_lock` cell, so racing heartbeat-vs-reclaim becomes a serialization conflict the retry layer replays instead of cell-merging into a zombie claim; work-queue hot paths retry the same way, so N workers draining one queue stop surfacing raw MySQL 1213/1205 errors. Leases are replica-aware: `bd reclaim` skips a lease another replica granted unless you pass `--any-replica`; the guard is opt-in and fail-open, armed by `node_id` / `BEADS_NODE_ID`.

## Session End

```bash
# Sync before ending session (when you want to share)
bd sync
```

## Export

```bash
bd export -o backup.jsonl     # Export full DB backup (JSONL)
bd export --id bd-xyz        # Export specific issue
bd export --parent bd-abc    # Export subtree by parent
```

## Troubleshooting

```bash
bd doctor                   # Health check
bd doctor --fix             # Auto-fix issues
bd doctor --deep            # Full integrity check
bd doctor --server          # Dolt server mode health checks
bd doctor --agent           # Diagnostics for AI agent setups (v0.57.0)
```

## Safe Re-initialization (v0.60.0)

When automation must reinitialize a store non-interactively, use the explicit destroy-token flow instead of scripting blind destructive prompts.

```bash
bd init --destroy-token <token>
```

Treat the token as a deliberate safety barrier, not as a convenience flag to hardcode into generic scripts.
