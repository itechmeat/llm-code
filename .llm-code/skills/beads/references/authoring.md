# Issue Authoring (Spec-Grade Quality)

Write Beads issues that are implementable without guesswork.

## Quality Triangle

Every issue must answer:
- **What must be true?** (`description` = contract/requirements)
- **How do we implement it here?** (`design` = approach + integration map)
- **How do we prove it works?** (`acceptance_criteria` = pass/fail)

## Minimum Content Bar

| Field | Must Include |
|-------|--------------|
| **Contract** | Inputs/outputs, schemas, defaults, limits |
| **Decision closure** | No unresolved "pick one" behaviors |
| **Integration map** | Concrete files/modules/symbols |
| **Acceptance** | Executable pass/fail checklist |
| **Constraints** | Hard rules, allowed identifiers for QA |

## Description (Requirements)

### Recommended Structure

1. **System context**: runtime surface, tenant/bot scope, invariants
2. **Functional requirements**: EARS-style with `REQ-###` numbering
3. **Non-functional requirements**: only if measurable
4. **Out of scope**: explicit non-goals
5. **Acceptance scenarios**: 3–6 Given/When/Then

### EARS Writing Rules

Each requirement must be testable and unambiguous:
- **When** `<trigger>`, the system shall `<behavior>`.
- **While** `<state>`, the system shall `<behavior>`.
- **If** `<condition>`, then the system shall `<behavior>`.

Do not leave behavioral forks (e.g., "reject or return empty — pick one").

### Input Contract Checklist

- Field list + types (Pydantic/JSON schema)
- Defaulting rules
- Validation constraints (ranges, max window, enums)
- Time semantics (timezone source, absolute vs relative)
- Tenant scoping fields
- Invalid input behavior and signaling model

### Output Contract Checklist

- Field list + types
- Ordering guarantees
- Empty result signaling (`empty_reason` values)
- Debug block (flag-controlled)
- Error signaling model

## Design (Implementation Plan)

### Recommended Structure

1. Current state (what exists today)
2. Proposed approach (decisions and rationale)
3. Data flow (bullets or Mermaid diagram)
4. Integration map (files/modules/symbols)
5. Isolation & invariants (RLS, required identifiers)
6. Risks & mitigations

### Architecture Decomposition

Make component boundaries explicit:
- API/handler layer
- Tool/agent layer
- Service layer
- Data access layer (RLS enforcement)
- External deps (RAG, cache)

For each component: public interface, failure modes, observability.

### Cutover Checklist (when replacing legacy)

- Tool catalog/registry: remove legacy tool visibility
- Tool exports: ensure legacy not re-exported
- Runtime toolset: ensure legacy not registered
- References: update prompts/docs

## Acceptance Criteria

### Scenario Template

```text
Scenario A (Happy path)
- Given <precondition>
- When <trigger/input>
- Then <observable outputs>

Scenario B (Empty result)
- Given <no matching data>
- When <trigger/input>
- Then <empty_reason + no hallucination>

Scenario C (Constraints/limits)
- Given <invalid window / out-of-range>
- When <trigger/input>
- Then <exact behavior and signaling>
```

### Multi-Tenant Isolation Scenario (mandatory when applicable)

```text
- Given tenant A and tenant B have different data
- When tenant A invokes the feature
- Then only tenant A data is returned
```

Require proof in `design`: where tenant context is derived and set.

## NFRs (Non-Functional Requirements)

Only include if measurable. Use prefixes:
- **PERF-###**: Latency/size budgets
- **QUAL-###**: Quality targets with measurement method

Example:
- PERF-001: When retrieval is executed, p95 latency shall be < 500ms.
- QUAL-001: Grouping correctness shall achieve 95% measured by manual sampling.

## Task Authoring

Decompose each STAGE into 3–8 atomic TASKs:
- Schemas/contract
- Data access (queries, RLS)
- Business logic
- Formatting/output
- Observability
- Tests

Each TASK must name concrete touch points and what verification it adds.
