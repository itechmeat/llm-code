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
  wait    block until the current turn finishes (or a permission gate appears)
  digest  print a compact JSON digest of a session's latest result

Examples:
  python3 zcode_agent.py run "Refactor the parser and run the tests"
  python3 zcode_agent.py run --follow "Now add a test for the empty-input case"
  python3 zcode_agent.py send --new "..."            # prints session id only
  python3 zcode_agent.py digest --session sess_abc123

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
JS_CLICK_NEW = _js_click("New task")


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
    if prompt.strip() not in got:
        die(f"editor did not accept the prompt (saw: {got!r:.80})")
    start = now_ms()
    if ev(JS_CLICK_SEND) != "clicked":
        die("Send button not found in the ZCode UI")
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
    """Block until an assistant turn finishes, or a tool call awaits approval."""
    deadline = time.time() + timeout
    while time.time() < deadline:
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
        time.sleep(1.5)
    return {"status": "timeout"}


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


if __name__ == "__main__":
    main()
