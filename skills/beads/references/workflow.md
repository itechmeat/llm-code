# Daily Workflow

Daily task operations with `bd` CLI.

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
bd ready --json             # JSON output for agents
bd ready --limit=10         # Limit results
```

### List Tasks

```bash
bd list                     # Default: 50 non-closed issues
bd list --all               # All issues
bd list --status=open       # Filter by status
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

## Agent Mode

For AI agents, use structured output:

```bash
BD_AGENT_MODE=1 bd ready --json
BD_AGENT_MODE=1 bd list --json
```

## Key-Value Store

Store arbitrary key-value data alongside issues:

```bash
bd kv set config.api_url "https://api.example.com"
bd kv get config.api_url
bd kv list                  # List all keys
bd kv delete config.api_url
```

Useful for storing agent configuration, session state, or project metadata.

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
