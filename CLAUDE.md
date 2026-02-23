# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of 40+ Agent Skills for AI coding tools (Claude Code, GitHub Copilot, Cursor). Skills are installed into user projects via `npx add-skill itechmeat/llm-code`.

## Key Commands

```bash
# Scaffold a new skill
python skills/skill-master/scripts/init_skill.py <skill-name>

# Validate a skill's structure
python skills/skill-master/scripts/quick_validate_skill.py skills/<skill-name>

# Package a skill for distribution
python skills/skill-master/scripts/package_skill.py skills/<skill-name>
```

There are no build or test commands — this is a documentation/skill collection with no runtime dependencies.

## Repository Structure

```
skills/                     # Main skills directory
  <skill-name>/
    SKILL.md                # Required: frontmatter + agent instructions (must be human-readable too)
    references/             # Documentation for agents to read
    assets/                 # Templates/static files for agents to copy
    examples/               # Sample outputs showing expected format
    scripts/                # Executable utilities
agents/                     # Claude Code agent mode definitions
.github/
  skills/                   # GitHub Copilot-specific skill copies
  instructions/             # Copilot .instructions.md files
  agents/                   # Copilot agent definitions
  copilot-instructions.md   # Copilot repo-wide rules
.agents/skills/             # Agent-specific local skills (gitignored)
CHANGELOG.md                # Date-based versioning (Keep a Changelog)
SKILLS_VERSIONS.md          # Tracks product versions for each skill
```

## Skill Authoring Rules

### SKILL.md Frontmatter

```yaml
---
name: skill-name # must match folder name; lowercase a-z0-9- only, no --
description: "..." # 80-150 chars; include trigger keywords for agent discovery
version: "1.2.3" # upstream product/library version being documented
release_date: "2026-01-01"
---
```

**Hard rules:**

- `name` must exactly match folder name
- Keep `SKILL.md` under 500 lines — move details to `references/`
- All skill content must be in English
- Do not copy large verbatim chunks from vendor documentation
- Do not include project-specific secrets or paths
- Cross-skill references must use relative paths (skills are assumed to be in the same folder)

**Folder purposes:**

- `references/` — documentation agents read to understand a topic
- `assets/` — templates/configs agents copy verbatim
- `examples/` — sample outputs showing expected result format
- `scripts/` — executable code agents run

**File size:** avoid small isolated reference files — merge logically related content into a single well-named file.

### SKILL.md

`SKILL.md` is the single source of truth for both agents and humans. It must:

- Be equally readable by humans and agents without "fluff" or duplication.
- Briefly describe what the skill covers (1-2 sentences) at the top.
- Include a `## Links` section: Documentation → Changelog/Releases → GitHub → Package registry (only applicable links).
- Installation steps do NOT belong in `SKILL.md` — put them in a separate `references/installation.md` if needed.
- **Do NOT create a `README.md` file inside the skill folder.** If a `README.md` exists, its useful information (like links and brief description) should be merged into `SKILL.md` and the `README.md` deleted.

## Workflows

### Creating a New Skill from Documentation

**Phase 1 — Init (strictly sequential):**

1. Visit the start page of the documentation
2. Create `plan.md` in the skill folder with basic info
3. Add a checklist to `plan.md` from the nav links — do NOT visit them yet
4. Create base `SKILL.md` with structure

**Phase 2 — Iterative ingestion (one page at a time — CRITICAL):**

1. Visit ONE page from the checklist
2. Immediately create or update the corresponding `references/` file
3. Mark the page in `plan.md` as `✅`
4. Only then move to the next page

**Forbidden during ingestion:**

- Visiting multiple pages without writing between them
- Accumulating information in memory for later writing
- Batch-fetching several pages at once

**Phase 3 — Finalization:**

1. Check consistency across all references
2. Remove duplication; merge overlapping files into logically named ones
3. Ensure `SKILL.md` has a human-readable overview and `## Links` section

`plan.md` is a temporary file — do not reference it from `SKILL.md`. It is deleted manually after finalization.

### Updating an Existing Skill

When iterating through `SKILLS_VERSIONS.md`:

1. Visit the Releases page for the skill
2. If there's an update — move the row to the top of the table, update `version` and `release_date` in both `SKILLS_VERSIONS.md` and the skill's `SKILL.md`
3. If there is real content to update — fetch only the relevant changed docs (filter by changelog since last skill version), then **ask the user** whether to update
4. If the change is minor (version bump only) — do it autonomously without asking
5. Skip skills marked with `[ignore]` in the table
6. Work strictly one skill at a time; after moving a skill to the top, continue from where it was in the original order to avoid re-checking

### Checking / Compressing a Skill

- Remove fluff and redundant content
- Merge duplicating or overlapping references — use logical (not compound) file names
- Be concise without losing valuable information
- Ensure `version`, `release_date`, and `description` are present and correct
- Ensure `SKILL.md` has the `Links` section
- Do not put installation details in `SKILL.md` — move to `references/installation.md`

## Versioning & Changelog

- CHANGELOG.md uses date-based versioning (`[YYYY-MM-DD]` headings), not semver
- When writing a changelog entry: read `skills/changelog/SKILL.md` and `skills/commits/SKILL.md` first
- Do not use `[Unreleased]` — use today's date
- Do not modify old entries — only prepend a new dated block
- Commit messages follow Conventional Commits: short subject on first line, details in body
- All changelog and commit text must be in English
- **Added** = genuinely new things (new skill, new file that didn't exist); **Changed** = updates to existing things; do not put an updated skill in Added
- Keep entries concise — one sentence per item, no sub-lists; omit implementation details

When adding or updating a skill, also update:

- `CHANGELOG.md` (new dated block at the top)
- `SKILLS_VERSIONS.md` (version, date, move row to top)
- Root `README.md` skills table (if adding a new skill)

## Documentation Sources

- **Always use official documentation links** — do not use Context7 or internal knowledge base for skill content
- The `version` + `release_date` in skill frontmatter refers to the upstream product version, not this repo
