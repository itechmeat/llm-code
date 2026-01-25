# Daily Workflow

Daily task operations with `bd` CLI.

## Daily Loop

```bash
# 1. What can I work on?
bd ready                    # Unblocked tasks
bd ready --pretty           # Formatted output
bd ready --gated            # Tasks at gate checkpoints

# 2. Pick and start work
bd update bd-xyz --status=in_progress

# 3. Complete work
bd close bd-xyz --reason "Implemented per spec"

# 4. Sync changes
bd sync
```

## Finding Work

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
```

## Agent Mode

For AI agents, use structured output:

```bash
BD_AGENT_MODE=1 bd ready --json
BD_AGENT_MODE=1 bd list --json
```

## Claiming Work

```bash
bd update bd-xyz --claim    # Mark as claimed by current agent
```

## Session End

```bash
# Sync before ending session
bd sync

# Or just import changes without committing
bd sync --import-only
```

## Troubleshooting

```bash
bd doctor                   # Health check
bd doctor --fix             # Auto-fix issues
bd doctor --deep            # Full integrity check
```
