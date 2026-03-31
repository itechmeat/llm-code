---
name: coderabbit
description: "CodeRabbit AI code review. Covers CLI usage, .coderabbit.yaml configuration, supported linters/tools, PR commands, and triage workflow. Use when running AI-powered code reviews on pull requests or local changes, configuring review rules, or triaging CodeRabbit findings. Keywords: @coderabbitai, code review, CLI, .coderabbit.yaml."
metadata:
  version: "—"
  release_date: "2026-03-31"
---

# CodeRabbit

AI-powered code review for pull requests and local changes.

## Quick Navigation

| Task                          | Reference                                                   |
| ----------------------------- | ----------------------------------------------------------- |
| Install & run CLI             | [cli-usage.md](references/cli-usage.md)                     |
| Configure .coderabbit.yaml    | [configuration.md](references/configuration.md)             |
| Supported tools (40+ linters) | [tools.md](references/tools.md)                             |
| Git platform setup            | [platforms.md](references/platforms.md)                     |
| PR commands (@coderabbitai)   | [pr-commands.md](references/pr-commands.md)                 |
| Claude/Cursor/Codex workflow  | [agent-integration.md](references/agent-integration.md)     |
| Triage findings               | [triage.md](references/triage.md)                           |
| Fix single issue              | [fix.md](references/fix.md)                                 |
| Reporting & metrics           | [end-to-end-workflow.md](references/end-to-end-workflow.md) |
| End-to-end workflow           | [end-to-end-workflow.md](references/end-to-end-workflow.md) |
| Windows/WSL setup             | [windows-wsl.md](references/windows-wsl.md)                 |

## Prerequisites Check (MUST RUN BEFORE REVIEW)

Before running CodeRabbit CLI, verify ALL of the following:

```bash
# 1. CLI installed?
which coderabbit || echo "MISSING: install with: curl -fsSL https://cli.coderabbit.ai/install.sh | sh"

# 2. Authenticated?
coderabbit auth status 2>&1 | grep -q "Logged in" || echo "MISSING: run coderabbit auth login"

# 3. Git repo has at least one commit? (CRITICAL — CLI crashes with GitError on empty repos)
git rev-parse HEAD >/dev/null 2>&1 || echo "MISSING: repo has no commits — make at least one commit first"

# 4. Base branch exists? (CLI defaults to 'main')
git rev-parse main >/dev/null 2>&1 || echo "WARNING: 'main' branch not found — use --base <branch>"
```

**If any check fails, fix it before running the review. Do NOT proceed with a broken state.**

**Authentication failure rule:** If authentication check fails (step 2), the agent MUST:

1. Stop immediately — do not attempt to run the review
2. Notify the user that CodeRabbit CLI is not authenticated
3. Show the user the exact command to authenticate: `coderabbit auth login`
4. Wait for the user to complete authentication before retrying
5. Do NOT attempt to run `coderabbit auth login` on behalf of the user — it requires interactive browser redirect

## Quick Start

### Run Review

```bash
# AI agent workflow (most common) — note: 'review' subcommand is optional
coderabbit review --prompt-only --type uncommitted --no-color

# If base branch is not 'main' (e.g., master, develop):
coderabbit review --prompt-only --type uncommitted --base master --no-color

# Plain text output (human-readable)
coderabbit review --plain --type uncommitted --no-color
```

### Local Capture Script

Persist output to a file for later analysis:

```bash
# IMPORTANT: use absolute path to the skill's script directory
python3 ~/.claude/skills/coderabbit/scripts/run_coderabbit.py --output coderabbit-report.txt
```

Options:

- `--output` to choose a different file name (saved to `.code-review/` in repo root)
- `--timeout` to adjust the timeout in seconds (default: 1800)
- `--base` to specify base branch (default: auto-detect from git)

### PR Commands

```text
@coderabbitai review          # Incremental review
@coderabbitai full review     # Complete review
@coderabbitai simplify        # Apply targeted simplifications to changed files
@coderabbitai fix merge conflict  # Attempt automatic merge-conflict resolution
@coderabbitai pause           # Stop auto-reviews
@coderabbitai resume          # Resume auto-reviews
@coderabbitai resolve         # Mark comments resolved
```

## Severity Matrix

| Severity     | Action          | Examples                                          |
| ------------ | --------------- | ------------------------------------------------- |
| **CRITICAL** | Fix immediately | Security, data loss, tenant isolation             |
| **HIGH**     | Should fix      | Reliability, performance, architecture violations |
| **MEDIUM**   | Judgment call   | Maintainability, type safety (quick wins)         |
| **LOW**      | Skip            | Style/formatting, subjective nits                 |

## AI Agent Workflow Pattern

```text
Implement [feature] and then run CodeRabbit CLI in a background terminal.
Wait for it to complete, then read the report. Fix CRITICAL/HIGH issues. Ignore nits.
```

Step-by-step:

1. **Run prerequisites check** (see above) — fix any issues before proceeding
2. Detect base branch: `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null` or fall back to `main`/`master`
3. Run CLI in background: `coderabbit review --prompt-only --type uncommitted --base <branch> --no-color`
4. Reviews take **7-30+ minutes** — run in background (`run_in_background=true`)
5. Read output when process completes
6. Fix CRITICAL/HIGH findings, skip LOW
7. Limit to **2-3 review iterations** maximum

## Troubleshooting

### `[error] stopping cli` with no details

Run with `DEBUG=*` to see the actual error:

```bash
DEBUG=* coderabbit review --prompt-only --type uncommitted 2>&1 | grep -E "(ERROR|error|GitError)"
```

