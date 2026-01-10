---
name: skill-master
description: "Create, edit, and validate Agent Skills following the open agentskills.io specification. Covers SKILL.md format, frontmatter schema, progressive disclosure, docs ingestion workflow, and packaging. Keywords: agent skills, skill authoring, SKILL.md, frontmatter, description, progressive disclosure, docs ingestion, ai_fetch_url."
---

# Skill Master

This skill is the entry point for creating and maintaining Agent Skills.

**Language requirement:** all skills MUST be authored in English.

## Quick Navigation

- New to skills? Read: `references/specification.md`
- Need templates? Read: `references/templates.md`
- Creating from docs? Read: `references/docs-ingestion.md`
- Validation & packaging? See `scripts/`

## When to Use

- Creating a new skill from scratch
- Updating an existing skill
- Creating a skill by ingesting external documentation
- Validating or packaging a skill for distribution

## Skill Structure (Required)

```
my-skill/
├── SKILL.md          # Required: instructions + metadata
├── README.md         # Optional: human-readable description
├── references/       # Optional: detailed documentation
├── scripts/          # Optional: executable code
└── assets/           # Optional: templates, resources
```

## Frontmatter Schema

Every `SKILL.md` MUST start with YAML frontmatter:

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### Required Fields

| Field       | Constraints                                                                               |
| ----------- | ----------------------------------------------------------------------------------------- |
| name        | 1-64 chars, lowercase `a-z0-9-`, no `--`, no leading/trailing `-`, must match folder name |
| description | 1-1024 chars, describes what skill does + when to use it, include discovery keywords      |

### Optional Fields

| Field         | Purpose                                           |
| ------------- | ------------------------------------------------- |
| license       | License name or reference to bundled LICENSE file |
| compatibility | Environment requirements (max 500 chars)          |
| metadata      | Arbitrary key-value pairs (author, version, etc.) |
| allowed-tools | Space-delimited pre-approved tools (experimental) |

### Name Validation Examples

```yaml
# Valid
name: pdf-processing
name: data-analysis
name: code-review

# Invalid
name: PDF-Processing  # uppercase not allowed
name: -pdf            # cannot start with hyphen
name: pdf--processing # consecutive hyphens not allowed
```

### Description Best Practices

Good:

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

Poor:

```yaml
description: Helps with PDFs.
```

## How Skills Work (Progressive Disclosure)

1. **Discovery**: Agent loads only `name` + `description` of each skill (~50-100 tokens)
2. **Activation**: When task matches, agent reads full `SKILL.md` into context
3. **Execution**: Agent follows instructions, loads referenced files as needed

**Key rule:** Keep `SKILL.md` under 500 lines. Move details to `references/`.

## Creating a New Skill

### Step 1: Scaffold

```bash
python scripts/init_skill.py <skill-name>
# Or specify custom directory:
python scripts/init_skill.py <skill-name> --skills-dir .llm-code/skills
```

Or manually create:

```
<skills-folder>/<skill-name>/
├── SKILL.md
└── references/
```

### Step 2: Write Frontmatter

```yaml
---
name: <skill-name>
description: "[Purpose] + [Triggers/Keywords]"
---
```

### Step 3: Write Body

Recommended sections:

- When to use (triggers, situations)
- Quick navigation (router to references)
- Steps / Recipes / Checklists
- Critical prohibitions
- Links

### Step 4: Add References

For each major topic, create `references/<topic>.md` with:

- Actionable takeaways (5-15 bullets)
- Gotchas / prohibitions
- Practical examples

### Step 5: Validate

```bash
python scripts/quick_validate_skill.py <skill-path>
```

## Creating a Skill from Documentation

When building a skill from external docs, use the autonomous ingestion workflow:

### Phase 1: Scaffold

1. Create skill folder with `SKILL.md` skeleton
2. Create `plan.md` for progress tracking
3. Create `references/` directory

### Phase 2: Build Queue

For each doc link:

- Fetch the page
- Extract internal doc links (avoid nav duplicates)
- Prioritize: concepts → API → operations → troubleshooting

### Phase 3: Ingest Loop

For each page:

1. Fetch **one** page
2. Create `references/<topic>.md` with actionable summary
3. Update `plan.md` checkbox
4. Update `SKILL.md` if it adds a useful recipe/rule

**Do not ask user after each page** — continue autonomously.

### Phase 4: Finalize

- Review `SKILL.md` for completeness
- Ensure practical recipes, not docs mirror
- `plan.md` may be deleted manually after ingestion

## Critical Prohibitions

- Do NOT copy large verbatim chunks from vendor docs (summarize in own words)
- Do NOT write skills in languages other than English
- Do NOT include project-specific secrets, paths, or assumptions
- Do NOT keep `SKILL.md` over 500 lines
- Do NOT skip `name` validation (must match folder name)
- Do NOT use poor descriptions that lack trigger keywords

## Validation Checklist

- [ ] `name` matches folder name
- [ ] `name` is 1-64 chars, lowercase, no `--`
- [ ] `description` is 1-1024 chars, includes keywords
- [ ] `SKILL.md` under 500 lines
- [ ] Long content moved to `references/`
- [ ] All text in English

## Scripts

| Script                    | Purpose                                                 |
| ------------------------- | ------------------------------------------------------- |
| `init_skill.py`           | Scaffold new Agent Skill (agentskills.io)               |
| `init_copilot_asset.py`   | Scaffold Copilot-specific assets (instructions, agents) |
| `quick_validate_skill.py` | Validate skill structure                                |
| `package_skill.py`        | Package skill into distributable zip                    |

## Links

- Specification: `references/specification.md`
- Templates: `references/templates.md`
- Docs Ingestion: `references/docs-ingestion.md`
- Official spec: https://agentskills.io/specification
