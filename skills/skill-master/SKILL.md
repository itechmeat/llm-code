---
name: skill-master
description: "Agent Skills authoring, evaluation, and optimization. Create, edit, validate, benchmark, and improve skills following the agentskills.io specification. Use when designing SKILL.md files, structuring skill folders (references, scripts, assets), ingesting external documentation into skills, running trigger evals, benchmarking skill quality, optimizing descriptions, or performing blind A/B comparisons. Keywords: agentskills.io, SKILL.md, skill authoring, eval, benchmark, trigger optimization."
metadata:
  version: "1.6.0"
  release_date: "2026-03-11"
---

# Skill Master

Create, edit, and validate Agent Skills following the open [agentskills.io](https://agentskills.io) specification. This skill is the entry point for creating and maintaining Agent Skills.

**Language requirement:** all skills MUST be authored in English.

## Links

- [Agent Skills Specification](https://agentskills.io/specification)
- [What are Skills?](https://agentskills.io/what-are-skills)
- [Integrate Skills](https://agentskills.io/integrate-skills)
- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) (Anthropic)

## Quick Navigation

- New to skills? Read: `references/specification.md`
- SKILL.md templates? See: `assets/skill-templates.md`
- Writing effective descriptions & instructions? Read: `references/writing-skills.md`
- Structuring multi-step processes? Read: `references/workflows.md`
- Adding scripts to a skill? Read: `references/scripts.md`
- Adding assets/templates to a skill? Read: `references/assets.md`
- Advanced features (context, agents, hooks)? Read: `references/advanced-features.md`
- Creating from docs? Read: `references/docs-ingestion.md`
- Testing, evals, benchmarking, or iterative improvement? Read: `references/testing-troubleshooting.md`, `references/eval-testing.md`, `references/iterative-improvement.md`
- Description optimization? Read: `references/description-optimization.md`
- JSON schemas (evals, grading, benchmark)? Read: `references/schemas.md`
- Eval set review UI and output viewer? See: `assets/eval_review.html`, `eval-viewer/`
- Validation & packaging? See `scripts/`

## When to Use

- Creating a new skill from scratch
- Updating an existing skill
- Creating a skill by ingesting external documentation
- Validating or packaging a skill for distribution
- Running the full skill-creator-style loop: interview, draft, eval, benchmark, viewer review, and iteration

`skill-master` subsumes `skill-creator`; for the detailed operator playbook, workspace layout, timing capture, benchmark analysis, and viewer handoff, read `references/iterative-improvement.md`.

## Skill Structure (Required)

```
my-skill/
├── SKILL.md          # Required: instructions + metadata (must be human-readable too)
├── metadata.json     # Optional: extended metadata for publishing
├── references/       # Optional: documentation, guides, API references
├── examples/         # Optional: sample outputs, usage examples
├── scripts/          # Optional: executable code
└── assets/           # Optional: templates, images, data files
```

_Do NOT include `README.md` in skill folders. `SKILL.md` is the single source of truth. If migrating a skill with `README.md`, merge its content into `SKILL.md` and delete it._

### Folder Purposes (CRITICAL)

| Folder        | Purpose                                    | Examples                                                |
| ------------- | ------------------------------------------ | ------------------------------------------------------- |
| `references/` | **Documentation** for agents to read       | Guides, API docs, concept explanations, troubleshooting |
| `examples/`   | **Sample outputs** showing expected format | Output examples, usage demonstrations                   |
| `assets/`     | **Static resources** to copy/use           | Document templates, config templates, images, schemas   |
| `scripts/`    | **Executable code** to run                 | Python scripts, shell scripts, validators               |

### When to Use Each

- `references/` — documentation the agent reads and understands
- `examples/` — sample outputs showing expected format
- `assets/` — templates, configs, schemas to copy verbatim
- `scripts/` — executable code the agent runs

**IMPORTANT**: Templates belong in `assets/`, examples in `examples/`, documentation in `references/`.

## Frontmatter Schema

Every `SKILL.md` MUST start with YAML frontmatter:

```yaml
---
name: skill-name
description: "What it does. Keywords: term1, term2."
metadata:
  author: your-name
  version: "1.2.3"
  release_date: "2026-01-01"
---
```

**Field order:** `name` → `description` → `license` → `compatibility` → `metadata`

### Required Fields

| Field       | Constraints                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------- |
| name        | 1-64 chars, lowercase `a-z0-9-`, no `--`, no leading/trailing `-`, must match folder name   |
| description | 1-1024 chars (target: 80-150), describes what skill does + when to use it, include keywords |

### Optional Fields (Top Level)

| Field         | Purpose                                           |
| ------------- | ------------------------------------------------- |
| license       | License name or reference to bundled LICENSE file |
| compatibility | Environment requirements (max 500 chars)          |
| metadata      | Object for arbitrary key-value pairs (see below)  |

### metadata Object (Common Fields)

| Field         | Purpose                                       |
| ------------- | --------------------------------------------- |
| author        | Author name or organization                   |
| version       | Upstream product version or skill version     |
| release_date  | Last meaningful update date (`YYYY-MM-DD`)    |
| argument-hint | Hint for autocomplete, e.g., `[issue-number]` |

### Optional Fields (Claude Code / Advanced)

| Field                    | Purpose                                                                    |
| ------------------------ | -------------------------------------------------------------------------- |
| disable-model-invocation | `true` = only user can invoke (via `/name`). Default: `false`              |
| user-invocable           | `false` = hidden from `/` menu, only agent can load. Default: `true`       |
| allowed-tools            | Space-delimited tools agent can use without asking, e.g., `Read Grep Glob` |
| model                    | Specific model to use when skill is active                                 |
| context                  | Set to `fork` to run in a forked subagent context                          |
| agent                    | Subagent type when `context: fork`, e.g., `Explore`, `Plan`                |
| hooks                    | Hooks scoped to skill's lifecycle (see agent documentation)                |

### Invocation Control Matrix

| Frontmatter                      | User can invoke | Agent can invoke | Notes                                   |
| -------------------------------- | --------------- | ---------------- | --------------------------------------- |
| (default)                        | ✅ Yes          | ✅ Yes           | Description in context, loads when used |
| `disable-model-invocation: true` | ✅ Yes          | ❌ No            | For manual workflows with side effects  |
| `user-invocable: false`          | ❌ No           | ✅ Yes           | Background knowledge, not a command     |

### Variable Substitutions

Available placeholders in skill content:

| Variable               | Description                                              |
| ---------------------- | -------------------------------------------------------- |
| `$ARGUMENTS`           | All arguments passed when invoking the skill             |
| `${CLAUDE_SESSION_ID}` | Current session ID for logging or session-specific files |

If `$ARGUMENTS` is not in content, arguments are appended as `ARGUMENTS: <value>`.

Example:

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---
Fix GitHub issue $ARGUMENTS following our coding standards.
```

### Dynamic Context Injection

Use `!`command`` syntax to run shell commands before skill content is sent to the agent:

```markdown
## Pull request context

- PR diff: !`gh pr diff`
- Changed files: !`gh pr diff --name-only`

## Your task

Review this pull request...
```

The command output replaces the placeholder, so the agent receives actual data.

## metadata.json (Optional)

For publishing or extended metadata, create `metadata.json`:

```json
{
  "version": "1.0.0",
  "organization": "Your Org",
  "date": "January 2026",
  "abstract": "Brief description of what this skill provides...",
  "references": ["https://docs.example.com", "https://github.com/org/repo"]
}
```

**Fields:**

- `version` — Skill version (semver)
- `organization` — Author or organization
- `date` — Publication date
- `abstract` — Extended description (can be longer than frontmatter)
- `references` — List of source documentation URLs

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

### Description Rules

**Purpose:** Tell the LLM what the skill does and when to activate it. Minimize tokens — just enough for activation decision.

**Formulas:**

For library/reference skills (Claude Code, keyword-based discovery):

```
[Product] [core function]. Covers [2-3 key topics]. Keywords: [terms].
```

For workflow/automation skills (Claude.ai, trigger-based activation):

```
[What it does]. Use when user [specific trigger phrases].
```

**Critical for auto-triggering:** include explicit "Use when user says / asks / mentions..." phrases. Without them, Claude may not load the skill automatically. See `references/writing-skills.md` for good/bad examples and debugging tips.

**Constraints:**

- Target: 80-150 chars
- Max: 1024 chars (300 if keeping it minimal)
- No marketing ("powerful", "comprehensive", "modern")
- No filler ("this skill", "use this for", "helps with")
- No XML angle brackets `< >`
- Names with "claude" or "anthropic" are reserved

**Good examples:**

```yaml
description: "Turso SQLite database. Covers encryption, sync, agent patterns. Keywords: Turso, libSQL, SQLite."

description: "Base UI unstyled React components. Covers forms, menus, overlays. Keywords: @base-ui/react, render props."

description: "Inworld TTS API. Covers voice cloning, audio markups, timestamps. Keywords: Inworld, TTS, visemes."
```

**Poor examples:**

```yaml
# Too vague
description: "Helps with PDFs."

# Too verbose
description: "Turso embedded SQLite database for modern apps and AI agents. Covers encryption, authorization, sync, partial sync, and agent database patterns."

# Marketing
description: "A powerful solution for all your database needs."
```

**Keywords:** product name, package name, 3-5 terms max.

## How Skills Work (Progressive Disclosure)

1. **Discovery**: Agent loads only `name` + `description` of each skill (~50-100 tokens)
2. **Activation**: When task matches, agent reads full `SKILL.md` into context
3. **Execution**: Agent follows instructions, loads referenced files as needed

**Key rule:** Keep `SKILL.md` under 500 lines. Move details to `references/`.

## Creating a New Skill

_Pro Tip: You can use the `skill-creator` skill (available in Claude.ai or Claude Code) to interactively generate your first draft, then refine it using the steps below._

### Step 1: Scaffold

```bash
python scripts/init_skill.py <skill-name>
# Or specify custom directory:
python scripts/init_skill.py <skill-name> --skills-dir skills
```

Or manually create:

```
<skills-folder>/<skill-name>/
├── SKILL.md
├── references/   # For documentation, guides
└── assets/       # For templates, static files
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
- Quick navigation (router to references and assets)
- Steps / Recipes / Checklists
- Critical prohibitions
- Links

### Step 4: Add References (documentation)

For each major topic, create `references/<topic>.md` with:

- Actionable takeaways (5-15 bullets)
- Gotchas / prohibitions
- Practical examples

### Step 5: Add Scripts (if applicable)

Consult `references/scripts.md` for when scripts are worth writing and how to structure them.

Language selection:

- **Python** — default for CLI wrappers, validators, scaffolding
- **Go** — when the skill's ecosystem is Kubernetes/cloud-native (see k8s-cluster-api)
- **JS/TS** — when the skill's ecosystem is Node/npm

Minimal checklist for a script:

- `argparse` (Python) or `flag` (Go) for all parameters — no hardcoded values
- Check tool availability before use (`shutil.which()` in Python)
- Docstring at top with Usage + Examples
- All exceptions caught; exit non-zero with a message to stderr

### Step 6: Add Assets (if needed)

Consult `references/assets.md` for when assets are worth creating and how to format them.

For templates or static resources, create `assets/<resource>`. Common types:

- **Config templates** — `.minimal.yaml` / `.full.yaml` pair; add `# yaml-language-server: $schema=` header
- **YAML manifests** — use `${VAR_NAME:=default}` for variables; include purpose + usage comment at top
- **Text templates** — use `#`-prefixed comments to explain fields and valid values
- **Markdown checklists / runbooks** — `- [ ]` checkboxes, inline commands, sign-off section
- **Prompt / prose templates** — grouped by use case, each block self-contained

Naming: `<tool>.minimal.yaml`, `<purpose>-checklist.md`, `<name>.template`, `<topic>-prompts.md`.

### Step 7: Validate

```bash
python scripts/quick_validate_skill.py <skill-path>
# Compatibility alias:
python scripts/quick_validate.py <skill-path>
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
- Do NOT omit product version when creating skills from documentation

## Version Tracking

### What `version` Means

In this repository, store version metadata as `metadata.version` and `metadata.release_date` to match the existing skills and current Copilot skill-file validation.
`metadata.version` holds the **upstream product version** the skill was built against (e.g., `"1.12.3"` for CAPI v1.12.3). For standalone skills not tied to an external product, it holds the **skill's own version** (e.g., `"1.2.4"` for skill-master).
Use `"—"` when the product uses continuous deployment with no semantic versioning (e.g., hosted services like Cloudflare Workers).

### When to Update

| Trigger                              | Update `metadata.version` | Update `metadata.release_date` |
| ------------------------------------ | ------------------------- | ------------------------------ |
| Product released a new version       | ✅ Yes                    | ✅ Yes                         |
| Content changed, no upstream version | ❌ No                     | ✅ Yes                         |
| Typo or minor fix                    | ❌ No                     | ❌ No                          |

When bumping `metadata.version` or making significant content changes, also update:

- `SKILLS_VERSIONS.md` — set new version + date, move row to top of table
- `CHANGELOG.md` — prepend a new dated block at the top

**Links format:**

```markdown
## Links

- [Documentation](https://example.com/docs)
- [Changelog](https://example.com/changelog)
- [GitHub](https://github.com/org/repo)
- [npm](https://www.npmjs.com/package/name)
```

Order: Documentation → Changelog/Releases → GitHub → Package registry. Include only applicable links.

## Validation Checklist

_Pro Tip: You can use the `skill-creator` skill (available in Claude.ai or Claude Code) to review your skill and suggest improvements before finalizing._

- [ ] `name` matches folder name, kebab-case, 1-64 chars, no `--`
- [ ] `description` includes WHAT it does AND WHEN to use it (trigger phrases)
- [ ] `description` has no XML angle brackets `< >`
- [ ] `SKILL.md` under 500 lines
- [ ] Documentation in `references/`, templates in `assets/`
- [ ] Complex multi-step processes extracted to `references/workflows.md`
- [ ] All text in English
- [ ] Skill triggers on obvious test queries
- [ ] Skill does NOT trigger on unrelated queries

Full pre-publish checklist: `references/testing-troubleshooting.md`

## Scripts

| Script                    | Purpose                                                 |
| ------------------------- | ------------------------------------------------------- |
| `init_skill.py`           | Scaffold new Agent Skill (agentskills.io)               |
| `init_copilot_asset.py`   | Scaffold Copilot-specific assets (instructions, agents) |
| `quick_validate_skill.py` | Validate skill structure                                |
| `quick_validate.py`       | Compatibility wrapper for legacy validation workflow    |
| `package_skill.py`        | Package skill into distributable zip                    |
| `run_eval.py`             | Run evals via `claude -p` with parallel workers         |
| `run_loop.py`             | Eval+improve loop with train/test split                 |
| `improve_description.py`  | Improve skill description using eval feedback           |
| `aggregate_benchmark.py`  | Aggregate grading results into benchmark stats          |
| `generate_report.py`      | Generate HTML report from loop iteration data           |

Agents: `agents/grader.md` (grade expectations), `agents/comparator.md` (blind A/B comparison), `agents/analyzer.md` (post-hoc analysis + benchmark)

## Links

- Specification: `references/specification.md`
- Writing Skills (descriptions, instructions, patterns): `references/writing-skills.md`
- Workflow Patterns: `references/workflows.md`
- Scripts in Skills: `references/scripts.md`
- Assets in Skills: `references/assets.md`
- Testing & Troubleshooting: `references/testing-troubleshooting.md`
- Advanced Features: `references/advanced-features.md`
- SKILL.md Templates: `assets/skill-templates.md`
- Docs Ingestion: `references/docs-ingestion.md`
- Eval Testing & Benchmarking: `references/eval-testing.md`
- Iterative Improvement Loop: `references/iterative-improvement.md`
- Description Optimization: `references/description-optimization.md`
- JSON Schemas: `references/schemas.md`
- Eval Set Review: `assets/eval_review.html`
- Eval Output Viewer: `eval-viewer/`
- Official spec: https://agentskills.io/specification
- Claude Code skills: https://code.claude.com/docs/en/skills
