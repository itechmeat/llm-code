# ZCode Internals, Data Model, and Troubleshooting

Everything here was verified against a live ZCode install (app 3.3.4, bundled CLI
0.15.2, GLM-5.2). Paths are macOS defaults.

## Layout on disk

- App bundle: `/Applications/ZCode.app`
- Headless CLI (Node): `/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs`
- Curated model catalog: `.../Contents/Resources/model-providers/`
- Shared data store (GUI and CLI both use it): `~/.zcode/cli/`
  - Session DB: `~/.zcode/cli/db/db.sqlite` (WAL mode)
  - Structured event log: `~/.zcode/cli/log/zcode-YYYY-MM-DD.jsonl`
- GUI profile: `~/.zcode/v2/` (`config.json` with provider block + `credentials.json`)

The GUI and the headless CLI write the same `~/.zcode/cli/` store, so a digest
built from that DB reflects exactly what the GUI produced.

## The captcha gate (why headless model calls fail)

The signed-in "coding plan" provider points at
`https://zcode.z.ai/api/v1/zcode-plan/anthropic`. Any endpoint whose path ends in
`/zcode-plan` is gated by an interactive Aliyun captcha (request header
`x-aliyun-captcha-verify-param`, protocol step `captcha-retry`). Headless
`zcode.cjs -p` cannot solve it and returns `403 code 3007 captcha verify failed`.
The app webview solves it, so driving the app is the working path.

An ordinary API-key endpoint (`https://api.z.ai/api/anthropic`) is NOT gated, so a
standalone API key would allow true headless use. This skill intentionally avoids
that to reuse the existing logged-in plan.

## Headless CLI config (for reference only)

The CLI reads `~/.zcode/cli/config.json` with a different shape than the GUI's
`~/.zcode/v2/config.json`:

- `provider`: map of provider blocks (only include entries with a non-empty
  `apiKey`; empty `apiKey:""` entries fail Zod validation and drop the whole file).
- `model`: a string reference `"<providerId>/<modelId>"` (for example
  `"builtin:zai-start-plan/GLM-5.2"`), or `{ "main": "...", "lite": "..." }`. It
  must be a string ref, not an object descriptor.

This is only useful for non-model CLI commands (`doctor`, `skills list --json`,
`plugins list --json`), which run without hitting the captcha.

## Driving the Electron UI

- Cold-start the app with `--remote-debugging-port=<port>`. The flag only takes
  effect at launch; if the app is already running, quit and relaunch it.
- Find the renderer target via `GET http://127.0.0.1:<port>/json` and pick the
  `type:"page"` whose URL contains `index.html`. Connect agent-browser to that
  page's `webSocketDebuggerUrl`, not the browser-level endpoint (the browser
  endpoint lands on a blank tab).
- The UI is rendered in **Shadow DOM** (web components). `querySelectorAll` and
  accessibility snapshots see nothing; you must recurse into `el.shadowRoot`.
  `document.body.innerText` still returns composed text, which is handy for a
  quick read.
- Chat input is a `div[role="textbox"]` (a Lexical editor). It ignores
  `execCommand`; use CDP `Input.insertText` (agent-browser `keyboard inserttext`)
  after focusing it. Submit by clicking the button whose `aria-label`/`title` is
  `Send`, or the app shortcut. New task is the `Cmd+N` shortcut.
- **Screenshots via CDP are black** when the window is occluded or unfocused.
  Rely on DOM text and the DB, not images.
- Each agent-browser CLI call is a separate process and the tracked target can
  revert to `about:blank`; reconnect to the page before each action.

## Session DB schema (the audit surface)

Key tables in `~/.zcode/cli/db/db.sqlite`:

- `message` (`id`, `session_id`, `time_created`, `time_updated`, `data` JSON).
  The `data` blob for an assistant message carries `role`, `modelID`,
  `providerID`, `mode`, `agent`, `finish` (finish reason), `error`, `tokens`
  (`total`/`input`/`output`/`reasoning`/`cache`), `cost`.
- `part` (`message_id`, `session_id`, `data` JSON). Content by step:
  `step-start`, `step-finish`, `text`, and tool parts. The last `type:"text"`
  part is the final answer.
- `tool_usage`: one row per tool call with rich telemetry: `tool_name`,
  `read_only`, `destructive`, `approval_status`, `status`, `exit_code`,
  `started_at`, `completed_at`, `duration_ms`, `output_bytes`, `stdout_bytes`,
  `stderr_bytes`, `retry_count`, `cancelled_by_user`, `error_type`,
  `error_code`, `error_message`. This answers "what did it run, did it succeed,
  was anything destructive or blocked".
- Also present: `turn_usage`, `todo`, `permission`, `session_target`,
  `workflow_run`/`workflow_event`/`workflow_definition`, `input_history`.

`~/.zcode/v2/tasks-index.sqlite` holds the task/group index (`tasks`,
`task_groups`, ...); it is not needed for result digests.

## Completion signals

- DB (session-scoped, preferred): an assistant `message` for the session whose
  `data.finish` is set (for example `stop`), with `time_updated` at or after
  dispatch.
- Event log (global): a `turn.completed` line in the JSONL, carrying `queryId`,
  `turnNumber`, `toolCallCount`. Good for a global counter, weaker for
  correlation across concurrent tasks.
- Approval pause: in `build`/`plan` mode a tool call parks for approval. Detect
  it via `tool_usage.approval_status` (best-effort) or the in-app approve UI.
  This is not completion.

## Ground truth for changes

The digest reports what the agent recorded. To know what actually changed on
disk, diff the workspace: `git -C <workspace> diff --stat` (and `git status`
for untracked files). Cross-check against `tool_usage.destructive`.

## Common failures

- `captcha verify failed` (headless): expected; use the app path.
- `Model config is missing`: the CLI has no valid `~/.zcode/cli/config.json`
  (only relevant to headless non-model commands).
- Blank/`about:blank` reads: agent-browser attached to the wrong target;
  reconnect to the page `webSocketDebuggerUrl`.
- Empty selectors: the UI is in Shadow DOM; recurse into shadow roots.
- Black screenshots: window occlusion; do not use screenshots for state.
