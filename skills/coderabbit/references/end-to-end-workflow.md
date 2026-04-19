# CodeRabbit End-to-End Workflow

Complete workflow from running a review to implementing fixes.

## When to use

- You want a structured, pre-PR review to catch correctness/security issues early.
- You want to use CodeRabbit output as an input for a focused, minimal-fix workflow.

## Inputs

- Target scope: repo root or a subfolder (e.g. `src/`).
- CodeRabbit output (prompt-only) for triage.

If the team is close to PR review limits, confirm whether the Usage-based add-on is enabled before assuming PR/CLI reviews will continue past the plan cap.

## Process

1. Run CodeRabbit (prompt-only) for the relevant scope.
2. If the review fails (rate limit/auth/network), stop and resolve the failure first.
3. Triage findings with `triage.md`.
4. If the PR needs agentic cleanup, optionally trigger `@coderabbitai simplify` and review the produced branch/commit before touching code manually.
5. If the PR is blocked by merge conflicts, use the merge-conflict path below instead of manual triage.
6. Implement fixes with `fix.md` (one issue at a time).
7. Verify quality gates (project checks, tests).

## Merge Conflict Resolution Path (2026-03-17)

Use this when CodeRabbit detects merge conflicts in a PR or merge request.

Trigger options:

- `@coderabbitai fix merge conflict`
- **Resolve merge conflicts** checkbox in the GitHub Walkthrough

Operational behavior:

- CodeRabbit simulates the merge in a sandbox, analyzes the intent of both sides, edits the repo, and validates the result.
- On success it creates a proper merge commit with two parents.
- If the branch changes during processing, the run is aborted and must be retried.
- If any file is ambiguous or security-sensitive, the entire attempt is declined and no partial commit is created.

Treat these conflict classes as manual-review territory even if CodeRabbit offers the action:

- authentication or authorization logic
- encryption, secrets handling, or access control
- mutually exclusive architectural decisions that need product judgment

## Critical prohibitions

- Do not introduce fallbacks, mocks, or stubs in production code.
- Do not "fix" style nits if tooling already covers them.
- Do not broaden the scope beyond the reviewed findings.

## Reporting & Metrics

### Usage-based review continuity (2026-04-08)

- PR reviews and CLI-triggered reviews follow the same usage-based add-on behavior when a plan limit is exceeded.
- When enabled, only the overflow is billed; the normal usage remains on-plan.
- Treat sudden review stoppage after plan exhaustion as an account/billing configuration issue before debugging the CLI.

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
