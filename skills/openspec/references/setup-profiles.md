# Setup and Profiles (CLI)

Operational notes for OpenSpec v1.3.0+ about initializing a project, updating installed tool integrations, and managing workflow profiles.

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

In v1.3.0, GitHub Copilot detection is stricter: a bare `.github/` directory is not enough. Detection should be based on Copilot-specific markers such as `.github/copilot-instructions.md`, `.github/instructions/`, `.github/prompts/`, `.github/agents/`, or `.github/skills/`.

### New tool directories (v1.2.0)

- **Pi:** `.pi/skills/` and `.pi/prompts/`
- **Kiro:** `.kiro/skills/` and `.kiro/prompts/`

### New tool directories / adapters (v1.3.0)

- **Junie:** `.junie/skills/` and `.junie/commands/`
- **Lingma:** `.lingma/skills/` and `.lingma/commands/opsx/`
- **IBM Bob:** `.bob/skills/` and `.bob/commands/`
- **ForgeCode:** `.forge/skills/` only; no command adapter is generated
- **OpenCode:** command files belong under `.opencode/commands/` (plural)
- **Pi:** if command references or template arguments looked broken in older output, regenerate after upgrading to pick up the v1.3.0 fix

### Shell completions (v1.3.0)

- Completion installation is opt-in. Do not assume `openspec init` should modify shell completion files unless the operator explicitly wants it.
- This matters most on PowerShell, where the v1.3.0 change avoids encoding corruption from automatic completion installation.

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
