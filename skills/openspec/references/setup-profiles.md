# Setup and Profiles (CLI)

Operational notes for OpenSpec v1.2.0+ about initializing a project, updating installed tool integrations, and managing workflow profiles.

## Initialize a Project (`openspec init`)

Interactive setup (recommended):

```bash
openspec init
```

Non-interactive tool selection:

```bash
# Configure specific tools
openspec init --tools claude,cursor

# Configure all supported tools
openspec init --tools all

# Skip tool configuration
openspec init --tools none
```

OpenSpec can also auto-detect existing tool directories (e.g. `.claude/`, `.cursor/`) and pre-select them during `openspec init`.

### New tool directories (v1.2.0)

- **Pi:** `.pi/skills/` and `.pi/prompts/`
- **Kiro:** `.kiro/skills/` and `.kiro/prompts/`

## Keep Tool Files in Sync (`openspec update`)

After upgrading the CLI, regenerate tool-specific command/skill files:

```bash
openspec update
```

In v1.2.0, `openspec update` can also prune command files and tool skill directories for workflows you’ve deselected (so projects don’t accumulate stale integrations).

## Workflow Profiles (`openspec config profile`)

Profiles control which workflows are selected (and thus which command/skill files are installed).

```bash
# Interactive wizard
openspec config profile

# Fast preset: minimal essential workflows
openspec config profile core
```

Notes:

- `openspec config profile` updates global configuration; apply to a project with `openspec update`.
- `openspec config list` may warn when global config and the current project’s installed files drift out of sync (run `openspec update`).
