# GitHub PR Commands (@coderabbitai)

All commands use `@coderabbitai` mention in PR comments.

## Review Control

| Command                     | Description                             |
| --------------------------- | --------------------------------------- |
| `@coderabbitai review`      | Incremental review of new changes only  |
| `@coderabbitai full review` | Complete review from scratch            |
| `@coderabbitai pause`       | Stop automatic reviews                  |
| `@coderabbitai resume`      | Restart automatic reviews               |
| `@coderabbitai ignore`      | Disable reviews (add to PR description) |
| `@coderabbitai resolve`     | Mark all CodeRabbit comments resolved   |

## Information Commands

| Command                                   | Description                          |
| ----------------------------------------- | ------------------------------------ |
| `@coderabbitai summary`                   | Regenerate PR summary in description |
| `@coderabbitai generate sequence diagram` | Post sequence diagram of PR history  |
| `@coderabbitai configuration`             | Show current settings                |
| `@coderabbitai help`                      | Quick-reference guide                |

## Code Generation

| Command                             | Description                          |
| ----------------------------------- | ------------------------------------ |
| `@coderabbitai generate docstrings` | Generate documentation for functions |
| `@coderabbitai generate unit tests` | Generate test coverage               |

## Finishing Touches

| Command                            | Description                                                           |
| ---------------------------------- | --------------------------------------------------------------------- |
| `@coderabbitai simplify`           | Simplify the changed files in the PR while preserving behavior        |
| `@coderabbitai fix merge conflict` | Attempt automatic merge-conflict resolution and commit a merge result |

## Chat Interaction

Ask questions about code changes:

```text
@coderabbitai Why did you suggest using a factory pattern here?
```

```text
@coderabbitai Can you explain the security implications of this change?
```

## Usage Notes

- `@coderabbitai ignore` must be in PR description (not comments)
- `@coderabbitai resolve` marks ALL comments as resolved
- CodeRabbit learns from your feedback over time
- Chat responses consider full repository context
- `@coderabbitai simplify` is an Open Beta Pro feature and may take up to 20 minutes on large PRs
- `@coderabbitai fix merge conflict` aborts without a commit when any conflicted file is too ambiguous or security-sensitive for safe automation
