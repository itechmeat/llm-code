# CodeRabbit Triage Workflow

Turn CodeRabbit output into a severity-ranked plan: fix/defer/skip with clear rationale.

## When to use

- You have CodeRabbit output (preferably `--prompt-only`) and need a structured fix plan.
- You want to balance pragmatism (minimal diffs) with safety (security/correctness first).

## Inputs

- Full CodeRabbit output (do not paraphrase; keep exact wording where possible).
- Repository context: applicable instructions and skills (e.g., architecture, multi-tenancy, async rules).

## Process

1. Extract issues into a list with: `file`, `line` (if provided), `issue`, `suggestion`.
2. Classify severity:
   - **CRITICAL**: security, data loss/corruption, tenant isolation violations, broken error handling, missing timeouts.
   - **HIGH**: reliability/performance regressions, transaction/session misuse, architectural violations.
   - **MEDIUM**: type safety, refactors, maintainability improvements.
   - **LOW**: formatting, naming preferences, pure style nits.

Cross-repo note:

- If linked-repository analysis flags contract drift across repos, default to **HIGH**.
- Escalate to **CRITICAL** if breakage can cause production runtime failures.

3. Decide per issue:
   - **FIX** if it materially improves safety/correctness or is a clear quick win.
   - **DEFER** if valuable but not appropriate now (add an explicit TODO with reason).
   - **SKIP** if subjective/outdated or handled by tooling.
4. Produce a triage report and a task plan (one task per issue).

## Documentation for deferred issues

When deferring HIGH/MEDIUM issues, add a focused TODO that includes:

- Issue summary
- Reason for deferral
- Suggested follow-up

## Expected output (template)

```text
CRITICAL: N
HIGH: N
MEDIUM: N
LOW: N

Issue 1
- Severity: CRITICAL
- Decision: FIX
- Location: path/to/file.py:123
- Reason: ...
- Verification: ...

Issue 2
- Severity: MEDIUM
- Decision: DEFER
- Location: ...
- Reason: ...
- Follow-up: TODO(...)
```

## Critical prohibitions

- Do not invent issues.
- Do not broaden scope beyond what CodeRabbit flagged.
- Do not recommend adding fallbacks/mocks/stubs to production code.
