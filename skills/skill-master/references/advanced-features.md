# Advanced Skill Features

Extended features for Claude Code and other advanced agent environments.

## Context Forking (Subagents)

Run a skill in isolation with `context: fork`. The skill becomes the prompt for a subagent without conversation history.

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

### Agent Types

| Agent | Best For |
|-------|----------|
| `Explore` | Research, code analysis, finding patterns |
| `Plan` | Creating implementation plans, breaking down tasks |

### When to Use Context Fork

- Tasks that benefit from fresh context
- Research that shouldn't pollute main conversation
- Long-running analysis that might exceed context limits
- Tasks where isolation prevents interference

## Allowed Tools

Restrict which tools a skill can use:

```yaml
---
name: safe-reader
description: Read files without making changes
allowed-tools: Read Grep Glob
---
```

### Common Tool Restrictions

| Use Case | Allowed Tools |
|----------|---------------|
| Read-only analysis | `Read Grep Glob` |
| Code review | `Read Grep Glob Write` |
| Git operations | `Bash(git:*)` |
| Python scripts | `Bash(python:*)` |

### Tool Syntax

- Simple: `Read Grep Glob`
- With patterns: `Bash(git:*) Bash(npm:*)`
- All bash: `Bash(*)`

## Invocation Control

### Manual-Only Skills

For workflows with side effects that users should control:

```yaml
---
name: deploy
description: Deploy to production
disable-model-invocation: true
---

Deploy $ARGUMENTS to production:
1. Run test suite
2. Build application
3. Push to deployment target
```

### Background Knowledge Skills

For reference material that shouldn't appear in `/` menu:

```yaml
---
name: api-conventions
description: API design patterns for this codebase
user-invocable: false
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
```

## Dynamic Context

Inject live data using `!`command`` syntax:

```yaml
---
name: pr-review
description: Review pull request with current data
context: fork
agent: Explore
allowed-tools: Bash(gh:*)
---

## Current PR State
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Review Task
Analyze this PR for issues...
```

### How It Works

1. Commands execute **before** the prompt is sent
2. Output replaces the `!`command`` placeholder
3. Agent receives fully-rendered content with real data

### Use Cases

- Fetching current git state
- Getting issue/PR details
- Reading dynamic configuration
- Gathering system information

## Argument Hints

Show users what arguments are expected:

```yaml
---
name: analyze-file
description: Analyze a specific file
argument-hint: <filename> [--verbose]
---
```

Appears in autocomplete as: `/analyze-file <filename> [--verbose]`

## Model Override

Force a specific model for a skill:

```yaml
---
name: complex-analysis
description: Deep analysis requiring advanced reasoning
model: claude-3-opus-20240229
---
```

## Extended Thinking

Include "ultrathink" anywhere in skill content to enable extended thinking mode.

## Hooks

Scope hooks to skill lifecycle:

```yaml
---
name: my-skill
hooks:
  on-invoke:
    - command: echo "Skill invoked"
  on-complete:
    - command: echo "Skill completed"
---
```

See agent documentation for full hooks configuration.

## Examples Structure

Include `examples/` folder for sample outputs:

```
my-skill/
├── SKILL.md
└── examples/
    ├── basic-output.md     # Simple example
    ├── complex-output.md   # Advanced example
    └── edge-case.md        # Handling edge cases
```

Reference in SKILL.md:
```markdown
See `examples/basic-output.md` for expected format.
```
