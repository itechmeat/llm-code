# Skill Master

Create, edit, and validate Agent Skills following the open [agentskills.io](https://agentskills.io) specification.

## What This Skill Covers

- **Specification**: SKILL.md format, frontmatter schema, naming rules
- **Progressive Disclosure**: How skills work with agents (discovery → activation → execution)
- **Docs Ingestion**: Autonomous workflow for building skills from external documentation
- **Validation & Packaging**: Scripts for validating and distributing skills

## Quick Navigation

- [SKILL.md](SKILL.md) — Entry point for agents
- [references/specification.md](references/specification.md) — Full specification details
- [references/templates.md](references/templates.md) — Ready-to-use templates
- [references/docs-ingestion.md](references/docs-ingestion.md) — Building skills from docs
- [scripts/](scripts/) — Scaffolding, validation, packaging

## When to Use

Activate this skill when:

- Creating a new skill from scratch
- Updating or refactoring an existing skill
- Building a skill by ingesting vendor documentation
- Validating skill structure before distribution

## Scripts

| Script                    | Purpose                              |
| ------------------------- | ------------------------------------ |
| `init_skill.py`           | Scaffold new Agent Skill             |
| `quick_validate_skill.py` | Validate SKILL.md format             |
| `package_skill.py`        | Package skill into distributable zip |

## External Links

- [Agent Skills Specification](https://agentskills.io/specification)
- [What are Skills?](https://agentskills.io/what-are-skills)
- [Integrate Skills](https://agentskills.io/integrate-skills)
