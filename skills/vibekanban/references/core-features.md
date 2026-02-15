# Core Features

Projects, tasks, execution monitoring, testing, code review, and task completion.

## Creating Projects

### From Existing Repository

1. Click "Create Project"
2. Select "From existing git repository"
3. Browse and select git repo

### Create Blank

1. Click "Create Project"
2. Select "Create blank project"
3. New git repo generated

### Project Settings

Access via settings button (top right) after creating project.

| Setting            | Purpose                                    |
| ------------------ | ------------------------------------------ |
| Setup Scripts      | Run before agent (e.g., `npm install`)     |
| Dev Server Scripts | Start preview server (e.g., `npm run dev`) |
| Cleanup Scripts    | Run after agent (e.g., `npm run format`)   |
| Copy Files         | Files copied to worktree (e.g., `.env`)    |

**Important**: Setup scripts ensure dependencies exist in worktree. Cleanup scripts act like pre-commit hooks.

**Warning**: Ensure copied files are gitignored to avoid accidental commits.

## Creating Tasks

Press `C` or click `+` icon.

### Options

- **Create Task**: Add to board only
- **Create & Start**: Add + immediately execute with default agent

### Task Fields

- Title (required)
- Description (optional, supports markdown; paste preserves inline code and supports raw paste)
- Base branch (defaults to configured target branch)

### Task Tags

Reusable text snippets via `@mention`:

1. Type `@` in description
2. Filter by typing tag name
3. Select tag → content inserted

Manage tags: Settings → General → Task Tags

### Issue Attachments (v0.1.13)

- Image attachments are supported on issues.
- Use inline attachments in descriptions/comments; attachment handling is proxied by the server (ensure proxy routes are enabled for self-hosting).

### Task Columns

| Column      | Trigger                       |
| ----------- | ----------------------------- |
| To do       | Task created                  |
| In Progress | Attempt started               |
| In Review   | Attempt completed             |
| Done        | Merged or PR merged on GitHub |

## Kanban Filters (v0.1.7)

- Per-project Kanban views for tailored boards
- Filter dialog refreshed for faster selection
- Sub-issues and Workspaces visibility toggles moved into the filter bar

## Starting Tasks

1. Open task without attempts
2. Click `+` to create attempt
3. Configure:
   - **Agent profile**: Claude Code, Gemini, Codex, etc.
   - **Variant**: DEFAULT, PLAN, etc.
   - **Base branch**: Branch to work from

## Monitoring Execution

### Execution Flow

1. **Setup Script** runs (if configured)
2. **Task sent to agent** (title + description)
3. **Real-time actions** displayed:
   - Reasoning
   - Commands
   - File operations
   - Tool usage
4. **Action approvals** (Codex; Claude Code coming soon)
5. **Cleanup Script** runs
6. **Commit generated** (auto-message from agent's last message)

### Interaction During Execution

| Action               | How                         |
| -------------------- | --------------------------- |
| Send message         | `⌘/Ctrl + Enter`            |
| New line             | `Enter`                     |
| Switch agent profile | `Shift + Tab`               |
| View task details    | Click task title (top left) |

### Edit Previous Messages

Supported by: Claude Code, Amp, Codex, Gemini, Qwen

**Warning**: Editing reverts all subsequent agent work.

## Testing Your Application

Preview Mode — embedded browser for web apps.

### Setup

1. Configure dev server script in project settings
2. Install Web Companion (optional, for component selection):

```bash
npm install vibe-kanban-web-companion
```

Add to app:

```javascript
import { VibeKanbanWebCompanion } from 'vibe-kanban-web-companion';

// In React root
<VibeKanbanWebCompanion />
<App />
```

### Using Preview

1. Click "Start Dev Server" in Preview tab
2. App loads in iframe
3. Dev server logs shown at bottom
4. Toolbar: Refresh, Copy URL, Open in Browser, Stop

### Component Selection

With Web Companion installed:

1. Click floating Vibe Kanban button
2. Click component to select
3. Choose depth (inner/outer)
4. Add follow-up message — agent knows exactly which component

## Reviewing Code Changes

1. Task moves to "In Review" when agent finishes
2. Click **Diff** icon to view changes
3. Click `+` on line to add comment
4. Write feedback
5. Click **Send** to submit all comments
6. Task returns to "In Progress"

Comments sent as single message to agent.

## Completing a Task

### Git Operations Header

Shows:

- Task branch
- Target branch (with change option)
- Commits ahead/behind

### Actions

| Button    | Action                              |
| --------- | ----------------------------------- |
| Merge     | Merge to target branch, task → Done |
| Create PR | Open PR on GitHub/Azure             |
| Rebase    | Update branch with target changes   |
| Push      | Push new changes to existing PR     |

**Guardrails**: Merge actions are disabled when an open PR exists or when the target is remote-only.

Rebase dialog reflects the current target branch; verify it before rebasing.

### Pull Request Flow

1. Click "Create PR"
2. Title/description pre-filled from task
3. After creation, button becomes "Push" (disabled until new changes)
4. When PR merged on GitHub, task auto-moves to Done
