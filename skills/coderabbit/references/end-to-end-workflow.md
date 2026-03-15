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

## Reporting & Metrics

### Dashboard Structure (2026-03-12)

CodeRabbit dashboards are now split into two top-level review surfaces:

- **Git platform reviews** for GitHub/GitLab/Azure DevOps/Bitbucket pull-request review metrics.
- **IDE/CLI reviews** for local or editor-driven reviews through extensions and the CLI.

Use the dashboard split to avoid mixing PR review trends with IDE/CLI review adoption data.

Team filters are available across the dashboards, which is useful when adoption or findings need to be compared across teams instead of across the entire organization.

### Data Export (Dashboard)

Use **Data Export** to download per‑PR review metrics as CSV for a selected date range (last 7/30/90 days or a custom range within the last year). The export includes fields like complexity scores, review times, and comment breakdowns by severity/category.

Dashboard drill-down (2026-02-24):

- You can drill into severity/category metrics to open a Comment Details view (useful for audits and debugging false positives).

Additional Git-platform dashboard pages (2026-03-12):

- **Knowledge Base**: review how Learnings and MCP integrations affect review outcomes.
- **Pre-merge Checks**: monitor pass/fail results for built-in and custom gates.
- **Reporting**: track report delivery volume and channel distribution.

Additional IDE/CLI dashboard pages (2026-03-12):

- **Summary**: overall IDE/CLI review activity and findings.
- **Organization Trends**: week-over-week adoption and findings by tool/severity.
- **Data Metrics**: per-user IDE/CLI review breakdown.

### Review Metrics API

REST API for programmatic access to review metrics. Query by date range, filter by repository or user, and retrieve results in JSON or CSV.

## Related references

- CLI usage: `cli-usage.md`
- Triage workflow: `triage.md`
- Single issue fix: `fix.md`
