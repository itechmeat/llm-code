---
name: beads
description: "Task tracking with Beads (bd/bv): spec-grade issues, stage/gate delivery, dependency graphs, bulk operations. Use when creating issues, planning work, or managing daily task workflow. Keywords: beads, bd, bv, issues, tasks, stage-gate, EARS, bulk create."
---

# Beads Skill

Task tracking with Beads (bd) and beads_viewer (bv).

## When to use

- Creating, updating, or closing issues/tasks
- Planning work with Stage/Gate delivery pattern
- Writing spec-grade requirements (EARS methodology)
- Bulk-creating issues from Markdown files
- Querying triage/insights via `bv --robot-*` flags

## Core commands

```bash
# Triage (start here)
bv --robot-triage           # Full recommendations + quick wins + blockers
bv --robot-next             # Single top pick

# Daily operations
bd ready                    # Unblocked work ready to start
bd list --status=open       # All open issues
bd show <id>                # Full issue details
bd update <id> --status=in_progress
bd close <id>               # Close single issue
bd close <id1> <id2>        # Close multiple issues

# Session end
bd sync --flush-only        # Export to JSONL (no git)
```

## Issue requirements

Every issue MUST have:

1. **Clear acceptance criteria** — measurable outcomes
2. **Dependencies declared** — `blocks:` and `depends_on:` fields
3. **Type and priority** — P0-P4 (numbers), task/bug/feature/epic

## References

| File                                            | Purpose                                                             |
| ----------------------------------------------- | ------------------------------------------------------------------- |
| [authoring.md](references/authoring.md)         | Spec-grade issue writing: EARS patterns, NFRs, acceptance scenarios |
| [workflow.md](references/workflow.md)           | Daily operations: bd/bv commands, status updates, session flow      |
| [stage-gate.md](references/stage-gate.md)       | Stage/Gate pattern: naming, dependency chain, tranches              |
| [bulk-creation.md](references/bulk-creation.md) | Batch operations: markdown format, JSON plan script                 |

## Scripts

| Script                                                               | Purpose                                           |
| -------------------------------------------------------------------- | ------------------------------------------------- |
| [bd_generate_markdown_plan.py](scripts/bd_generate_markdown_plan.py) | Generate Beads-compatible Markdown from JSON plan |

## Quick quality checklist

Before closing any issue:

- [ ] Acceptance criteria met and verified
- [ ] Tests pass (if code change)
- [ ] No regressions introduced
- [ ] Dependencies updated (if applicable)
- [ ] Documentation updated (if user-facing)

## Stage/Gate quick reference

```
Stage-1 → Gate-1 (review) → Stage-2 → Gate-2 (review) → ...
```

- **Stage** = implementation tranche (coding).
- **Gate** = QA checkpoint (review, testing).
- Pattern: `{story}-Stage-{n}`, `{story}-Gate-{n}`.

## Anti-patterns

| ❌ Wrong                       | ✅ Correct                  |
| ------------------------------ | --------------------------- |
| `priority: high`               | `priority: 1` (P0-P4 scale) |
| Vague acceptance               | EARS-style requirements     |
| Missing `blocks:`              | Explicit dependency graph   |
| `bd create` without template   | Use `bd create -f plan.md`  |
| Interactive `bv` in automation | `bv --robot-*` flags only   |
