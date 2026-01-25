# Agent Skills Specification

Source: https://agentskills.io/specification

## Overview

Agent Skills are a lightweight, open format for extending AI agent capabilities. A skill is a folder containing a `SKILL.md` file with metadata and instructions.

## SKILL.md File Format

The file MUST contain:

1. YAML frontmatter (between `---` markers)
2. Markdown body with instructions

```markdown
---
name: skill-name
description: What this skill does and when to use it.
---

# Skill Title

Instructions go here...
```

## Frontmatter Fields

### Required: `name`

- 1-64 characters
- Lowercase alphanumeric + hyphens only (`a-z`, `0-9`, `-`)
- No consecutive hyphens (`--`)
- No leading/trailing hyphens
- MUST match parent directory name

### Required: `description`

- 1-1024 characters
- Describes what the skill does AND when to use it
- Include keywords for agent discovery

### Optional: `license`

License name or reference to bundled file.

```yaml
license: Apache-2.0
license: Proprietary. LICENSE.txt has complete terms
```

### Optional: `compatibility`

Environment requirements (1-500 chars). Only include if skill has specific needs.

```yaml
compatibility: Requires git, docker, jq, and access to the internet
compatibility: Designed for Claude Code (or similar products)
```

### Optional: `metadata`

Arbitrary key-value pairs for additional properties.

```yaml
metadata:
  author: example-org
  version: "1.0"
```

### Optional: `allowed-tools`

Space-delimited list of pre-approved tools (experimental).

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

## Markdown Body

No format restrictions. Write whatever helps agents perform the task.

Recommended sections:

- Step-by-step instructions
- Input/output examples
- Common edge cases

**Size guideline:** Keep under 500 lines. Split longer content into referenced files.

## Progressive Disclosure Model

Skills use three-phase loading to manage context:

1. **Discovery** — At startup, agent loads only `name` + `description` (~50-100 tokens per skill)
2. **Activation** — When task matches, agent reads full `SKILL.md`
3. **Execution** — Agent follows instructions, loads referenced files as needed

## Agent Integration

### Filesystem-based agents

Skills activate when agent reads the file:

```bash
cat /path/to/my-skill/SKILL.md
```

### Tool-based agents

Skills activate via custom tool implementation (developer-defined).

### Context Injection Format

For Claude models, recommended XML format:

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extracts text and tables from PDFs...</description>
    <location>/path/to/skills/pdf-processing/SKILL.md</location>
  </skill>
</available_skills>
```

## Validation Rules

1. Frontmatter must parse as valid YAML
2. `name` must match directory name
3. `name` must follow naming constraints
4. `description` must be non-empty
5. No angle brackets in description (`<` or `>`)

## Security Considerations

When skills include scripts:

- Sandbox execution environments
- Allowlist trusted skills only
- Confirm before dangerous operations
- Log all script executions

## Reference Implementation

The `skills-ref` library provides validation and prompt generation:

```bash
# Validate a skill
skills-ref validate <path>

# Generate available_skills XML
skills-ref to-prompt <path>...
```