Check the log file:

```bash
ls -t ~/.coderabbit/logs/ | head -1 | xargs -I{} cat ~/.coderabbit/logs/{}
```

### Common errors

| Error                                      | Cause                       | Fix                                           |
| ------------------------------------------ | --------------------------- | --------------------------------------------- |
| `GitError` (no details)                    | No commits in repo          | Make at least one commit                      |
| `Failed to get commit SHA for branch main` | Base branch doesn't exist   | Use `--base master` or `--base <your-branch>` |
| `Raw mode is not supported`                | Interactive mode in non-TTY | Always use `--prompt-only` or `--plain`       |
| `[error] stopping cli` after auth          | Token expired               | Re-run `coderabbit auth login`                |
| CLI hangs / no output                      | Large changeset             | Use `--type uncommitted` to limit scope       |

### Check auth status

```bash
coderabbit auth status
```

## Linked Repositories (2026-02-18)

CodeRabbit can analyze linked repositories during PR review to catch cross-repo breakages (API/type/dependency drift).

- Configure linked repositories in Knowledge Base settings.
- As of 2026-03-11, Pro plans can link up to **2** repositories for Multi-Repo Analysis.
- Use this when changes in one repo affect contracts in another.
- Treat cross-repo findings as HIGH/CRITICAL when they indicate runtime incompatibility.

## Dashboard and Reporting (2026-03-12)

- Dashboard metrics are now split between **Git platform reviews** and **IDE/CLI reviews**.
- Reporting surfaces now include Git-platform pages like Knowledge Base, Pre-merge Checks, and Reporting, plus IDE/CLI pages like Summary, Organization Trends, and Data Metrics.
- Team filters are available across dashboards; use them when review volume or findings need to be separated by team rather than repository alone.

## Simplify Code (Open Beta, Pro) (2026-03-13)

- `@coderabbitai simplify` runs an agentic cleanup pass over the files changed in the PR.
- It focuses on extracting reusable helpers, simplifying conditionals, and removing redundancy while preserving behavior.
- CodeRabbit validates the result with the repository's existing test suite and can either open a follow-up PR or commit directly to the branch.
- Not available for fork PR direct-commit mode.

## Chat Access Control (GitHub Orgs) (2026-03-16)

- Use `chat.allow_non_org_members: false` in `.coderabbit.yaml` when PR comment chat must stay limited to organization members.
- This affects comment-thread interaction only; automatic PR review behavior is unchanged.
- Default remains `true`, so public-repo chat stays open unless you opt out.

## Resolve Merge Conflicts (Open Beta, Pro) (2026-03-17)

- CodeRabbit can detect merge conflicts during PR review and offer one-click or comment-triggered resolution.
- Trigger with `@coderabbitai fix merge conflict` or the Walkthrough checkbox on GitHub.
- It commits a proper merge commit when successful, but declines if the resolution is ambiguous or touches security-critical logic such as auth, encryption, secrets, or access control.
- If any conflicted file is declined, the whole auto-resolution attempt is aborted and no partial commit is created.

## Betterleaks (replaces Gitleaks) (2026-03-19)

- Secret scanning now uses Betterleaks (improved detection over Gitleaks).
- The `gitleaks` config key in `.coderabbit.yaml` now controls Betterleaks.
- Default remains enabled; existing secret scanning continues without changes.

## Slop Detection (2026-03-24)

- Automatically detects low-quality AI-generated PRs on public GitHub repositories.
- Flagged in the PR Walkthrough comment.
- Opt-in label tagging:

```yaml
reviews:
  slop_detection:
    enabled: true # default
    label: "slop" # optional label
```

## Bitbucket Data Center (2026-03-24)

- Full support for Bitbucket Data Center as a Git platform.
- OAuth 2.0, automated webhook configuration, and full PR review capabilities.

## Audit Logs (2026-03-25)

- Tamper-resistant audit log for every administrative action across the workspace.
- Covers seat assignments/removals, role changes, org/repo changes, subscription events, config updates, and API key operations.
- Accessible in Settings UI or via REST API for automated export.

## CLI Agent Mode (2026-03-31)

- `coderabbit review --agent` outputs results in structured JSON format for Skills and agent integrations.

## Custom Finishing Touch Recipes (Early Access) (2026-02-23)

Define reusable, named "finishing touch" recipes that apply agentic code changes to your PR.

See [configuration.md](references/configuration.md) for a minimal example.

## Minimal Configuration

```yaml
# .coderabbit.yaml
language: en-US
reviews:
  profile: chill
  high_level_summary: true
  tools:
    gitleaks:
      enabled: true
    ruff:
      enabled: true
```

## Critical Prohibitions

- Do not introduce fallbacks, mocks, or stubs in production code
- Do not broaden scope beyond what CodeRabbit flagged
- Do not "fix" style nits handled by formatters/linters
- Do not ignore CRITICAL findings; escalate if unclear
- Stop and resolve CLI errors (auth/network) before fixing code
- **Do not run CLI on a repo with no commits — it will silently crash**

## Links

- [Documentation](https://docs.coderabbit.ai/)
- [Changelog](https://docs.coderabbit.ai/changelog)
- [GitHub](https://github.com/coderabbitai/coderabbit)
- [Schema](https://coderabbit.ai/integrations/schema.v2.json)

## Templates

- [coderabbit.minimal.yaml](assets/coderabbit.minimal.yaml) — Minimal configuration
- [coderabbit.full.yaml](assets/coderabbit.full.yaml) — Full example with all options
- [agent-prompts.md](assets/agent-prompts.md) — Ready-to-use AI agent prompts
