# Stage/Gate Pattern

Incremental delivery with mandatory QA checkpoints.

## Concepts

| Role | Purpose |
|------|---------|
| **Stage** | Shippable implementation tranche (code changes) |
| **Gate** | Manual QA checkpoint proving the Stage is shippable |

## Title Prefixes (Required)

Issue titles MUST embed the role:
- Epic: `EPIC — ...`
- Stage: `STAGE <N> — ...`
- Gate: `GATE <N> — ...`

## Type Mapping

| Issue Role | `type` Value | Notes |
|------------|--------------|-------|
| EPIC | `epic` | Container for stages |
| STAGE | `epic` | Implementation work |
| GATE | `task` | Do NOT use `type: gate` (falls back to task) |

Use title prefix + `gate` label for gates.

## Dependency Chain

Recommended linear pipeline:

```
STAGE 1 → GATE 1 → STAGE 2 → GATE 2 → ...
```

- `GATE 1` blocks on `STAGE 1`
- `STAGE 2` blocks on `GATE 1`
- `GATE 2` blocks on `STAGE 2`

This guarantees Stage N+1 cannot start until Gate N passes.

### Commands

```bash
# Add blocking dependency (B must be done before A)
bd dep add <A> <B>
```

## Stage Content

**`description`** (requirements):
- System context
- Functional requirements (EARS-style)
- Non-functional requirements
- Out of scope
- Acceptance scenarios

**`design`** (implementation):
- Current state
- Proposed approach
- Data flow
- Integration map
- Isolation & invariants

## Gate Content

Gates are **manual QA scripts**, not design docs:
- Environment assumptions
- Allowed real identifiers (if constrained)
- Exact steps/prompts
- Expected outcomes
- Evidence format

### Gate Quality Bar

- Runnable by human in 5–15 minutes
- Explicitly lists:
  - What to run (service/container)
  - What inputs to provide
  - What evidence to capture
- Pass/fail criteria (no vague "works")

## Stage Planning Rules

Each STAGE must:
- Deliver a shippable slice of user value
- Minimize changes to stable surfaces
- Have at least one GATE exercising new behavior end-to-end

### Common Progression

1. Cutover/visibility control (hide old, expose new)
2. Minimal functional path
3. Correctness + formatting
4. Optional retrieval/filtering
5. Edge cases + observability + hardening

## Template

Use the repo template:

```bash
cp .beads/templates/stage-gate-plan.md .tmp/beads/my-plan.md
# Edit the plan
bd --no-db create -f .tmp/beads/my-plan.md --json
```
