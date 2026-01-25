# CodeRabbit Fix (Single Issue)

Implement a single CodeRabbit issue fix with minimal scope, root-cause focus, and mandatory verification.

## When to use

- You have one triaged issue and you want to implement a focused fix.
- You want to avoid scope creep and keep diffs minimal.

## Inputs

- One issue from triage: `file`, `line` (optional), `issue`, `suggestion`, `severity`, `constraints`.

## Process

1. Read the relevant code section (include a small context window before/after).
2. Confirm the root cause (do not blindly apply the suggestion).
3. Implement the smallest correct fix that addresses the cause.
4. Preserve existing patterns and public APIs unless the issue requires a change.
5. Add or update verification:
   - Run the narrowest checks/tests first.
   - Then run broader checks if needed.

## Verification (minimum)

- Run the workspace checker (`code_checker`) after edits.
- Run the most relevant tests for the changed area (follow repo test instructions).

## Fixing guidelines

- Security/correctness: prefer explicit validation and clear error handling.
- Multi-tenant systems: ensure tenant context/isolation rules are respected (if applicable).
- Async code: avoid blocking I/O and ensure timeouts for network calls.
- Types: add precise type hints when it reduces risk; avoid "Any" unless justified.

## Report format

```text
Issue: <summary>
Severity: <CRITICAL|HIGH|MEDIUM|LOW>
Decision: FIXED
Files:
- path/to/file.py
Verification:
- code_checker: PASS
- tests: <what ran>
Notes: <trade-offs, if any>
```

## Critical prohibitions

- Do not introduce silent fallbacks for required identifiers.
- Do not add mocks/stubs/fake implementations to production code.
- Do not refactor unrelated code while fixing a single issue.
