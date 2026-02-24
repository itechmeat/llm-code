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
