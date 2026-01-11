# Configuration & Customisation

Global settings, agent profiles, task tags, and keyboard shortcuts.

## Supported Agents

| Agent          | Variants              | Notes                  |
| -------------- | --------------------- | ---------------------- |
| Claude Code    | DEFAULT, PLAN, ROUTER | Primary recommendation |
| Codex          | DEFAULT, HIGH         | OpenAI Codex           |
| Gemini         | DEFAULT, FLASH        | Google Gemini          |
| GitHub Copilot | —                     | VS Code integration    |
| Amp            | —                     | Sourcegraph agent      |
| Cursor Agent   | —                     | Cursor IDE             |
| OpenCode       | —                     | Open-source agent      |
| Qwen Code      | —                     | Alibaba's coding agent |
| Droid          | —                     | —                      |

### Variant Meanings

**Claude Code**: DEFAULT (standard), PLAN (plan → confirm → execute), ROUTER (agentic routing)

**Codex**: DEFAULT (standard), HIGH (high-effort mode)

**Gemini**: DEFAULT (standard), FLASH (fast mode)

**Best Practice**: Use biggest/most capable model — fewer mistakes, less intervention.

## Global Settings

Access: Settings page (⚙️ icon in sidebar)

### Themes

Light / Dark mode toggle.

### Default Agent Configuration

Pre-selected agent and variant for new attempts.

1. Select agent (Claude Code, Gemini, Codex, etc.)
2. Choose variant (DEFAULT, PLAN, etc.)

Override per-attempt in create dialog.

### Editor Integration

Supported editors:

- VS Code
- Cursor
- Windsurf
- Neovim, Emacs, Sublime Text
- Custom shell command

#### Remote SSH Configuration

For Vibe Kanban running on remote server:

| Field           | Purpose                           |
| --------------- | --------------------------------- |
| Remote SSH Host | Hostname/IP (e.g., `example.com`) |
| Remote SSH User | SSH username                      |

Enables `vscode://vscode-remote/ssh-remote+user@host/path` URLs.

Prerequisites:

- SSH keys configured (no password prompts)
- VSCode Remote-SSH extension installed

### Git Configuration

**Branch Prefix**: Prefix for auto-generated branches (e.g., `vk` → `vk/task-name`)

### Notifications

Toggle sound effects and push notifications.

### Telemetry

Enable/disable data collection.

## Agent Profiles & Configuration

Settings → Agents

Define multiple variants per agent with different configurations.

### Configuration Access

- **Form Editor**: Guided interface
- **JSON Editor**: Direct JSON editing

### Configuration Structure

```json
{
  "executors": {
    "CLAUDE_CODE": {
      "DEFAULT": { "CLAUDE_CODE": { "dangerously_skip_permissions": true } },
      "PLAN": { "CLAUDE_CODE": { "plan": true } },
      "ROUTER": { "CLAUDE_CODE": { "claude_code_router": true, "dangerously_skip_permissions": true } }
    },
    "GEMINI": {
      "DEFAULT": { "GEMINI": { "model": "default", "yolo": true } },
      "FLASH": { "GEMINI": { "model": "flash", "yolo": true } }
    },
    "CODEX": {
      "DEFAULT": { "CODEX": { "sandbox": "danger-full-access" } },
      "HIGH": { "CODEX": { "sandbox": "danger-full-access", "model_reasoning_effort": "high" } }
    }
  }
}
```

### Agent-Specific Options

**Claude Code**:

- `plan`: Planning mode
- `claude_code_router`: Route across instances
- `dangerously_skip_permissions`: Skip prompts

**Universal Options**:

- `append_prompt`: Text appended to system prompt
- `base_command_override`: Override CLI command
- `additional_params`: Extra CLI arguments

**Warning**: Options with "dangerously\_" bypass safety confirmations.

## Task Tags

Reusable text snippets inserted via `@mention`.

### Managing Tags

Settings → General → Task Tags

- **Add Tag**: Click "Add Tag"
- **Edit**: Click edit icon (✏️)
- **Delete**: Click delete icon (🗑️)

### Naming

Use `snake_case` (no spaces): `bug_report`, `feature_request`, `code_review_checklist`

### Using Tags

1. Type `@` in task description
2. Filter by typing
3. Select tag or press Enter
4. Content inserted at cursor

Works in task descriptions and follow-up messages.

### Common Use Cases

- Bug report templates
- Acceptance criteria checklists
- Code review guidelines

## Keyboard Shortcuts

### Platform Keys

- `⌘` = Mac Command
- `Ctrl` = Windows/Linux Control

### Global Shortcuts

| Key          | Action       |
| ------------ | ------------ |
| `C`          | Create Task  |
| `⌘/Ctrl + S` | Focus Search |

### Board Navigation

(When task card has blue focus ring)

| Key       | Action                          |
| --------- | ------------------------------- |
| `k` / `j` | Move up/down in column          |
| `h` / `l` | Move left/right between columns |
| `Enter`   | Open task                       |
| `d`       | Delete task                     |

### Forms & Dialogs

| Key              | Action                |
| ---------------- | --------------------- |
| `⌘/Ctrl + Enter` | Submit / Send message |
| `Enter`          | New line              |
| `Shift + Tab`    | Switch agent profile  |
| `Escape`         | Cancel / Clear draft  |

### Tips

- Blue focus ring indicates active navigation
- Global shortcuts disabled in text fields
- `⌘S` badge shown near search field
