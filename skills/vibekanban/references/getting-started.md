# Getting Started

Installation and initial setup for Vibe Kanban.

## Supported Systems

macOS (Intel/Apple Silicon), Linux, Windows

## Prerequisites

1. **Node.js**: Latest LTS version
2. **Coding Agent**: Authenticate externally before using Vibe Kanban

## Installation

```bash
npx vibe-kanban
```

- Binds to random free port
- Opens browser automatically
- This remains the default docs-first launch path even after the packaged desktop app moved to a Tauri v2 shell in v0.1.30.

### Fixed Port

```bash
PORT=8080 npx vibe-kanban
```

## Initial Setup Flow

1. **Authenticate with coding agent** — Do this externally first (e.g., `claude auth login`)
2. **Run `npx vibe-kanban`** — Application launches
3. **Complete setup dialogs** — Configure agent and editor preferences
4. **Create first project** — Select from recent git repos or create blank
5. **Add tasks** — Start tracking work

## GitHub Integration (Optional)

Requires GitHub CLI:

```bash
brew install gh  # macOS
gh auth login
```

Enables: Creating PRs, PR status syncing, auto-move to Done when merged.

## Updating

```bash
npx vibe-kanban@latest
```

- If you run the packaged desktop build rather than `npx`, expect updates to come through the app's Tauri v2 auto-updater path instead of the npm command above.
