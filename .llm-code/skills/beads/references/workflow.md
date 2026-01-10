# Beads Workflow (Daily Operations)

Daily task operations with bd (CLI) and bv (viewer).

## Daily Loop

```bash
# What can I start now?
bd ready

# Why is something blocked?
bd blocked

# Start work
bd update <id> --status in_progress

# Close with evidence
bd close <id> --reason "..."
```

## Viewing Work

### Interactive (Humans)

```bash
bv          # Launch TUI
# Press 'b' for Kanban board
```

### Structured (Agents)

```bash
bv --robot-next      # Top pick + claim command
bv --robot-plan      # Parallel execution tracks
bv --robot-triage    # Full recommendations
```

## Status Updates

```bash
# Single issue
bd update <id> --status in_progress

# Multiple issues
bd update id1 id2 --status in_progress --json

# Close with reason
bd close <id> --reason "Completed per gate checklist"

# Close multiple
bd close id1 id2 --reason "..." --json
```

## Labels

```bash
# Add labels
bd label add <id> urgent backend

# Remove labels
bd label remove <id> urgent
```

## Dependencies

```bash
# Add blocking dependency (B must be done before A)
bd dep add <A> <B>

# View dependencies
bd show <id>
```

## Session Sync

Always run before ending a session:

```bash
bd sync --flush-only  # Export beads changes to JSONL (no git commit)
```

## Keeping Contracts Discoverable

When using Stage/Gate:

- **Stage `description`**: Source-of-truth contract
- **Stage `design`**: Implementation approach
- **Gate `acceptance_criteria`**: Test/QA checklist
- **Gate `description`**: Exact inputs, expected vs actual, logs
