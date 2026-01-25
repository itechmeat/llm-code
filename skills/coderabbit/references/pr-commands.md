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
