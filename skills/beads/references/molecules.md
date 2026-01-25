# Molecules & Gates

Molecules group related issues for incremental delivery with QA checkpoints.

## Concepts

### Molecule

A molecule is a collection of related issues (steps) that form a deliverable unit:

```bash
bd mol create "Feature X" --steps=3
# Creates: bd-xyz (molecule) with 3 step issues
```

### Gates

Gates are QA checkpoints between steps:

```bash
bd ready --gated           # Tasks waiting at gates
bd gate check bd-xyz       # Evaluate gate conditions
```

## Creating Molecules

### Simple Molecule

```bash
bd mol create "Add user auth" --steps=3
```

Creates:

- `bd-abc` (molecule root)
- `bd-abc.1` (step 1)
- `bd-abc.2` (step 2)
- `bd-abc.3` (step 3)

### With Variables

```bash
bd mol create "Feature" --steps=2 --var="component=auth"
```

### From Formula

```bash
bd mol pour my-formula --var="name=auth"
```

## Managing Molecules

```bash
# Progress check
bd mol progress bd-abc

# Show compound structure
bd mol show bd-abc

# Complete molecule
bd mol burn bd-abc

# Batch burn
bd mol burn bd-abc bd-def bd-ghi
```

## Wisps (Ephemeral Molecules)

Lightweight molecules for quick experiments:

```bash
bd mol wisp create "Quick test"
bd mol burn --wisp  # Burns all wisps
```

## Gate Types

### Human Gates

Manual approval required:

```bash
bd gate add-waiter bd-step1 --human
bd gate show bd-step1
```

### Timer Gates

Wait for time period:

```bash
bd gate check bd-xyz  # Checks timer conditions
```

### GitHub Gates

Wait for CI/workflow:

```bash
bd gate check bd-xyz --gh:run  # Check GitHub Actions
bd gate discover bd-xyz        # Auto-discover workflow ID
```

### Merge-Slot Gates

Serialized conflict resolution:

```bash
bd slot set bd-xyz agent-1
bd slot show bd-xyz
```

## Formulas

Reusable molecule templates:

```bash
# List formulas
bd mol list-formulas

# Pour (instantiate) formula
bd mol pour release-checklist --var="version=1.0"

# Validate template
bd lint template.yaml
```

### Formula Structure

```yaml
name: release-checklist
steps:
  - title: "Prepare {{version}}"
    gate:
      type: human
  - title: "Deploy {{version}}"
    condition: "{{ci_passed}}"
```

## Compounds

Nested molecule structures:

```bash
bd mol show bd-abc --tree  # Show compound hierarchy
```

## Best Practices

1. **Use gates** for mandatory review points
2. **Keep molecules small** (3-5 steps max)
3. **Name descriptively** for audit trail
4. **Use formulas** for repeatable patterns
5. **Check progress** regularly with `bd mol progress`
