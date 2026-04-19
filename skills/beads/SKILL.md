---
name: beads
description: "Beads (bd) Dolt-backed issue tracker for agent task memory. Covers CLI ops, molecules, Dolt sync, Linear/Jira/GitLab. Use when tracking tasks and dependencies with the Beads CLI, syncing issues via Dolt, or integrating with Linear/Jira/GitLab. Keywords: bd, beads, Dolt, issue tracker."
metadata:
  version: "1.0.2"
  release_date: "2026-04-15"
---

# Beads (bd)

Distributed, Dolt-backed (Git-like) graph issue tracker for AI coding agents. Persistent memory with dependency-aware task tracking.

## Quick Start

Install: `brew install beads` or use the install scripts/binaries from the [GitHub repo](https://github.com/gastownhall/beads).

```bash
# Initialize in repo (humans run once)
bd init

# Tell your agent
echo "Use 'bd' for task tracking" >> AGENTS.md
```

## When to Use

- AI agent needs persistent task memory across sessions
- Tracking dependencies between tasks (`blocks:`, `depends_on:`)
- Multi-agent/multi-branch workflows (hash-based IDs prevent conflicts)
- Incremental delivery with molecules/gates
- Sync issues with GitLab, Linear, Jira, GitHub

## Essential Commands

| Command                       | Action                                    |
| ----------------------------- | ----------------------------------------- |
| `bd ready`                    | List tasks with no open blockers          |
| `bd ready --explain`          | Explain why tasks are or are not ready    |
| `bd ready --gated`            | Tasks waiting at gate checkpoints         |
| `bd ready --exclude-type=X`   | Exclude specific issue types              |
| `bd create "Title" -p 0`      | Create P0 task                            |
| `bd show <id>`                | View task details and audit trail         |
| `bd update <id> --status=X`   | Update status (open/in_progress/done)     |
| `bd close <id>`               | Close task                                |
| `bd close <id> --claim-next`  | Close current task and claim next         |
| `bd dep add <child> <parent>` | Link tasks (blocks, related, parent)      |
| `bd list`                     | List issues (default: 50, non-closed)     |
| `bd list --format json`       | JSON output (alias for `--json`)          |
| `bd show --current`           | Show active issue (no ID needed)          |
| `bd update <id> --claim`      | Atomically claim issue for work           |
| `bd note <id> "text"`         | Append note (shorthand)                   |
| `bd import -i <file>`         | Import JSONL incrementally                |
| `bd sync`                     | Sync database state                       |
| `bd dolt pull`                | Pull latest DB changes (advanced)         |
| `bd dolt push`                | Push DB changes (advanced)                |
| `bd bootstrap`                | Repair/bootstrap workspace identity       |
| `bd context`                  | Show current workspace/task context       |
| `bd kv set <key> <value>`     | Store key-value pair                      |
| `bd kv get <key>`             | Retrieve stored value                     |
| `bd dolt show`                | Show Dolt connection/remote settings      |
| `bd config set-many`          | Apply multiple config changes in one step |
| `bd ado sync`                 | Sync with Azure DevOps work items         |
| `bd ado status`               | Check Azure DevOps sync status            |
| `bd ado projects`             | List Azure DevOps projects                |
| `bd gitlab sync`              | Sync with GitLab                          |
| `bd github sync`              | Sync with GitHub Issues                   |
| `bd remember`                 | Write persistent agent memory             |
| `bd recall`                   | Read persistent agent memory              |
| `bd purge`                    | Delete closed ephemeral beads (wisps)     |

## Hash-Based IDs

Issues use hash-based IDs like `bd-a1b2` to prevent merge conflicts:

```bash
bd create "Fix login bug" -p 1
# Created: bd-x7k3

bd show bd-x7k3
```

### Hierarchical IDs

```
bd-a3f8      (Epic)
bd-a3f8.1    (Task)
bd-a3f8.1.1  (Sub-task)
```

Use `bd children <id>` to view hierarchy.

## References

| File                                    | Purpose                               |
| --------------------------------------- | ------------------------------------- |
| [workflow.md](references/workflow.md)   | Daily operations, status flow, sync   |
| [authoring.md](references/authoring.md) | Writing quality issues, EARS patterns |
| [molecules.md](references/molecules.md) | Molecules, gates, formulas, compounds |
| [sync.md](references/sync.md)           | Dolt sync, upgrades, and integrations |

## Key Concepts

### Dolt as Database

Beads stores issues in a Dolt database. Team synchronization happens via Dolt-style
`pull`/`push`, not by committing JSONL files into your repo history.

### Dependency Graph

```bash
bd dep add bd-child bd-parent --blocks   # child blocks parent
bd dep add bd-a bd-b --related           # related items
bd ready                                 # only shows unblocked work
```

### Molecules (Advanced)

Molecules group related issues with gates for incremental delivery:

```bash
bd mol create "Feature X" --steps=3      # Create 3-step molecule
bd mol progress bd-xyz                   # Check progress
bd mol burn bd-xyz                       # Complete molecule
```

### Stealth Mode

Use Beads locally without committing to repo:

```bash
bd init --stealth
```

### Contributor vs Maintainer

```bash
# Contributor (forked repos) — separate planning repo
bd init --contributor

# Maintainer auto-detected via SSH/HTTPS credentials
```

## Configuration

Config stored in `.beads/config.yaml`:

The exact schema evolves between releases. Prefer using CLI helpers to inspect
and validate your current setup:

- `bd dolt show` to see current Dolt connection/remote settings
- `bd dolt test` to validate connectivity
- `bd doctor` / `bd doctor --deep` for health checks

## Storage Backend (Dolt)

Beads uses Dolt as its primary backend. Depending on your setup, Dolt can run:

- Embedded (single-writer, no daemon)
- Server mode (multi-writer)

Use `bd doctor` (and `bd doctor --server` when applicable) to validate your
environment. For legacy stores, use `bd migrate` workflows.

## Agent Integration

### Tell Agent About Beads

Add to `AGENTS.md`:

```markdown
## Task Tracking

Use `bd` for task tracking. Run `bd ready` to find work.
```

### Agent-Optimized Output

```bash
BD_AGENT_MODE=1 bd list --json  # Ultra-compact JSON output
bd list --json                   # Standard JSON output
```

### MCP Plugin

Beads includes Claude Code MCP plugin for direct integration.

## Release Highlights (1.0.0–1.0.2)

- **Distribution**: precompiled binaries now cover Linux, macOS (Intel/Apple Silicon), Windows (AMD64/ARM64), Android/Termux, and FreeBSD.
- **Automation**: `bd init --non-interactive` / `--role` and `bd bootstrap --non-interactive` improve CI/cloud-agent setup.
- **Workflow**: `bd ready --explain`, `bd config set-many`, batch dependency listing, and comma-separated status filters improve agent ergonomics.
- **Authoring/modeling**: `spike`, `story`, and `milestone` are now first-class issue types; custom statuses/types moved to normalized tables.
- **Integrations/sync**: GitLab sync adds better dedup + epic→milestone mapping, ADO sync respects more filters, and embedded/shared-server recovery got safer.

## Release Highlights (0.62.0–0.63.3)

- **Azure DevOps integration**: `bd ado` CLI commands (sync, status, projects) for work item tracking.
- **Embedded Dolt support**: dep, duplicate, epic, graph, supersede, swarm operations work without a running Dolt server.
- **Custom status categories**: configure active/wip/done/frozen status groupings.
- **`bd note` command**: shorthand for appending notes to issues.
- **`--exclude-type` flag**: filter by issue type on `bd ready` and `bd list`.
- **`--format json` alias**: alternative to `--json` flag for consistency.
- **Audit log**: captures close reason; status changes logged to `interactions.jsonl`.
- **Memories in export/import**: round-trip includes agent memories.
- **Init defaults**: AGENTS.md defaults to minimal profile; `--agents-profile` flag added.
- **Quality/lifecycle commands**: surfaced in prime, template, and doctor.
- **Validation on close**: `--validate` checks `--acceptance` field; `validation.on-close` config.

## Release Highlights (0.61.0)

- `bd close --claim-next` shortens the common close-and-claim-next loop for agents.
- `bd create` gains `--skills`, `--context`, and `--no-history` for richer task creation and optional Dolt-history suppression.
- `bd import` adds incremental JSONL import for portability and recovery workflows.
- `bd init` / `bd bootstrap` can auto-detect the Beads database from the repository git origin.
- Dolt/server-mode sync improves credential pass-through, runtime port reporting, and health checks.
- Config and backup handling are safer, including proper project+user config merge and `BD_BACKUP_ENABLED=false` support.

## Critical Commands

```bash
# What to work on
bd ready                    # Unblocked tasks
bd ready --pretty           # Formatted output

# Create with dependencies
bd create "Task B" --blocks bd-a1b2
bd create "Task C" --context "Need schema review" --skills "python,sql"

# Doctor (fix issues)
bd doctor                   # Check health
bd doctor --fix             # Auto-fix problems

bd sync                     # Sync DB state
bd import -i backup.jsonl   # Incremental JSONL import

bd dolt pull                # Pull latest changes (advanced)
bd dolt push                # Push to remote (advanced)
```

## Anti-patterns

| ❌ Wrong              | ✅ Correct                  |
| --------------------- | --------------------------- |
| `priority: high`      | `-p 1` (P0-P4 numeric)      |
| Manual JSON editing   | Use `bd` commands           |
| Ignoring `bd ready`   | Always check blockers first |
| Skipping `bd sync`    | Sync before/after work      |
| Creating without deps | Declare `--blocks` upfront  |

## Links

- [Releases](https://github.com/gastownhall/beads/releases)
- [Documentation](https://github.com/gastownhall/beads#readme)
- [Community Tools](https://github.com/gastownhall/beads/blob/main/docs/COMMUNITY_TOOLS.md)
