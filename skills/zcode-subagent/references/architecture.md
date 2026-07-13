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
- **The submit button flips to `Queue message` while a turn is running.** So the
  `Send` label is present only when idle; a follow-up sent mid-turn is queued via
  the `Queue message` button. Absence of a `Send` button is a reliable "turn is
  running" signal, alongside a `Stop` button and a `Working for <duration>` label.
- **Autonomy is a combobox** with `aria-label` containing `Switch mode`. Its
  options are `Ask before changes`, `Edit automatically`, `Plan mode`, and
  `Full access` (run with fewer confirmations). Open it, then click the option
  whose `role` is `option`/`menuitem`. Below Full access, tool calls raise a
  numbered permission popup (`Always allow in this project` / `Do not ask again`);
  activating those menu items with a synthetic `.click()` is unreliable (the
  choice frequently does not commit and the popup returns), so prefer Full access
  for unattended runs rather than clicking every popup.
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

## Background subagents

For a large task ZCode spawns its own parallel worker agents. Each runs in a
separate DB session id prefixed `sess_subagent_agent_*`, whose `context` carries
`parentSessionId` pointing back at the top-level session, plus `agentType` (e.g.
`general-purpose`). Their tool calls and `model.request.*` events appear under the
subagent session, not the parent. This is normal orchestration by ZCode - not a
second user task - so scope error/progress scans to the parent session OR its
`parentSessionId` children, and never treat these as a concurrency violation.

## Model request failures (backend / plan)

When the plan backend rejects a request, ZCode logs `model.request.failed` and
`model.network.failed`, then `turn.failed`, in the JSONL event log. The useful
fields live in `context`: `statusCode` (HTTP), `retryable`, `reason`, `requestId`,
`baseURL` (`.../zcode-plan/anthropic`), and the deepest `error.cause.message`
(e.g. `Method Not Allowed`). Observed classes:

- `statusCode: 405`, `retryable: false` - the plan endpoint refuses every request
  after previously succeeding. Seen when the plan session/captcha expires or a
  usage limit trips (it surfaces as 405, not always 429). Retrying does not clear
  it; the app just re-fails and goes quiet. Fix path: relaunch the app to
  re-establish the plan session, else escalate to the user (re-login / captcha /
  plan limit).
- `403` with `code 3007 captcha verify failed` - captcha gate; only the app
  webview can solve it (this is the whole reason for driving the app).
- `429` / `503` / transport errors - usually `retryable:true`; a bounded retry or
  a short wait clears them.

The orchestrator detects these by tailing the newest log file for the three
`*.failed` events rather than polling the model; `retryable:false` means stop and
report, do not loop.

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
