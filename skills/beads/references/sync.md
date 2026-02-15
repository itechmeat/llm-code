# Sync & Integration

Git synchronization, sync-branch mode, and external integrations.

## Git Sync Basics

Beads stores issues in `.beads/issues.jsonl` and syncs with git:

```bash
bd sync              # Full sync (import + export + commit)
bd sync --import-only   # Import changes from git only
bd sync --full          # Force full sync
```

## Sync Hooks (v0.50.3)

SyncEngine now supports PullHooks and PushHooks to keep CLI sync behavior consistent across commands. Use hooks for validation or automation during pull/push stages, and re-run `bd sync` after upgrading to ensure the new hook flow is applied.

## Sync Modes

### Default Mode

Issues tracked in main branch:

```bash
bd init
bd sync  # Commits to current branch
```

### Sync-Branch Mode

Issues synced to separate branch (recommended for teams):

```bash
bd init --branch=beads-sync
# or configure later:
bd config set sync.branch beads-sync
```

Benefits:

- Keeps issues out of feature branches
- Reduces merge conflicts
- Cleaner commit history

### Stealth Mode

Local-only, no git commits:

```bash
bd init --stealth
```

## Contributor vs Maintainer

### Contributor Mode

For forked repos — routes issues to separate planning repo:

```bash
bd init --contributor
# Issues go to ~/.beads-planning instead of repo
```

### Maintainer Mode

Auto-detected via SSH URLs or configured:

```bash
git config beads.role maintainer
```

## Conflict Resolution

### 3-Way Merge

Beads uses 3-way merge for sync conflicts:

```bash
bd sync  # Auto-merges when possible
```

### Manual Resolution

When conflicts can't be auto-resolved:

```bash
bd resolve-conflicts  # Interactive resolution
```

### Per-Field Strategies

Configure merge strategies in config:

```yaml
sync:
  conflict_strategy: manual # or: ours, theirs, merge
```

## External Integrations

### GitLab Sync

Bidirectional issue synchronization with GitLab:

```bash
# Setup
bd config set integrations.gitlab.url https://gitlab.com
bd config set integrations.gitlab.token <token>

# Sync commands
bd gitlab sync              # Full bidirectional sync
bd gitlab sync --push       # Push changes to GitLab
bd gitlab sync --pull       # Pull changes from GitLab
bd gitlab status            # Show sync status
bd gitlab projects          # List available projects
```

Configuration:

```yaml
integrations:
  gitlab:
    url: https://gitlab.com
    token: ${GITLAB_TOKEN}
    project_id: 12345
    pull_prefix: "gl-" # Prefix for imported issues
    push_prefix: "" # Prefix for pushed issues
```

Conflict detection runs before push to prevent overwrites.

### Linear Sync

```bash
# Setup
bd config set integrations.linear.api_key <key>

# Sync
bd linear sync --project-id=<id>
bd linear sync --push  # Push changes to Linear
```

Filtering:

```bash
bd linear sync --type=bug --exclude-type=epic
```

### Jira Import

```bash
bd jira import --project=KEY
```

### GitHub

PR status syncing, issue linking via `gh` CLI.

## Daemon & Auto-Sync

### Daemon Mode

Background daemon for auto-sync:

```bash
bd daemon start
bd daemon status
bd daemon stop
```

### Auto-Sync Config

```yaml
daemon:
  auto_start: true
  auto_sync: true
  auto_pull: true
```

### Real-Time Feed

With fsnotify:

```bash
bd activity --watch  # Real-time activity feed
```

## Worktrees

Parallel development with git worktrees:

```bash
bd worktree create feature-x
bd worktree list
```

Issues follow worktree via `.beads/redirect`.

## Federation (Advanced)

Peer-to-peer sync between Beads instances:

```bash
bd federation status
bd federation sync
```

Requires Dolt backend for SQL-based sync.

### Dolt Server Mode

As of v0.49.3, Beads defaults to the embedded Dolt backend; server mode is opt-in for multi-client access. Use `bd doctor --server` to validate server-mode health checks.

## Troubleshooting

### Sync Divergence

```bash
bd doctor --deep  # Check JSONL/SQLite/git consistency
bd doctor --fix   # Auto-fix divergence
```

### Force Push Detection

Beads detects force-pushes and warns:

```bash
bd sync  # Will warn about potential conflicts
```

### Redirect Issues

```bash
bd doctor  # Checks redirect configuration
```

## Configuration Reference

```yaml
sync:
  branch: beads-sync
  remote: origin
  mode: sync-branch # or: default, stealth
  conflict_strategy: merge

daemon:
  auto_start: true
  auto_sync: true
  auto_pull: true

integrations:
  linear:
    api_key: ${LINEAR_API_KEY}
  jira:
    url: https://company.atlassian.net
```
