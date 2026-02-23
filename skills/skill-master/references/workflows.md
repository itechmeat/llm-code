# Workflow Patterns

Source: The Complete Guide to Building Skills for Claude (Anthropic)

When building skills, especially those that automate multi-step processes or enhance MCP tools, structuring the workflow correctly is critical.

## Problem-First vs. Tool-First Framing

Before choosing a pattern, decide on the framing:

- **Problem-first**: User describes an outcome → skill orchestrates the right tool calls. Example: "I need to set up a project workspace"
- **Tool-first**: User has a tool connected → skill teaches the optimal workflows. Example: "I have Notion MCP connected"

Most skills lean one direction. Choose the framing that fits your use case before writing instructions.

## Core Workflow Patterns

Choose the pattern that best fits your use case.

### Pattern 1: Sequential Workflow Orchestration

**Use when:** users need multi-step processes in a specific order.
**Key techniques:** explicit step ordering, dependencies between steps, validation at each stage, rollback instructions.

_Tip: It is often helpful to give Claude an overview of the process towards the beginning of `SKILL.md`:_

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

### Pattern 2: Conditional Workflows (Context-Aware Tool Selection)

**Use when:** same outcome, different tools depending on context, or tasks with branching logic.
**Key techniques:** decision tree with clear criteria, fallback options, explain the choice to user.

_Tip: Guide Claude through decision points explicitly:_

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```

### Pattern 3: Multi-Service Coordination

**Use when:** workflow spans multiple services (e.g., Figma → Drive → Linear → Slack).
**Key techniques:** clear phase separation, data passing between services, validation before moving to next phase.

### Pattern 4: Iterative Refinement

**Use when:** output quality improves with iteration (e.g., report generation).
**Key techniques:** generate draft → run validation script → fix issues → re-validate → repeat until threshold met.

### Pattern 5: Domain-Specific Intelligence

**Use when:** skill adds specialized knowledge beyond tool access (compliance, security, finance).
**Key techniques:** domain logic before action, comprehensive audit trail, clear governance rules.

## When to use `references/workflows.md`

If your skill contains complex, multi-step processes, conditional logic, or orchestrates multiple tools, you should extract these patterns into a dedicated `references/workflows.md` file.

This keeps `SKILL.md` lean (focused on triggers and high-level navigation) while providing Claude with detailed procedural knowledge when it actually needs to execute the workflow.
