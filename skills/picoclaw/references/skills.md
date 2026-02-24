# Skills management

Skills live inside the workspace (default: `~/.picoclaw/workspace/skills`).

## List / show

- List installed:
  - `picoclaw skills list`
- Show a skill:
  - `picoclaw skills show <skill-name>`

## Install

Two install paths are supported:

1. From GitHub repo slug (backward compatible)

- `picoclaw skills install <owner>/<repo>/<skill-folder>`
  - Example: `picoclaw skills install sipeed/picoclaw-skills/weather`

2. From a registry (e.g. ClawHub)

- `picoclaw skills install --registry <name> <slug>`
  - Example: `picoclaw skills install --registry clawhub github`

Registry endpoints are configured under `tools.skills.registries.*`.

## Remove

- `picoclaw skills remove <skill-name>`

## Built-in skills

- `picoclaw skills install-builtin` copies a small set of builtin skills (weather/news/stock/calculator) into the workspace.
- `picoclaw skills list-builtin` lists builtin skills from the global picoclaw directory.
