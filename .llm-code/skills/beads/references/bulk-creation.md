# Bulk Creation (Batch Operations)

Create many issues in one shot from a Markdown file.

## Location Policy

Bulk-create plans MUST be written into a **project-local temp dir**:

```bash
mkdir -p .tmp/beads  # Keep gitignored
```

## Basic Command

```bash
bd --no-db create -f .tmp/beads/plan.md --json
```

## Markdown Format

```md
## EPIC — Example Feature

### Priority
2

### Type
epic

### Description
Contract/context.

### Design
Implementation plan.

### Acceptance Criteria
- [ ] Pass/fail item

## STAGE 1 — Core Implementation

### Priority
2

### Type
epic

### Description
Stage contract.

### Design
Stage approach.

### Acceptance Criteria
- [ ] Stage complete

### Labels
stage

### Dependencies
blocks:bd-123
```

### Section Notes

- Section names are case-insensitive
- `Acceptance` is accepted as alias for `Acceptance Criteria`
- Dependencies: `blocks:id`, `related:id`, or plain `id` (defaults to `blocks`)

## Option A: Hand-Write Plan

1. Copy template: `cp .beads/templates/stage-gate-plan.md .tmp/beads/my-plan.md`
2. Edit the plan
3. Create: `bd --no-db create -f .tmp/beads/my-plan.md --json`

## Option B: Generate from JSON

Use the helper script:

```bash
# 1. Write JSON plan
cat > .tmp/beads/plan.json << 'EOF'
{
  "issues": [
    {
      "title": "EPIC — Example",
      "priority": 2,
      "type": "epic",
      "description": "Contract",
      "design": "Approach",
      "acceptance_criteria": "- [ ] Done"
    }
  ]
}
EOF

# 2. Generate Markdown
python .github/skills/beads/scripts/bd_generate_markdown_plan.py \
  --in .tmp/beads/plan.json --print-path

# 3. Create issues
bd --no-db create -f <printed-path> --json
```

## Batch Delete

```bash
# Preview
bd delete <id> --dry-run --json

# Apply
bd delete <id> --force --json

# Multiple
bd delete id1 id2 id3 --force --json

# From file
bd delete --from-file ids.txt --force --json

# Prune tombstones
bd compact
```

## Batch Update

```bash
# Update status
bd update id1 id2 --status in_progress --json

# Close multiple
bd close id1 id2 --reason "..." --json

# Add labels
bd label add id1 id2 urgent --json
```

## Deletion Policy

- Prefer tombstones (`bd delete ...`) so deletions propagate
- Do NOT use `bd reset --force` as deletion shortcut
- Controlled "wipe JSONL" exception: see `.github/instructions/beads.instructions.md`
