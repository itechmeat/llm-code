---
name: zcode-subagent
description: "Offload a coding task to the ZCode (z.ai / GLM, 1M context) desktop app as an independent subagent: the work runs on ZCode's quota, not the caller's tokens, and needs no API key. Use when the current agent wants another agent to do coding, to run a task in parallel, or to conserve its own context. Keywords: ZCode, z.ai, GLM, subagent, delegate, offload."
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

## Prerequisites (check first, recommend if missing)

Run the check below. If a tool is missing, recommend installing it (do not install
silently) and point to `references/installation.md`.

```bash
echo "ZCode.app: $([ -d '/Applications/ZCode.app' ] && echo yes || echo MISSING)"
for t in node agent-browser python3 curl; do
  printf '%s: %s\n' "$t" "$(command -v "$t" || echo MISSING)"
done
```

- **ZCode.app** - the z.ai desktop app, installed and signed in. Recommend:
  download from https://zcode.z.ai and log in once (solves the captcha in-app).
- **agent-browser** - drives the Electron app over CDP. Recommend:
  `npm i -g agent-browser && agent-browser install`. Note its PATH symlink is
  sometimes broken; the script resolves the real binary under `npm root -g`.
- **node** - the app and its CLI are Node; also runs agent-browser's dispatcher.
- **python3** - runs the orchestrator script (`sqlite3` is the built-in module).
- **curl** - queries the CDP `/json` endpoint. macOS also uses `open` + `osascript`.

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

## Make results self-summarizing

Because you author the dispatched prompt, end it with a bounded summary
instruction so the `final` field is directly useful and never a wall of text:

> ...When done, finish with a 1-3 line summary: what changed, why, and status.

## Reading the digest

- `finish`: `stop` = clean; `length` = truncated; `error` field set = failed.
- `wait.status`: `done` | `error` | `awaiting_approval` | `timeout`. In `build`/`plan`
  mode ZCode pauses for approval - that is NOT completion; approve in-app or dispatch
  in a mode with fewer confirmations.
- `tools[]`: one row per call - `destructive:true` or non-`ok` `status` is where to
  look. Read-only calls are expected noise.
- Always verify real disk changes with `git diff --stat`, not the agent's claims.

## Critical notes

- **Session correlation** is the one thing to get right for concurrency: capture
  the `session_id` at dispatch (the script does) and scope every wait/digest to it.
  The "newest session" heuristic only holds when one task runs at a time.
- The UI is inside **Shadow DOM**; ordinary selectors and accessibility snapshots
  return nothing. The script pierces shadow roots to find the input and Send button.
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
