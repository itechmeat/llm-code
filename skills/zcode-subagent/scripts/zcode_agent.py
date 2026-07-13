#!/usr/bin/env python3
"""Orchestrate the ZCode (z.ai) desktop app as a subagent over Chrome DevTools Protocol.

Dispatches a prompt into the running ZCode Electron app, waits for the turn to
finish, and prints a compact JSON result digest read from ZCode's local SQLite
session store. Deliberately avoids screenshots and full-transcript scraping so the
caller spends a fixed, tiny number of tokens regardless of how long the agent ran.

Why the app path (not headless): the ZCode "coding plan" endpoint gates model
requests behind an interactive captcha that only the app's webview can solve, so
`zcode -p` fails headless. Driving the app reuses the already-solved captcha and
needs no API key. See ../references/architecture.md.

Subcommands:
  run     send + wait + digest in one shot (the common case)
  send    send a prompt (new task or --follow) and print the target session id
  wait    block until the turn finishes, awaits approval, or the backend fails
  digest  print a compact JSON digest of a session's latest result
  errors  print recent backend failures (HTTP status, retryable) from the log
  state   print 'running' or 'idle' for the current turn
  mode    print or set the autonomy mode (Ask before changes | Edit automatically
          | Plan mode | Full access)
  workspace  print the open workspace directory, or switch to a registered one
  approve    click a pending permission popup (prefers 'always allow')

Examples:
  python3 zcode_agent.py mode --set "Full access"    # hands-off, no prompts
  python3 zcode_agent.py run "Refactor the parser and run the tests"
  python3 zcode_agent.py run --follow "Now add a test for the empty-input case"
  python3 zcode_agent.py send --new "..."            # prints session id only
  python3 zcode_agent.py digest --session sess_abc123
  python3 zcode_agent.py errors --session sess_abc123 # why did a turn stall?

Requires: ZCode.app (logged in), node, agent-browser, python3, curl (macOS: open,
osascript). See ../references/installation.md.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sqlite3
import sys
import time
import urllib.request

APP_NAME = "ZCode"
DEFAULT_PORT = 9333
AB_SESSION = "zcode"  # isolate our agent-browser session from other CDP work
HOME = os.path.expanduser("~")
DB_PATH = os.path.join(HOME, ".zcode", "cli", "db", "db.sqlite")
LOG_DIR = os.path.join(HOME, ".zcode", "cli", "log")

# Autonomy modes offered by the composer's "Switch mode" control. Hands-off bulk
# work wants "Full access" so per-command permission prompts never appear; the
# in-UI approval popups are unreliable to click over CDP.
MODES = ("Ask before changes", "Edit automatically", "Plan mode", "Full access")

# --- JavaScript run inside the ZCode renderer (UI lives in Shadow DOM) ---------
_WALK = (
    "const w=(r)=>{r.querySelectorAll('*').forEach(el=>{CB;"
    "if(el.shadowRoot)w(el.shadowRoot);});};w(document);"
)
JS_FOCUS_EDITOR = (
    "(()=>{let ed=null;" + _WALK.replace(
        "CB", "if(!ed&&el.getAttribute&&el.getAttribute('role')==='textbox')ed=el")
    + "if(ed){ed.focus();return 'ok';}return 'no';})()"
)
JS_READ_EDITOR = (
    "(()=>{let ed=null;" + _WALK.replace(
        "CB", "if(!ed&&el.getAttribute&&el.getAttribute('role')==='textbox')ed=el")
    + "return ed?ed.innerText:'';})()"
)
def _js_click(label):
    return (
        "(()=>{let b=null;" + _WALK.replace(
            "CB",
            "const l=el.getAttribute&&(el.getAttribute('aria-label')||el.getAttribute('title'));"
            "if(!b&&(el.tagName==='BUTTON'||(el.getAttribute&&el.getAttribute('role')==='button'))"
            "&&l&&l.trim()===LABEL)b=el").replace("LABEL", json.dumps(label))
        + "if(!b)return 'NOT_FOUND';b.click();return 'clicked';})()"
    )


JS_CLICK_SEND = _js_click("Send")
JS_CLICK_QUEUE = _js_click("Queue message")
JS_CLICK_NEW = _js_click("New task")

# A turn is running when the composer shows "Queue message" (instead of "Send")
# or a "Stop" button is present; otherwise the app is idle.
JS_STATE = (
    "(()=>{let r=false;" + _WALK.replace(
        "CB",
        "if(!r){const l=((el.getAttribute&&(el.getAttribute('aria-label')||el.getAttribute('title')))||'').toLowerCase();"
        "const b=(el.tagName==='BUTTON'||(el.getAttribute&&el.getAttribute('role')==='button'));"
        "const t=b?(el.innerText||'').trim().toLowerCase():'';"
        "if(/queue message/.test(l)||l==='stop'||t==='stop')r=true;}")
    + "return r?'running':'idle';})()"
)
# Current autonomy mode: read the "Switch mode" control's composed text.
JS_READ_MODE = (
    "(()=>{let b=null;" + _WALK.replace(
        "CB",
        "const l=((el.getAttribute&&(el.getAttribute('aria-label')||el.getAttribute('title')))||'');"
        "if(!b&&/switch mode/i.test(l))b=el;")
    + "return b?(b.innerText||'').replace(/\\s+/g,' ').trim():'';})()"
)
def _js_open_switch_mode():
    return (
        "(()=>{let b=null;" + _WALK.replace(
            "CB",
            "const l=((el.getAttribute&&(el.getAttribute('aria-label')||el.getAttribute('title')))||'');"
            "if(!b&&/switch mode/i.test(l))b=el;")
        + "if(!b)return 'NOT_FOUND';b.click();return 'opened';})()"
    )
def _js_pick_mode(name):
    return (
        "(()=>{let o=null;" + _WALK.replace(
            "CB",
            "const r=el.getAttribute&&el.getAttribute('role');"
            "const t=(el.innerText||'').trim();"
            "if(!o&&(r==='option'||r==='menuitem'||r==='menuitemradio')&&t.toLowerCase().indexOf(NAME)>=0)o=el;")
        .replace("NAME", json.dumps(name.lower()))
        + "if(!o)return 'NO_OPTION';o.click();return 'picked';})()"
    )


def die(msg):
    print("error: " + msg, file=sys.stderr)
    sys.exit(1)


def now_ms():
    return int(time.time() * 1000)


# --- agent-browser resolution -------------------------------------------------
def resolve_ab():
    """Return the argv prefix for agent-browser, tolerating a broken PATH symlink."""
    onpath = shutil.which("agent-browser")
    if onpath:
        return [onpath]
    try:
        root = subprocess.check_output(["npm", "root", "-g"], text=True).strip()
    except Exception:
        root = None
    if root:
        sysname = "darwin" if sys.platform == "darwin" else "linux"
        arch = "arm64" if platform.machine() in ("arm64", "aarch64") else "x64"
        cand = os.path.join(root, "agent-browser", "bin", f"agent-browser-{sysname}-{arch}")
        if os.path.exists(cand):
            return [cand]
        js = os.path.join(root, "agent-browser", "bin", "agent-browser.js")
        if os.path.exists(js):
            return ["node", js]
    die("agent-browser not found. Install: npm i -g agent-browser && agent-browser install")


AB = None  # populated in main()


def ab(*args, capture=True):
    return subprocess.run(AB + ["--session", AB_SESSION, *args],
                          capture_output=capture, text=True)


def ev(js):
    """Run JS in the connected page; parse the JSON-encoded return when possible."""
    out = ab("eval", js).stdout.strip()
    try:
        return json.loads(out)
    except Exception:
        return out


# --- CDP / app lifecycle ------------------------------------------------------
def cdp_alive(port):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3)
        return True
    except Exception:
        return False


def page_ws(port):
    try:
        data = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=4))
    except Exception:
        return None
    for t in data:
        if t.get("type") == "page" and "index.html" in t.get("url", ""):
            return t.get("webSocketDebuggerUrl")
    return None


def app_running():
    if sys.platform != "darwin":
        return False
    r = subprocess.run(
        ["osascript", "-e",
         'tell application "System Events" to (name of processes) contains "ZCode"'],
        capture_output=True, text=True)
    return r.stdout.strip() == "true"


def ensure_app(port):
    """Guarantee ZCode is running with CDP exposed on `port`."""
    if cdp_alive(port):
        return
    if sys.platform != "darwin":
        die(f"start ZCode with --remote-debugging-port={port} (auto-launch is macOS-only)")
    if app_running():
        # Running without the debug flag: the flag only applies at cold start.
        subprocess.run(["osascript", "-e", 'quit app "ZCode"'])
        time.sleep(4)
    subprocess.run(["open", "-a", APP_NAME, "--args", f"--remote-debugging-port={port}"])
    for _ in range(25):
        time.sleep(1)
        if cdp_alive(port) and page_ws(port):
            return
    die(f"ZCode did not expose CDP on port {port}")


def connect_page(port):
    """(Re)attach agent-browser to the ZCode renderer page (not the browser target)."""
    ws = page_ws(port)
    if not ws:
        die("ZCode renderer page not found over CDP")
    ab("connect", ws)


# --- SQLite (read-only) -------------------------------------------------------
def db():
    if not os.path.exists(DB_PATH):
        die(f"ZCode session DB not found at {DB_PATH}")
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=5)


def q1(sql, params=()):
    c = db()
    try:
        row = c.execute(sql, params).fetchone()
        return row[0] if row else None
    finally:
        c.close()


def qall(sql, params=()):
    c = db()
    try:
        return c.execute(sql, params).fetchall()
    finally:
        c.close()


def newest_session():
    return q1("select session_id from message order by time_created desc limit 1")


# --- backend error detection (event log) --------------------------------------
def latest_log():
    try:
        files = [os.path.join(LOG_DIR, f) for f in os.listdir(LOG_DIR) if f.endswith(".jsonl")]
    except Exception:
        return None
    return max(files, key=os.path.getmtime) if files else None


def scan_errors(session=None, limit=5, tail_bytes=262144):
    """Return recent model/turn failures from the newest event log (tail only, so
    the cost is bounded). These are backend faults - HTTP status like 405/403/429,
    captcha rejections, network errors - that surface as turn.failed. A
    `retryable: false` status will not clear by retrying; escalate to the user."""
    path = latest_log()
    if not path:
        return []
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            if size > tail_bytes:
                f.seek(size - tail_bytes)
                f.readline()  # drop the partial first line
            lines = f.read().decode("utf-8", "ignore").splitlines()
    except Exception:
        return []
    out = []
    for line in lines:
        if ('"turn.failed"' not in line and '"model.request.failed"' not in line
                and '"model.network.failed"' not in line):
            continue
        try:
            j = json.loads(line)
        except Exception:
            continue
        ctx = j.get("context", {}) or {}
        if session and j.get("sessionId") != session and ctx.get("parentSessionId") != session:
            continue
        err = j.get("error", {}) or {}
        ectx = err.get("context", {}) or {}
        cause = err.get("cause", {})
        while isinstance(cause, dict) and isinstance(cause.get("cause"), dict):
            cause = cause["cause"]
        out.append({
            "ts": j.get("timestamp"),
            "event": j.get("event"),
            "status": ctx.get("statusCode") or ectx.get("statusCode"),
            "retryable": ctx.get("retryable", ectx.get("retryable")),
            "reason": ctx.get("reason") or ectx.get("reason"),
            "message": (cause.get("message") if isinstance(cause, dict) else None)
                       or ctx.get("statusMessage") or err.get("message"),
            "requestId": ctx.get("requestId") or ectx.get("requestId"),
        })
    # newest entries are last in the file
    return out[-limit:]


def ui_state(port):
    """'running' if a turn is in flight, else 'idle'."""
    connect_page(port)
    return ev(JS_STATE)


def read_mode(port):
    connect_page(port)
    return ev(JS_READ_MODE)


def set_mode(port, name):
    """Set the composer autonomy mode (case-insensitive substring of a MODES entry).
    Returns the mode string after the change."""
    connect_page(port)
    if ev(_js_open_switch_mode()) != "opened":
        die("could not open the Switch mode control")
    time.sleep(0.8)
    connect_page(port)
    r = ev(_js_pick_mode(name))
    if r != "picked":
        ab("press", "Escape")
        die(f"mode option matching {name!r} not found")
    time.sleep(0.6)
    ab("press", "Escape")  # close any lingering menu
    connect_page(port)
    return ev(JS_READ_MODE)


def current_workspace():
    """Absolute path of the workspace the newest task is bound to (DB truth)."""
    return q1("select directory from session where directory is not null "
              "order by time_created desc limit 1")


def set_workspace(port, path):
    """Best-effort switch of the open workspace to `path` via the command palette.
    Only works when `path` is already a registered ZCode project (its folder was
    opened before); opening a brand-new folder needs the native picker, which the
    CDP layer cannot drive. Returns 'switched' | 'already' | 'not_registered'.
    The robust, always-available alternative is to put absolute paths in the
    dispatched prompt - ZCode's tools operate on them regardless of the open
    workspace."""
    cur = current_workspace()
    if cur and os.path.abspath(cur) == os.path.abspath(path):
        return "already"
    name = os.path.basename(os.path.abspath(path))
    connect_page(port)
    ab("press", "Meta+k"); time.sleep(1.2); connect_page(port)
    picked = ev(
        "(()=>{let o=null;" + _WALK.replace(
            "CB",
            "const r=el.getAttribute&&el.getAttribute('role');"
            "const t=(el.innerText||'').trim();"
            "if(!o&&(r==='option'||r==='menuitem'||el.tagName==='LI'||r==='button')"
            "&&t.toLowerCase().indexOf(NAME)===0)o=el;").replace("NAME", json.dumps(name.lower()))
        + "if(!o)return 'NO_MATCH';o.click();return 'clicked';})()")
    if picked != "clicked":
        ab("press", "Escape")
        return "not_registered"
    time.sleep(1.0)
    ab("press", "Escape")
    return "switched"


def approve_once(port):
    """Click a pending permission popup, preferring an 'always allow in this
    project / do not ask again' option so the grant persists. Returns what was
    clicked or 'NONE'. Note: 'always allow' is scoped per command/file, so distinct
    later actions re-prompt; for a hands-off run set the mode to Full access
    (a project-wide, permanent grant) instead of clicking each popup."""
    connect_page(port)
    js = (
        "(()=>{const c=[];" + _WALK.replace(
            "CB",
            "if(el.tagName==='BUTTON'||(el.getAttribute&&(el.getAttribute('role')==='button'||el.getAttribute('role')==='menuitem'))){"
            "const l=((el.getAttribute&&(el.getAttribute('aria-label')||el.getAttribute('title')))||'').trim();"
            "const t=(el.innerText||'').trim();const s=(l+' '+t).toLowerCase();"
            "if(/(always allow|allow once|allow this|approve|accept|yes,? (run|proceed|continue)|grant|trust this)/.test(s)"
            "&&!/command palette|search|settings|help/.test(s))c.push([el,(l||t)]);}")
        + "if(!c.length)return 'NONE';"
        "const fav=c.find(x=>/(always|session|don.?t ask|project|forever)/i.test(x[1]));"
        "const p=fav||c[0];p[0].click();return 'CLICKED:'+p[1].replace(/\\s+/g,' ').slice(0,50);})()"
    )
    return ev(js)


# --- actions ------------------------------------------------------------------
def session_ids():
    return {r[0] for r in qall("select distinct session_id from message")}


def do_send(prompt, new, port):
    ensure_app(port)
    connect_page(port)
    if new:
        # The New task button is reliable from any UI state; Cmd+N is not (when the
        # follow-up editor holds focus the shortcut sends a follow-up instead).
        if ev(JS_CLICK_NEW) != "clicked":
            die("New task button not found in the ZCode UI")
        time.sleep(1.5)
        connect_page(port)
    before = session_ids()  # snapshot to detect a freshly created session
    if ev(JS_FOCUS_EDITOR) != "ok":
        die("chat input (role=textbox) not found in the ZCode UI")
    ab("press", "Meta+a")
    ab("press", "Backspace")
    ab("keyboard", "inserttext", prompt)
    got = ev(JS_READ_EDITOR) or ""
    # Compare on a leading slice: the editor may re-render whitespace/newlines.
    head = " ".join(prompt.split())[:40]
    if head and head not in " ".join(got.split()):
        die(f"editor did not accept the prompt (saw: {got!r:.80})")
    start = now_ms()
    # While a turn is in flight the composer shows "Queue message" instead of
    # "Send" (the follow-up is queued, not an error). Fall back to the app's
    # submit shortcut if neither labelled button is found.
    if ev(JS_CLICK_SEND) != "clicked" and ev(JS_CLICK_QUEUE) != "clicked":
        ab("press", "Meta+Enter")
    # Correlate: prefer a session that did not exist before send (new task);
    # otherwise the newest session (follow-up appends to the current one).
    sid = None
    for _ in range(12):
        time.sleep(0.5)
        fresh = session_ids() - before
        if fresh:
            sid = sorted(fresh)[0]
            break
        sid = newest_session()
        if sid and not new:
            break
    return sid, start


def do_wait(session, since_ms, timeout):
    """Block until an assistant turn finishes, awaits approval, or the backend
    starts failing (e.g. HTTP 405/403/429 from the plan endpoint)."""
    deadline = time.time() + timeout
    i = 0
    while time.time() < deadline:
        i += 1
        # Best-effort: a tool call parked for approval (build/plan modes pause here).
        try:
            pend = q1(
                "select count(*) from tool_usage where session_id=? "
                "and approval_status in ('pending','required','awaiting')", (session,))
        except Exception:
            pend = 0
        row = qall(
            "select json_extract(data,'$.finish'), json_extract(data,'$.error') "
            "from message where session_id=? "
            "and json_extract(data,'$.role')='assistant' and time_updated>=? "
            "order by time_updated desc limit 1", (session, since_ms))
        if row:
            finish, err = row[0]
            if finish or err:
                return {"status": "error" if err else "done", "finish": finish, "error": err}
        if pend:
            return {"status": "awaiting_approval", "pending_tools": pend}
        # Every ~10s check the event log for a non-retryable backend failure. When
        # the model endpoint returns 405/403/etc the app writes turn.failed and
        # goes quiet, so waiting on the DB alone would only ever time out.
        if i % 7 == 0:
            errs = scan_errors(session, limit=3)
            hard = [e for e in errs if e.get("retryable") is False]
            if hard:
                return {"status": "backend_error", "errors": hard}
        time.sleep(1.5)
    return {"status": "timeout", "errors": scan_errors(session, limit=3)}


def build_digest(session, final_max=400):
    # Bind the final text to the assistant message itself; a user prompt is also a
    # text part, and may be the newest one if the assistant part has not flushed yet.
    arow = qall("select id, data from message where session_id=? "
                "and json_extract(data,'$.role')='assistant' "
                "order by time_created desc limit 1", (session,))
    mid, m = (arow[0][0], json.loads(arow[0][1])) if arow else (None, {})
    final = ""
    if mid:
        for _ in range(6):  # brief retry: assistant text part can lag the finish flag
            final = q1("select json_extract(data,'$.text') from part "
                       "where message_id=? and json_extract(data,'$.type')='text' "
                       "and json_extract(data,'$.text') is not null "
                       "order by time_created desc limit 1", (mid,)) or ""
            if final:
                break
            time.sleep(0.5)
    tools = qall("select tool_name,status,destructive,exit_code,duration_ms,error_message "
                 "from tool_usage where session_id=? order by started_at", (session,))
    tok = m.get("tokens", {}) if isinstance(m.get("tokens"), dict) else {}
    return {
        "session": session,
        "model": m.get("modelID"),
        "mode": m.get("mode"),
        "finish": m.get("finish"),
        "error": m.get("error"),
        "tokens": tok.get("total"),
        "cost": m.get("cost"),
        "tools": [{"name": t[0], "status": t[1], "destructive": bool(t[2]),
                   "exit": t[3], "ms": t[4], "error": t[5]} for t in tools],
        "final": (final[:final_max] + "…") if len(final) > final_max else final,
        "backend_errors": scan_errors(session, limit=3),
    }


# --- CLI ----------------------------------------------------------------------
def main():
    global AB
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=DEFAULT_PORT, help="CDP debug port")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("send", help="send a prompt; print target session id")
    sp.add_argument("prompt")
    g = sp.add_mutually_exclusive_group()
    g.add_argument("--new", action="store_true", help="start a new task (default)")
    g.add_argument("--follow", action="store_true", help="continue the current session")

    wp = sub.add_parser("wait", help="wait for the current turn to finish")
    wp.add_argument("--session", required=True)
    wp.add_argument("--since", type=int, default=0, help="epoch ms floor for the turn")
    wp.add_argument("--timeout", type=int, default=900)

    dp = sub.add_parser("digest", help="print a compact result digest")
    dp.add_argument("--session", required=True)

    rp = sub.add_parser("run", help="send + wait + digest")
    rp.add_argument("prompt")
    g2 = rp.add_mutually_exclusive_group()
    g2.add_argument("--new", action="store_true")
    g2.add_argument("--follow", action="store_true")
    rp.add_argument("--timeout", type=int, default=900)

    ep = sub.add_parser("errors", help="recent backend failures from the event log")
    ep.add_argument("--session", default=None, help="scope to a session (and its subagents)")
    ep.add_argument("--limit", type=int, default=5)

    sub.add_parser("state", help="print 'running' or 'idle' for the current turn")

    mp = sub.add_parser("mode", help="print the autonomy mode, or set it with --set")
    mp.add_argument("--set", dest="set_to", default=None,
                    help="one of: " + ", ".join(MODES) + " (substring, case-insensitive)")

    kp = sub.add_parser("workspace", help="print the open workspace dir, or switch with --set")
    kp.add_argument("--set", dest="ws_to", default=None,
                    help="absolute path of an already-registered project to switch to")

    sub.add_parser("approve", help="click a pending permission popup (prefers 'always allow')")

    a = p.parse_args()
    AB = resolve_ab()

    if a.cmd == "send":
        sid, _ = do_send(a.prompt, new=not a.follow, port=a.port)
        print(sid or "")
    elif a.cmd == "wait":
        print(json.dumps(do_wait(a.session, a.since, a.timeout), ensure_ascii=False))
    elif a.cmd == "digest":
        print(json.dumps(build_digest(a.session), ensure_ascii=False))
    elif a.cmd == "run":
        sid, start = do_send(a.prompt, new=not a.follow, port=a.port)
        if not sid:
            die("could not correlate a session after send")
        st = do_wait(sid, start, a.timeout)
        dg = build_digest(sid)
        dg["wait"] = st
        print(json.dumps(dg, ensure_ascii=False))
    elif a.cmd == "errors":
        print(json.dumps(scan_errors(a.session, a.limit), ensure_ascii=False))
    elif a.cmd == "state":
        ensure_app(a.port)
        print(ui_state(a.port))
    elif a.cmd == "mode":
        ensure_app(a.port)
        print(set_mode(a.port, a.set_to) if a.set_to else read_mode(a.port))
    elif a.cmd == "workspace":
        if a.ws_to:
            ensure_app(a.port)
            print(set_workspace(a.port, a.ws_to))
        else:
            print(current_workspace() or "")
    elif a.cmd == "approve":
        ensure_app(a.port)
        print(approve_once(a.port))


if __name__ == "__main__":
    main()
