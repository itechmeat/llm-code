# Gateway operations

`picoclaw gateway` starts the long-running services that make PicoClaw feel like a “daemon”.

## What gateway starts

- Agent loop
- Channel manager (only enabled channels are started)
- Cron service (jobs stored under `workspace/cron/jobs.json`)
- Heartbeat service (periodic prompts)
- Health server
- Optional device monitoring
- Optional voice transcription integration (Groq)

## Health endpoints

When gateway is running:

- `GET http://<host>:<port>/health`
- `GET http://<host>:<port>/ready`

Bind address comes from `gateway.host` and `gateway.port` in config.

Recent releases also surface `server.pid` in health output, which is useful when supervising PicoClaw under service managers or wrapper scripts.

## Debug logs

- `picoclaw gateway --debug`

## Voice transcription (Groq)

If a Groq API key is configured, gateway can attach a Groq transcriber to supported channels (Telegram/Discord/Slack).

The key is detected from:

- legacy `providers.groq.api_key`, or
- a `model_list` entry whose `model` starts with `groq/` and has `api_key`.

## Common operational gotchas

- “No channels enabled”: set `channels.<name>.enabled=true` in config.
- Port conflicts: change `gateway.port` or channel webhook ports.
- External access: binding `gateway.host=0.0.0.0` exposes health endpoints to the network.

## v0.2.2 operational notes

- Gateway startup/path handling was tightened: prefer invoking the binary through the resolved gateway path and pass the config explicitly when you wrap PicoClaw in scripts or service managers.
- Empty-model errors are now clarified; if gateway fails early, verify `agents.defaults.model_name` against configured `model_list` entries before debugging channels.

## v0.2.3 operational notes

- Web gateway hot reload and polling state sync improve operator feedback when config or runtime state changes through the web flow.
- WebSocket traffic can now proxy through the web-server port, which simplifies deployments that only expose one web-facing port.
- Gateway should no longer start if the underlying gateway server is not actually running; treat that as an early failure signal, not a partial-success state.

## v0.2.6 operational notes

- Gateway PID handling now validates ownership/liveness more carefully and cleans stale pid files instead of treating every leftover pid as a live instance.
- If a wrapped/service-managed gateway still refuses to start, inspect the pid file and ownership first; manual pid deletion should be the last resort, not the first step.
- The web UI now derives the WebSocket URL from the browser location instead of backend assumptions, which is the safer behavior behind reverse proxies or browser-facing launchers.
