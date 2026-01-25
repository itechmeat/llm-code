# Integrations

GitHub, Azure Repos, VSCode Extension, and MCP servers.

## GitHub Integration

Create PRs directly from tasks via GitHub CLI.

### Setup

**Automatic**: Prompted when first creating PR on macOS (Homebrew install).

**Manual**:

```bash
# Install
brew install gh  # macOS
# Windows/Linux: See https://github.com/cli/cli#installation

# Authenticate
gh auth login
```

### Creating a PR

1. Open task with changes
2. Click "Create PR"
3. Title/description pre-filled from task
4. Click "Create"

PR link added to task. When merged on GitHub, task auto-moves to Done.

## Azure Repos Integration

Create PRs via Azure CLI with DevOps extension.

### Setup

```bash
# Install Azure CLI
brew install azure-cli  # macOS

# Add DevOps extension
az extension add --name azure-devops

# Authenticate
az login

# Configure defaults (optional)
az devops configure --defaults organization=https://dev.azure.com/{your-org} project={your-project}
```

### Supported URL Formats

- Modern: `https://dev.azure.com/{org}/{project}/_git/{repo}`
- Legacy: `https://{org}.visualstudio.com/{project}/_git/{repo}`

Both HTTPS and SSH remotes supported.

### Creating a PR

Same flow as GitHub: Click "Create PR" in task view.

## VSCode Extension

Task management directly in IDE.

### Installation

**VSCode**: Install from Marketplace (`bloop.vibe-kanban`)

**Cursor/Windsurf**: Install from Open VSX Registry

Or search: `@id:bloop.vibe-kanban`

### Features

| View      | Purpose                                    |
| --------- | ------------------------------------------ |
| Logs      | Task attempts, agent steps                 |
| Diffs     | Side-by-side code changes, inline comments |
| Processes | Running/completed processes                |

### Workflow

1. Start task in Vibe Kanban web UI
2. Click "Open in VSCode" (or Cursor/Windsurf)
3. IDE opens in task worktree
4. Extension populated with task context

**Important**: Extension only works when opened via Vibe Kanban — needs worktree context.

### Supported IDEs

| IDE      | Support | Source             |
| -------- | ------- | ------------------ |
| VSCode   | ✅      | VSCode Marketplace |
| Cursor   | ✅      | Open VSX Registry  |
| Windsurf | ✅      | Open VSX Registry  |

## Connecting MCP Servers to Agents

Add external tools to coding agents.

### Access

Settings → MCP Servers → Select agent

### Popular Servers

One-click installation for common servers (Playwright, Sentry, Notion, etc.)

### Custom Servers

Add to Server Configuration JSON:

```json
{
  "mcpServers": {
    "my_custom_server": {
      "command": "node",
      "args": ["/path/to/my-server.js"]
    }
  }
}
```

**Tip**: Don't add too many servers — overwhelms agents with options.

**Note**: Changes persist in agent's global config even without Vibe Kanban.

## Vibe Kanban MCP Server

Expose Vibe Kanban to external MCP clients (Claude Desktop, Raycast, etc.)

### Setup via Web UI

1. Settings → MCP Servers
2. Click Vibe Kanban in "Popular servers"
3. Save Settings

### Manual Setup

Add to MCP client config:

```json
{
  "mcpServers": {
    "vibe_kanban": {
      "command": "npx",
      "args": ["-y", "vibe-kanban@latest", "--mcp"]
    }
  }
}
```

### Available Tools

| Tool                 | Purpose               | Required Params                      |
| -------------------- | --------------------- | ------------------------------------ |
| `list_projects`      | Fetch all projects    | —                                    |
| `list_tasks`         | List tasks in project | `project_id`                         |
| `create_task`        | Create new task       | `project_id`, `title`                |
| `get_task`           | Get task details      | `task_id`                            |
| `update_task`        | Update task           | `task_id`                            |
| `delete_task`        | Delete task           | `task_id`                            |
| `start_task_attempt` | Start agent on task   | `task_id`, `executor`, `base_branch` |

### Supported Executors

`claude-code`, `amp`, `gemini`, `codex`, `opencode`, `cursor_agent`, `qwen-code`, `copilot`, `droid`

### Example Usage

**Create tasks from plan**:

```
I need to build user authentication with:
- Registration with email validation
- Login/logout
- Password reset

Then turn this plan into tasks.
```

MCP client creates structured tasks in Vibe Kanban.

**Start task execution**:

```
Start working on the registration task using Claude Code on main branch.
```

**Note**: MCP server is local-only — cannot be accessed via public URLs.
