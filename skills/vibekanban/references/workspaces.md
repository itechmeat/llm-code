# Workspaces (Beta)

New UI mode for multi-repo development, sessions, and improved workflow.

## Overview

Workspaces provide a modern interface for working with AI coding agents:

- **Multi-repo support**: Work across multiple repositories in one workspace
- **Sessions**: Multiple conversation threads per workspace
- **Command Bar**: Keyboard-driven navigation (`Cmd/Ctrl + K`)
- **Workspace Notes**: Document requirements and decisions
- **Integrated Terminal**: PTY-backed terminal with xterm.js

## Creating Workspaces

1. Click `+` in sidebar or use `Cmd/Ctrl + K` → **New Workspace**
2. Select project from dropdown (or create new)
3. Add repositories:
   - Recent repos list
   - Browse disk
   - Create new repo
4. Set target branches for each repo
5. Describe task in chat input
6. Select agent
7. Click **Create**

Workspace auto-creates working branch from target branch.

**Defaults**: Create flow now defaults to the last used project/repo/branch and sets a base target branch automatically. Adjust per repo if needed.

## Create Workspace from PR

Use the **Create Workspace from PR** action to prefill repo and branch context from an existing pull request.

## Remote Routes

Workspaces support remote routes for deep-linking into a specific workspace context.

## Sessions

Conversation threads within a workspace. All sessions share repos and git state.

### When to Create New Sessions

- Work on different parts simultaneously
- Try alternative approaches
- Work around token limits
- Use different agents for different tasks

### Session States

| State           | Meaning                                    |
| --------------- | ------------------------------------------ |
| Running         | Agent actively processing                  |
| Idle            | Waiting for input                          |
| Needs Attention | Agent waiting for approval or has question |

### Creating Sessions

1. Click session dropdown in chat toolbar
2. Select **+ New Session**
3. Provide context about existing work if needed

Sessions maintain independent conversation history.

Session dropdown shows agent icons next to session titles for quick identification.

## Command Bar

Central hub for navigation and actions. Press `Cmd/Ctrl + K`.

## Slash Commands

Type `/` in the chat input to open the slash command menu for quick actions.

### Quick Actions

| Command           | Description               |
| ----------------- | ------------------------- |
| New Workspace     | Create new workspace      |
| Open in IDE       | Open in configured editor |
| Copy Path         | Copy workspace path       |
| Toggle Dev Server | Start/stop dev server     |
| Open in Old UI    | Switch to classic kanban  |
| Settings          | Open application settings |

### Workspace Actions

| Command             | Description            |
| ------------------- | ---------------------- |
| Start Review        | Begin code review      |
| Rename Workspace    | Change name            |
| Duplicate Workspace | Create copy            |
| Pin/Unpin           | Toggle pinned status   |
| Archive/Unarchive   | Move to/from archive   |
| Run Setup Script    | Execute setup script   |
| Run Cleanup Script  | Execute cleanup script |
| Copy Raw Logs       | Copy logs to clipboard |

### Git Actions

| Command              | Description         |
| -------------------- | ------------------- |
| Create Pull Request  | Open PR dialog      |
| Merge                | Merge to target     |
| Rebase               | Rebase onto target  |
| Change Target Branch | Switch merge target |
| Push                 | Push to remote      |

### View Toggles

| Command              | Description     |
| -------------------- | --------------- |
| Toggle Left Sidebar  | Workspace list  |
| Toggle Chat Panel    | Conversation    |
| Toggle Right Sidebar | Details         |
| Toggle Changes Panel | Code changes    |
| Toggle Logs Panel    | Process logs    |
| Toggle Preview Panel | Browser preview |

### Diff Options

| Command                  | Description               |
| ------------------------ | ------------------------- |
| Toggle Diff View Mode    | Unified vs side-by-side   |
| Toggle Wrap Lines        | Line wrapping             |
| Toggle Ignore Whitespace | Hide whitespace changes   |
| Expand/Collapse All      | Expand/collapse all diffs |

## Workspace Notes

Document information in the **Notes** section of right sidebar:

- Task requirements
- Decisions made
- Which session is for what
- Context for future reference

## Interface Guide

### Layout Panels

| Panel         | Position | Content                |
| ------------- | -------- | ---------------------- |
| Left Sidebar  | Left     | Workspace list, search |
| Chat Panel    | Center   | Agent conversation     |
| Right Sidebar | Right    | Git info, Notes, Logs  |
| Changes Panel | Bottom   | Code diffs             |
| Preview       | Bottom   | Dev server preview     |
| Logs          | Bottom   | Process/terminal logs  |

### Workspace List

- Shows active workspace count
- Uses infinite scroll pagination for large lists

### Sidebar Filters & Sorting (v0.1.7)

- Filter by **Project** and **PR status** from the workspace sidebar
- Use **No project** to show unassigned workspaces
- Sorting in the accordion sidebar prioritizes older completed workspaces
- **Needs Attention** includes workspaces with unseen activity

### Branch Search

Search workspaces by branch name in sidebar.

### Drag-and-Drop Images

Drag images directly into chat for context.

## Integrated Terminal

PTY-backed terminal with full shell support:

- Expandable in logs panel
- Shell init scripts supported
- WebSocket reconnection for stability

## Multi-Repo Workspaces

Work across multiple repositories:

- Each repo has independent git state
- Per-repo commands in Command Bar
- Commits behind indicator in git panel

### Per-Repo Actions

| Command             | Description             |
| ------------------- | ----------------------- |
| Copy Repo Path      | Copy specific repo path |
| Open Repo in IDE    | Open just this repo     |
| Repository Settings | Configure repo options  |
| Create PR (repo)    | PR for specific repo    |
| Merge/Rebase (repo) | Operations per repo     |

## Duplicating Workspaces

Use `Cmd/Ctrl + K` → Workspace Actions → **Duplicate Workspace**

Duplicates repos and branch config with fresh conversation.

## Spin Off Workspace

Use **Spin Off Workspace** to create a child workspace from the current one.

## Archiving

Archive completed workspaces:

- Navbar: Click **Archive** button
- Command Bar: Workspace Actions → Archive

View archive at bottom of sidebar. Use **Pin** for important active workspaces.

## Simple IDs

Issues have readable IDs like `BLO-5` for easy reference.
