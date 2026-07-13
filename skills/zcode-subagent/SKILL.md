---
name: zcode-subagent
description: "Delegate a coding task to a ZCode (GLM) subagent and get the result back. Use when the current agent should hand off or parallelize coding work. Keywords: ZCode, GLM, subagent, delegate, offload."
metadata:
  version: "3.3.4"
  release_date: "2026-07-13"
---

# ZCode Subagent

Lets the current agent call the ZCode (z.ai, GLM engine) desktop app as a coding
subagent: hand it a task, then detect completion and read the result, all from the
shell. The calling agent dispatches a prompt into the app, detects when the turn
finishes, and reads a small structured digest of the result. It never screenshots
or scrapes the full transcript, so the caller spends a fixed, tiny token cost per
task regardless of how long ZCode worked.

## When to use

- You (a parent agent) need to hand a coding task to ZCode and understand the
  outcome cheaply.
- You want ZCode automation without a standalone z.ai API key (the app's
  logged-in "coding plan" is enough).
- You need a follow-up prompt in the same ZCode conversation.

## Why the desktop app, not the headless CLI

ZCode ships a headless CLI (`ZCode.app/Contents/Resources/glm/zcode.cjs -p`), and
it loads and reaches the API. But the "coding plan" endpoint (`.../zcode-plan/...`)
gates every model request behind an interactive Aliyun captcha that only the
app's webview solves, so headless prompts fail with `code 3007 captcha verify
failed`. Driving the app reuses the already-solved captcha and needs no API key.
Non-model CLI commands (`doctor`, `skills list --json`, `plugins list --json`) do
work headless. Full internals: `references/architecture.md`.

## Do not pre-check or pre-install anything

Just run the script. It resolves its own dependencies and fails with a clear,
actionable message naming exactly what is missing. Only when a run actually fails
that way do you diagnose - and even then, confirm the thing is really absent before
installing (never install on a first negative signal). Pre-emptively "checking
prerequisites" wastes turns and, worse, tends to reinstall software that is already
present.

Dependencies (for reference when a run does fail): **ZCode.app** signed in;
**agent-browser** (drives the app over CDP); **node**; **python3**; **curl** (macOS
also uses `open` + `osascript`).

- **agent-browser** is the common false alarm: its PATH symlink is frequently
  broken, so `command -v agent-browser` prints nothing while the package is fully
  installed under `npm root -g` - and the script resolves the real binary there. So
  a bare `command -v` miss is NOT proof it is absent. Only if the script itself
  dies with "agent-browser not found" do you check
  `ls "$(npm root -g)/agent-browser/bin/agent-browser.js"`, and only if that is
  also missing recommend `npm i -g agent-browser && agent-browser install` (do not
  install silently). See `references/installation.md`.
- **ZCode.app** missing/not signed in: download from https://zcode.z.ai and log in
  once (that solves the captcha in-app).

Only macOS auto-launch is implemented. On other platforms, start ZCode manually
with `--remote-debugging-port=<port>` and pass `--port`.

## The recipe (three cheap layers)

1. **Dispatch** a prompt into the app (new task or follow-up).
2. **Wait for free**: block in the shell until the turn finishes; do not re-read
   the screen. Completion is a DB fact (`message.finish` is set) or the structured
   event `turn.completed` in the JSONL log.
3. **Digest**: read one compact JSON record from the local session DB - model,
   finish reason, tokens, one row per tool call, and the final text. Cross-check
   file changes with `git -C <workspace> diff --stat` (ground truth).

Escalate to expensive detail (a failing tool's stderr, `git diff <file>`) ONLY
when the digest flags a problem (error, destructive edit, unexpected diff).

## Usage

One shot (dispatch + wait + digest):

```bash
python3 scripts/zcode_agent.py run "Refactor the parser and run the tests"
```

Follow-up in the same conversation:

```bash
python3 scripts/zcode_agent.py run --follow "Now add a test for empty input"
```

Split control (capture the session id, then wait/digest yourself):

```bash
SID=$(python3 scripts/zcode_agent.py send --new "Fix the flaky test")
python3 scripts/zcode_agent.py wait   --session "$SID" --timeout 900
python3 scripts/zcode_agent.py digest --session "$SID"
```

Sample digest (bounded regardless of run length):

```json
{"session":"sess_3de8a03","model":"GLM-5.2","mode":"build","finish":"stop",
 "tokens":11048,"tools":[],"final":"PONG-PONG-PONG",
 "wait":{"status":"done","finish":"stop"}}
