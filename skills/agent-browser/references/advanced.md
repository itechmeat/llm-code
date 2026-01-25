# Advanced Features

## Cloud Browser Providers (v0.7+)

Connect to Browserbase or Browser Use for remote browser infrastructure:

```bash
# Via -p flag (recommended)
agent-browser -p browserbase open https://example.com
agent-browser -p browseruse open https://example.com

# Via environment variable
export AGENT_BROWSER_PROVIDER=browserbase
agent-browser open https://example.com
```

## Persistent Browser Profiles (v0.7+)

Store cookies, localStorage, and login sessions across browser restarts:

```bash
agent-browser --profile ~/.myapp-profile open myapp.com
# Login persists across restarts
```

## Sessions

Run multiple isolated browser instances with separate cookies, storage, and auth.

```bash
# Named sessions
agent-browser --session agent1 open site-a.com
agent-browser --session agent2 open site-b.com

# List / show sessions
agent-browser session list
agent-browser session
```

### Authenticated Sessions

Headers scoped to specific origin:

```bash
agent-browser open api.example.com --headers '{"Authorization": "Bearer <token>"}'
agent-browser snapshot -i --json
agent-browser click @e2

# Navigate to another domain - headers NOT sent
agent-browser open other-site.com
```

### Save/Load Auth State

```bash
agent-browser state save auth.json    # After login
agent-browser state load auth.json    # Later, skip login
```

## CDP Mode

Connect to an existing browser via Chrome DevTools Protocol.

```bash
# Start Chrome with remote debugging
google-chrome --remote-debugging-port=9222

# Connect once, then run commands without --cdp
agent-browser connect 9222
agent-browser snapshot
agent-browser close

# Or pass --cdp on each command
agent-browser --cdp 9222 snapshot

# Remote WebSocket URL (v0.7+)
agent-browser --cdp "wss://browser-service.com/cdp?token=..." snapshot
```

Use cases: Electron apps, Chrome with remote debugging, WebView2.

## Downloads (v0.7+)

Trigger downloads and wait for completion:

```bash
agent-browser download @e1 ./file.pdf
agent-browser wait --download ./output.zip --timeout 30000
```

## Streaming

Stream browser viewport via WebSocket for live preview or "pair browsing".

```bash
AGENT_BROWSER_STREAM_PORT=9223 agent-browser open example.com
```

Connect to `ws://localhost:9223`.

### Messages

```json
{"type": "frame", "data": "<base64-jpeg>", "metadata": {"deviceWidth": 1280, "deviceHeight": 720}}
{"type": "status", "connected": true, "screencasting": true}
```

### Input Injection

```json
{"type": "input_mouse", "eventType": "mousePressed", "x": 100, "y": 200, "button": "left", "clickCount": 1}
{"type": "input_keyboard", "eventType": "keyDown", "key": "Enter", "code": "Enter"}
{"type": "input_touch", "eventType": "touchStart", "touchPoints": [{"x": 100, "y": 200}]}
```

Modifiers: 1=Alt, 2=Ctrl, 4=Meta, 8=Shift

## Global Options

| Option            | Description                        |
| ----------------- | ---------------------------------- |
| --session <name>  | Use isolated session               |
| --profile <path>  | Persistent browser profile (v0.7+) |
| -p <provider>     | Cloud provider (v0.7+)             |
| --headers <json>  | HTTP headers scoped to origin      |
| --executable-path | Custom browser executable          |
| --json            | JSON output for agents             |
| --full, -f        | Full page screenshot               |
| --headed          | Show browser window                |
| --cdp <port/url>  | CDP connection (port or WebSocket) |
| --args <list>     | Browser launch args (v0.7+)        |
| --user-agent <ua> | Custom User-Agent (v0.7+)          |
| --proxy-bypass    | Proxy bypass list (v0.7+)          |
| --debug           | Debug output                       |
