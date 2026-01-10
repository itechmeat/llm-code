# Agent prompt template (triage + fixes)

Use this as a starting point when dispatching an implementation-focused agent to fix CodeRabbit findings.

```yaml
Task:
  subagent_type: "tech-backend"
  description: "Fix CodeRabbit issues"
  prompt: |
    INTELLIGENT TRIAGE: Balance code quality with pragmatism.

    SEVERITY MATRIX:
    - CRITICAL (FIX IMMEDIATELY): Security, data loss/corruption, tenant isolation violations, fallbacks/mocks/stubs
    - HIGH (SHOULD FIX): Reliability, performance, architecture violations
    - MEDIUM (JUDGMENT CALL): Maintainability, type safety (fix if quick win)
    - LOW (SKIP): Style/formatting and subjective nits

    Constraints:
    - No fallbacks/mocks/stubs in production code
    - Keep changes minimal and root-cause oriented
    - Follow repository instructions and skills

    CodeRabbit output:
    <paste prompt-only output here>

    For each issue:
    1) Categorize severity
    2) Decide FIX / DEFER / SKIP
    3) Implement fixes for CRITICAL first
    4) Add explicit TODO for deferred HIGH/MEDIUM
    5) Verify with project checks/tests

    Provide a structured triage report.
```