```

## Point ZCode at the right directory

Every task is bound to the workspace folder open at dispatch (ZCode derives a
project from that directory; a new task inherits it). Check and, when possible,
switch it:

```bash
python3 scripts/zcode_agent.py workspace                 # print the open dir
python3 scripts/zcode_agent.py workspace --set /abs/path  # switch to a registered project
```

`--set` works only when that folder is an already-registered ZCode project
(previously opened) - it switches via the command palette. Opening a brand-new
folder is "Open workspace" (Cmd+O), which is a native OS picker the CDP layer
cannot drive; if the target has never been opened, ask the user to open it once.

The robust, always-available approach that needs no switching: put ABSOLUTE paths
in the prompt you dispatch. ZCode's edit/read tools act on absolute paths
regardless of the open workspace, so you can direct work into any directory. Prefer
switching the workspace when you also need the agent's own file search / `@`
mentions / relative tooling to target that tree.

## Autonomy modes and approvals

The composer has a "Switch mode" control with four autonomy levels: **Ask before
changes**, **Edit automatically**, **Plan mode**, and **Full access** (run with
fewer confirmations). For hands-off or bulk work, set Full access up front:

```bash
python3 scripts/zcode_agent.py mode              # read current mode
python3 scripts/zcode_agent.py mode --set "Full access"
```

Why this matters: in any mode below Full access, a tool call parks for per-command
permission (a numbered "Always allow in this project / Do not ask again" popup).
That "always allow" is scoped to the exact command or file, so the next distinct
action prompts again - the popup keeps returning and a long job crawls. Full access
sets a project-wide, persistent grant (stored as permission mode `yolo`), which is
the correct way to "approve forever". Setting it once covers the whole run.

If policy forbids Full access, you must approve each popup yourself:

```bash
python3 scripts/zcode_agent.py approve    # clicks a pending popup, prefers "always allow"
```

Poll `approve` while the turn runs. Expect to call it repeatedly (once per distinct
command/file) and accept a slower run - this is exactly the friction Full access
removes.

## Orchestrate cheaply

You are only the orchestrator; ZCode spends the task tokens, not you. Keep your own
cost flat:

- Poll sparingly. Use `wait` (it blocks server-side) or space checks tens of
  seconds apart - do not spin.
- Read state from the DB/log, never the screen: `state` (running vs idle),
  `errors` (backend failures), `digest` (result). Never screenshot or scrape the
  transcript.
- Judge real progress by ground truth on disk (`git diff --stat` / your own file
  scan), not by turn signals. On a large task the top-level turn often ends after
  planning while ZCode's own background subagents keep editing.

## Make results self-summarizing

Because you author the dispatched prompt, end it with a bounded summary
instruction so the `final` field is directly useful and never a wall of text:

> ...When done, finish with a 1-3 line summary: what changed, why, and status.

## Reading the digest

- `finish`: `stop` = the turn is done; `tool-calls` = the turn ended mid-loop and
  the agent intends to continue (send a short `--follow` "continue" to resume, or
  wait if background subagents are still active); `length` = truncated; `error`
  field set = failed.
- `wait.status`: `done` | `error` | `awaiting_approval` | `backend_error` |
  `timeout`. `awaiting_approval` means a permission popup is blocking (raise the
  mode to Full access, see above). `backend_error` means the model endpoint is
  failing - see the next section.
- `backend_errors`: recent model/turn failures from the event log (also via the
  `errors` command). Non-empty with `retryable:false` is a hard stop, not noise.
- `tools[]`: one row per call - `destructive:true` or non-`ok` `status` is where to
  look. Read-only calls are expected noise.
- Always verify real disk changes with `git diff --stat`, not the agent's claims.

## When the backend fails (detect, retry, or escalate)

ZCode's plan endpoint can start rejecting every request mid-task. The app writes
`turn.failed` / `model.request.failed` to its event log and then goes quiet, so a
DB-only `wait` would just time out with no explanation. Detect it explicitly:

```bash
python3 scripts/zcode_agent.py errors --session "$SID"
```

Each entry carries an HTTP `status`, a `retryable` flag, and the cause `message`.
Handle by class:

- **Transient / `retryable:true`** (e.g. `429`, `503`, network blips): wait and
  re-dispatch the same `--follow` once or twice; the app also retries internally.
- **`retryable:false`** (e.g. `405 Method Not Allowed`, `403 captcha`, an expired
  or exhausted plan session): retrying will not help. Try one cheap self-fix -
  quit and relaunch ZCode so it re-establishes the plan session and re-solves the
  captcha (the script relaunches with the debug flag on the next call) - then
  re-check `errors`. If it still fails, STOP and tell the user plainly: the ZCode
  backend is returning `<status> <message>`, which needs their action
  (re-login / solve the captcha in-app / check the coding-plan limit). Do not
  loop retrying a non-retryable failure.

## Critical notes

- **Session correlation** is the one thing to get right: capture the `session_id`
  at dispatch (the script does) and scope every wait/digest/errors to it. Run one
  top-level task at a time - do not dispatch a second concurrent task, since the
  "newest session" heuristic breaks. ZCode spawning its OWN background subagents
  (`sess_subagent_*`) for a large task is expected and fine; that is not a second
  top-level task and needs no action from you.
- **"Send" becomes "Queue message" while a turn is running.** A `--follow` sent
  during an active turn is queued, not lost, and looking for a "Send" button will
  fail - that means the turn is still running, not that something broke. Use
  `state` to tell running from idle before deciding to nudge.
- The UI is inside **Shadow DOM**; ordinary selectors and accessibility snapshots
  return nothing. The script pierces shadow roots to find the input, buttons, and
  the mode control.
- **CDP screenshots come back black** when the window is unfocused/occluded - do
  not rely on them. Read the DOM text or the DB instead.
- Each `agent-browser` call is a fresh process; the target can slip to
  `about:blank`. The script reconnects to the ZCode page before acting.
- The app must be launched with `--remote-debugging-port` at cold start; if it is
  already running without it, the script quits and relaunches it.
- ZCode's GUI and headless CLI share one store at `~/.zcode/cli/` (DB + JSONL log),
  so the digest sees exactly what the GUI produced.

## Links

- [ZCode docs](https://zcode.z.ai/en/docs/welcome)
- [z.ai](https://z.ai)
- Installation and prerequisites: `references/installation.md`
- Internals, data model, troubleshooting: `references/architecture.md`
