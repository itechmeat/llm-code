# Installation and Prerequisites

The orchestrator drives the installed ZCode desktop app; it does not install
ZCode or a model. Verify each tool below and recommend installing any that is
missing rather than installing silently.

## Quick check

```bash
echo "ZCode.app: $([ -d '/Applications/ZCode.app' ] && echo yes || echo MISSING)"
for t in node agent-browser python3 curl; do
  printf '%s: %s\n' "$t" "$(command -v "$t" || echo MISSING)"
done
```

## ZCode desktop app (required)

- Download and install from https://zcode.z.ai (docs: https://zcode.z.ai/en/docs/welcome).
- Launch it once and sign in with Z.AI. The first signed-in run solves the
  Aliyun captcha in the app webview; that solved state is what lets model
  requests succeed. Without a logged-in app, orchestration cannot run.
- No standalone API key is needed when using the logged-in "coding plan".

## agent-browser (required)

Drives the Electron app over Chrome DevTools Protocol.

```bash
npm i -g agent-browser
agent-browser install
```

Gotcha: the global `agent-browser` symlink can point at a stale path and appear
"command not found". The script falls back to the real binary under
`"$(npm root -g)/agent-browser/bin/agent-browser-<os>-<arch>"`, so a broken
symlink is tolerated. To fix the symlink manually, reinstall the global package.

## node (required)

- ZCode and its bundled CLI are Node programs, and agent-browser's `.js`
  dispatcher runs under Node.
- Any recent LTS works. Recommend installing via your version manager (nvm,
  fnm, Homebrew).

## python3 (required)

- Runs `scripts/zcode_agent.py`.
- SQLite access uses the built-in `sqlite3` module, so no external `sqlite3`
  CLI is required (installing the CLI is still handy for manual inspection).

## curl (required)

- Queries the CDP `http://127.0.0.1:<port>/json` endpoint to find the renderer
  page target. Preinstalled on macOS and most Linux distros.

## Platform notes

- macOS: auto-launch and window activation use `open` and `osascript`
  (preinstalled). This is the fully supported platform.
- Linux / Windows: auto-launch is not implemented. Start ZCode manually with
  `--remote-debugging-port=<port>` and pass the same `--port` to the script.
