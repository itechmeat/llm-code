# Troubleshooting

Common issues and solutions.

## Agent Reports Empty Codebase

**Cause**: Git sparse-checkout enabled.

**Solution**: `git sparse-checkout disable`

## Preview Not Loading

**Cause**: Dev server URL not detected.

**Solution**: Ensure dev server prints URL to stdout. Supported formats: `http://localhost:3000`, `https://localhost:3000`, `http://127.0.0.1:3000`

## VSCode Extension Empty

**Cause**: VSCode not opened via Vibe Kanban.

**Solution**: Click "Open in VSCode" from task view — extension requires worktree context.

## Extension Not Loading

**Solutions**:

- Verify installed: search `@id:bloop.vibe-kanban`
- Cursor/Windsurf: Install from Open VSX Registry
- Restart IDE

## Port Conflicts

**Cause**: Agents not cleaning up dev servers.

**Solutions**:

- Use fixed port: `PORT=8080 npx vibe-kanban`
- Kill stale processes manually

## Debug Logs

```bash
RUST_LOG=debug npx vibe-kanban
```

## Database Reset (Nuclear)

**Warning**: Deletes ALL tasks and settings.

| OS      | Path                                                  |
| ------- | ----------------------------------------------------- |
| macOS   | `~/Library/Application Support/ai.bloop.vibe-kanban/` |
| Linux   | `~/.local/share/ai.bloop.vibe-kanban/`                |
| Windows | `%APPDATA%\ai.bloop.vibe-kanban\`                     |

## GitHub CLI Issues

Check: `gh --version` and `gh auth status`. Re-auth: `gh auth login`

## Agent Not Executing

Checks:

1. Agent authenticated externally?
2. Correct agent profile selected?
3. Setup scripts failing?
4. View process logs (triple dot → View Processes)
