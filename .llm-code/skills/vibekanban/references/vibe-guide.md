# Vibe Guide

Best practices for working with AI coding agents.

## Planning

### Always Plan First

Ask agent: "come up with a plan, confirm with me before making changes"

### Plan More, Review Less

5 min planning saves 10 min reviewing. Plans faster to judge than diffs.

### Planning Sets the Shape

Agents optimize for minimal edits. Once code exists, changes patch rather than rethink. Plan picks the right shape before code hardens.

### Re-plan When Needed

If making many plan changes: start new session, summarize learnings, let agent begin fresh.

```
Knowing what you know please write a new high level plan:
- No code
- Just sentences
- Mention files to look at, at the bottom of your plan
```

## Async Work

### Use YOLO Mode

Async only works without constant approvals. Use agent's YOLO/dangerously-skip-permissions mode.

### Biggest Model is Fastest

Smaller models make more mistakes, need more intervention. With 2+ parallel tasks, big model is faster. Metric: how often you intervene.

### Set Up Codebase for QA

Make changes verifiable with dev/test commands. Most changes should end with "tests pass", not "can you try this?"

### Solve Dev Servers

Agents bad at starting/cleaning up servers → port conflicts. Use fixed port or Dev Manager MCP.

### Add Dummy Data

Make project runnable offline with seed data. Enables parallel agents, avoids database conflicts.

## Combating Laziness

### No Backwards Compatibility

Add to system prompt:

> We want the simplest change possible. We don't care about migration. Code readability matters most.

### Disable Disabling Lint Rules

Agents love `eslint-disable-next-line`. Ban with `eslint-comments/no-restricted-disable`.

## Frontend Tips

### Separate Presentation from Logic

Keep leaf components presentational. Business logic in parents. Avoids Frankenstein components.

```json
{
  "no-restricted-syntax": [
    "error",
    {
      "selector": "CallExpression[callee.name=\"useState\"]",
      "message": "View components should not manage state."
    }
  ]
}
```

### Restrict Tailwind

Agents add custom colors/spacing everywhere. Use ESLint to enforce allowed utility classes.

### Figma MCP

Good for first pass at presentational components. Specify Tailwind config paths and icon library.
