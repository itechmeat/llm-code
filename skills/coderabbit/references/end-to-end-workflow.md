# CodeRabbit End-to-End Workflow

Complete workflow from running a review to implementing fixes.

## When to use

- You want a structured, pre-PR review to catch correctness/security issues early.
- You want to use CodeRabbit output as an input for a focused, minimal-fix workflow.

## Inputs

- Target scope: repo root or a subfolder (e.g. `src/`).
- CodeRabbit output (prompt-only) for triage.

## Process

1. Run CodeRabbit (prompt-only) for the relevant scope.
2. If the review fails (rate limit/auth/network), stop and resolve the failure first.
3. Triage findings with `triage.md`.
4. Implement fixes with `fix.md` (one issue at a time).
5. Verify quality gates (project checks, tests).

## Critical prohibitions

- Do not introduce fallbacks, mocks, or stubs in production code.
- Do not "fix" style nits if tooling already covers them.
- Do not broaden the scope beyond the reviewed findings.

## Related references

- CLI usage: `cli-usage.md`
- Triage workflow: `triage.md`
- Single issue fix: `fix.md`
