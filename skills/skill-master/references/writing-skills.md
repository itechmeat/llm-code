# Writing Effective Skills

Source: The Complete Guide to Building Skills for Claude (Anthropic)

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?" Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

- **High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.
- **Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.
- **Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

## Use Case Categories

Before writing, identify which category your skill falls into — it shapes structure and techniques.

**Category 1: Document & Asset Creation**
Creating consistent, high-quality output: documents, designs, code, presentations.
Key techniques: embedded style guides, template structures, quality checklists, no external tools required.

**Category 2: Workflow Automation**
Multi-step processes with consistent methodology, possibly coordinating multiple services.
Key techniques: step-by-step workflow with validation gates, iterative refinement loops, built-in review suggestions.

**Category 3: MCP Enhancement**
Guidance layer on top of MCP tool access — turns raw tool calls into reliable workflows.
Key techniques: sequencing MCP calls, embedding domain expertise, handling common MCP errors.

## Writing the Description Field

The description is how Claude decides whether to load your skill. It appears in the system prompt and is the **first level of progressive disclosure** — loaded always, even when the skill body isn't.

**Formula:**

```
[What it does] + [When to use it] + [Key capabilities / trigger phrases]
```

**Good examples (include explicit "Use when..." triggers):**

```yaml
description: Analyzes Figma design files and generates developer handoff docs. Use when user uploads .fig files or asks for "design specs", "component documentation", or "design-to-code handoff".

description: Manages Linear sprint planning and task creation. Use when user mentions "sprint", "Linear tasks", "project planning", or asks to "create tickets".
```

**Bad examples:**

```yaml
description: Helps with projects.                           # Too vague
description: Creates sophisticated documentation systems.   # Missing triggers
description: Implements the Project entity model.           # Too technical, no triggers
```

**Rules:**

- Under 1024 chars (target 80-150)
- MUST include both WHAT it does and WHEN to use it (trigger phrases)
- Include phrases users would actually say, e.g. "help me plan this sprint"
- No XML angle brackets `< >`
- No "claude" or "anthropic" in the name (reserved)
- Mention file types if relevant (`.fig`, `.pdf`, `.csv`)

**Debugging undertriggering:** Ask Claude: "When would you use the [skill name] skill?" — Claude will quote the description back. Adjust based on what's missing.

**Fixing overtriggering:** Add negative triggers:

```yaml
description: Advanced CSV data analysis for statistical modeling. Use for regression, clustering. Do NOT use for simple data exploration.
```

## Writing Instructions in SKILL.md

### Recommended Structure

```markdown
# Skill Name

## Step 1: [First Major Step]

Clear explanation of what happens.
Example: `python scripts/fetch_data.py --input FILE`
Expected output: [describe what success looks like]

## Step 2: ...

## Examples

### Example 1: [common scenario]

User says: "..."
Actions: [numbered list]
Result: [what happens]

## Common Issues

### Error: [message]

Cause: [why]
Solution: [how to fix]
```

### Be Specific and Actionable

❌ Bad:

```
Validate the data before proceeding.
```

✅ Good:

```
Run `python scripts/validate.py --input {filename}`.
If validation fails, common issues:
- Missing required fields → add them to the CSV
- Invalid date formats → use YYYY-MM-DD
```

### Reference Bundled Resources Clearly

```markdown
Before writing queries, consult `references/api-patterns.md` for:

- Rate limiting guidance
- Pagination patterns
- Error codes
```

**Important guidelines for references:**

- **Avoid deeply nested references** — Keep references one level deep from `SKILL.md`. All reference files should link directly from `SKILL.md`.
- **Structure longer reference files** — For files longer than 100 lines, include a table of contents at the top so Claude can see the full scope when previewing.

### Use Scripts for Critical Validations

For critical checks, prefer a bundled script over language instructions — code is deterministic, language interpretation isn't:

```markdown
## Validation

Run `python scripts/validate.py` before proceeding.
Script checks: required fields, date formats, referential integrity.
```

## Workflow Patterns

For complex tasks, break operations into clear, sequential steps or conditional branches. See `references/workflows.md` for detailed patterns on structuring multi-step processes, tool coordination, and iterative refinement.
