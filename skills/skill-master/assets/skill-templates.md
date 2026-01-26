# Skill Templates

Ready-to-use templates for creating Agent Skills.

## SKILL.md Template

```markdown
---
name: <skill-name>
description: "[TODO] Describe what this skill does and when to use it. Include trigger keywords."
---

# <Skill Title>

## When to Use

- [TODO] Situations and triggers

## Quick Navigation

- Topic A: `references/topic-a.md`
- Topic B: `references/topic-b.md`

## Goal

[TODO] 1-3 sentences describing what this skill enables.

## Steps / Recipes

1. [TODO]

## Critical Prohibitions

- [TODO]

## Definition of Done

- [TODO]

## Links

- [TODO] External references
```

## SKILL.md Template (Router Style)

For skills with extensive reference material:

```markdown
---
name: <skill-name>
description: "[Purpose] + [Keywords for discovery]"
---

# <Skill Title> (Skill Router)

This file is intentionally short. Based on your situation, open the right note under `references/`.

## Start Here

- New to <topic>? Read: `references/concepts.md`
- Quick setup? Read: `references/quickstart.md`
- Integration? Read: `references/api.md`

## Choose by Situation

### Data Modeling

- What goes where? Read: `references/modeling.md`

### Operations

- Deployment: `references/deployment.md`
- Troubleshooting: `references/troubleshooting.md`

## Critical Prohibitions

- [Key prohibitions that apply broadly]

## Links

- Official docs: <URL>
```

## Reference Note Template

```markdown
# <Topic Title>

Source: <URL or "Internal">

## What This Covers

- 1-3 bullets summarizing scope

## Actionable Takeaways

- 5-15 practical bullets
- Focus on what helps build/operate/debug
- Include gotchas inline

## Examples

[Code examples if essential]

## Related

- `references/related-topic.md`
```

## README.md Template

Human-readable description (not for LLM):

```markdown
# <Skill Name>

Brief description of what this skill provides.

## What This Skill Covers

- Bullet list of capabilities
- Keep it scannable

## Quick Navigation

- [SKILL.md](SKILL.md) — Entry point for agents
- [references/](references/) — Detailed documentation

## When to Use

Activate this skill when [brief trigger description].
```

## Frontmatter Examples

### Minimal (Required Only)

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
---
```

### With Optional Fields

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDFs, forms, or document extraction.
license: Apache-2.0
compatibility: Requires pdfplumber, PyPDF2
metadata:
  author: example-org
  version: "1.0"
---
```

### With Allowed Tools

```yaml
---
name: git-workflow
description: Git branching, merging, and release workflows.
allowed-tools: Bash(git:*) Read Write
---
```

### With Context Fork (Subagent)

```yaml
---
name: deep-research
description: Research a topic thoroughly in isolated context.
context: fork
agent: Explore
allowed-tools: Read Grep Glob
---
```

### Manual-Only Skill

```yaml
---
name: deploy
description: Deploy application to production
disable-model-invocation: true
---
```

### Background Knowledge (Not User-Invocable)

```yaml
---
name: api-conventions
description: API design patterns for this codebase
user-invocable: false
---
```

### With Argument Hint

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
argument-hint: <issue-number>
metadata:
  author: team
  version: "1.0.0"
---
```

### Full Example (All Fields)

```yaml
---
name: pr-review
description: Review pull request for issues. Use when asked to review PR or code changes.
license: MIT
compatibility: Requires gh CLI
context: fork
agent: Explore
disable-model-invocation: true
argument-hint: [pr-number]
allowed-tools: Read Grep Bash(gh:*)
metadata:
  author: example-org
  version: "1.0.0"
---
```

## Skill with Dynamic Context Template

```markdown
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh:*)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task

Summarize this pull request focusing on:
1. Main changes
2. Potential issues
3. Testing recommendations
```

## Skill with Arguments Template

```markdown
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
argument-hint: <issue-number>
---

Fix GitHub issue $ARGUMENTS following our coding standards:

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit with message referencing the issue
```

## metadata.json Template

```json
{
  "version": "1.0.0",
  "organization": "Your Organization",
  "date": "January 2026",
  "abstract": "Comprehensive description of what this skill provides, its scope, and how it helps automated code generation and review.",
  "references": [
    "https://docs.example.com",
    "https://github.com/org/repo",
    "https://example.com/api-reference"
  ]
}
```

## Description Examples

### Good Descriptions

```yaml
# Includes purpose + triggers + keywords
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.

description: Qdrant vector database playbook: core concepts (collections/points/payload), filtering, indexing, snapshots, deployment. Keywords: Qdrant, vector database, embeddings, ANN.

description: PostgreSQL RLS policies for multi-tenant applications. Use when implementing row-level security, tenant isolation, or app.current_user patterns.
```

### Poor Descriptions

```yaml
# Too vague
description: Helps with PDFs.

# Missing triggers
description: A skill for database operations.

# No keywords
description: Handles some common tasks.
```

## Naming Examples

### Valid Names

```
pdf-processing
data-analysis
code-review
qdrant
postgresql-rls
mcp-server
```

### Invalid Names

```
PDF-Processing    # uppercase
-pdf              # leading hyphen
pdf-              # trailing hyphen
pdf--processing   # consecutive hyphens
my skill          # spaces
my_skill          # underscores
```
