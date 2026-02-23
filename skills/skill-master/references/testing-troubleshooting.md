# Testing and Troubleshooting Skills

Source: The Complete Guide to Building Skills for Claude (Anthropic)

## Testing Approach

### Pro Tip: Iterate on One Task First

Iterate on a single challenging task until Claude succeeds, then extract the winning approach into a skill. This gives faster signal than broad testing. Once working, expand to multiple cases.

### 1. Triggering Tests

Goal: ensure skill loads at the right times.

```
Should trigger:
- "Help me set up a new [tool] workspace"
- "I need to create a project in [tool]"
- "[tool]-style paraphrase of the task"

Should NOT trigger:
- "What's the weather today?"
- Unrelated tool requests
```

Run 10–20 test queries. Track how often the skill loads automatically vs. requires explicit invocation. Target: 90% of relevant queries.

### 2. Functional Tests

Goal: verify the skill produces correct outputs.

```
Test: [scenario name]
Given: [inputs]
When: skill executes
Then:
  - [expected output 1]
  - [expected output 2]
  - No errors
```

Check: valid outputs generated, API calls succeed, error handling works, edge cases covered.

### 3. Performance Comparison

Compare the same task with and without the skill:

| Metric                  | Without skill | With skill |
| ----------------------- | ------------- | ---------- |
| Back-and-forth messages | many          | minimal    |
| Failed calls            | several       | zero       |
| Tokens consumed         | high          | lower      |

## Iteration Signals

**Undertriggering** (skill doesn't load when it should):

- Add more specific trigger phrases to description
- Include technical terms users might say
- Add "Use when user asks to [specific action]"

**Overtriggering** (skill loads for unrelated queries):

- Add negative triggers: "Do NOT use for..."
- Be more specific about the scope
- Clarify with: "Use specifically for X, not for general Y queries"

**Execution issues** (skill loads but instructions not followed):

- Keep instructions concise — use bullets and numbered lists
- Put critical instructions at the top
- Use `## CRITICAL` or `## IMPORTANT` headers for must-follow rules
- Move detailed reference to `references/` files
- For critical validations, use a script instead of language instructions

## Troubleshooting: Skill Won't Upload

**Error: "Could not find SKILL.md in uploaded folder"**

- Rename to exactly `SKILL.md` (case-sensitive)
- No variations: `SKILL.MD`, `skill.md` are rejected

**Error: "Invalid frontmatter"**

```yaml
# Wrong — missing --- delimiters
name: my-skill
description: Does things

# Wrong — unclosed quotes
description: "Does things

# Correct
---
name: my-skill
description: Does things.
---
```

**Error: "Invalid skill name"**

```yaml
# Wrong
name: My Cool Skill   # spaces and capitals

# Correct
name: my-cool-skill
```

## Troubleshooting: Skill Doesn't Trigger

The description is too generic or missing trigger phrases.

Quick checklist:

- Is the description too generic? ("Helps with projects" won't work)
- Does it include phrases users would actually say?
- Does it mention relevant file types if applicable?

Fix: revise the description. See `references/writing-skills.md` for good/bad examples.

Debug: ask Claude "When would you use the [skill name] skill?" — it will quote the description back.

## Troubleshooting: Instructions Not Followed

1. **Instructions too verbose** — move details to `references/`, keep SKILL.md focused
2. **Critical info buried** — put key rules at the top, use `## CRITICAL` headers
3. **Ambiguous language** — replace vague phrases with specific commands and expected outputs
4. **Model "laziness"** — add explicit performance notes (more effective in user prompts than in SKILL.md):
   ```
   - Take your time; quality over speed
   - Do not skip validation steps
   ```

## Troubleshooting: Large Context / Slow Responses

Causes: SKILL.md too large, all content loaded instead of progressive disclosure.

Solutions:

- Move detailed docs to `references/` and link to them from SKILL.md
- Keep SKILL.md under 500 lines (Anthropic guide recommends under 5,000 words)
- Audit which references are actually needed and trim unused ones

## Validation Checklist

_Pro Tip: You can use the `skill-creator` skill (available in Claude.ai or Claude Code) to review your skill and suggest improvements before finalizing._

**Before starting:**

- [ ] Identified 2-3 concrete use cases
- [ ] Planned folder structure

**During development:**

- [ ] Folder named in kebab-case
- [ ] `SKILL.md` exists (exact spelling, case-sensitive)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name` is kebab-case, no spaces, no capitals, matches folder name
- [ ] `description` includes WHAT and WHEN (trigger phrases)
- [ ] No XML angle brackets `< >` anywhere
- [ ] Instructions are specific and actionable (not vague)
- [ ] Error handling included
- [ ] References clearly linked

**After creating:**

- [ ] Test triggering on obvious tasks
- [ ] Test triggering on paraphrased requests
- [ ] Verify it does NOT trigger on unrelated topics
- [ ] Run functional tests
