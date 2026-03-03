# Deployment (overview, pattern, platforms)

This page summarizes the docs under `/deployment/*`.

## Production guidance (high-level)

- You can run Pipecat anywhere that can run Python, but for production client↔server voice, the docs recommend WebRTC transports over raw WebSockets.
- Plan for:
  - A transport service (WebRTC/WebSocket) that can accept connections.
  - A deployment target (VMs, containers, managed services).
  - Docker (common for cloud targets).

## Recommended deployment pattern

The docs describe a common split:

- **Bot** (e.g., `bot.py`): encapsulated agent code + pipeline; accepts connection/session inputs.
- **Runner** (e.g., `bot_runner.py`): small HTTP service that accepts a request (or webhook), prepares transport credentials (e.g., creates a room + token), then spawns a bot process.

Typical runner endpoint:

- `POST /start_bot` → returns JSON with connection details like `room_url` and `token`.

Scaling note:

- Spawning bots as subprocesses is simple for early cloud testing, but may not hold up under load.
- For higher scale, isolate bots with their own resources (containers/VMs) instead of piling subprocesses onto a single host.

Secrets note:

- Keep provider keys in server-side environment variables / secrets (runner and/or bot). Avoid putting provider API keys in the client.

## Platform guides (selected)

### Fly.io

What the docs show:

- `fly.toml` (HTTP service on port 7860), Dockerfile, `.env`, and a `bot_runner.py` that calls the Fly Machines API to spawn bot workers.

Key gotchas:

- Cache model assets (e.g., Silero VAD) in the image to avoid slow cold starts.
- Example mentions 512MB can be “just enough” for VAD; 1GB is safer.
- Spawning machines from an unauthenticated HTTP endpoint can cause uncontrolled costs; lock down / authenticate your start endpoint.

### Modal

What the docs show:

- Deploy a self-hosted OpenAI-compatible LLM service (vLLM example), then deploy a Pipecat FastAPI app on Modal.

Operational notes:

- LLM cold starts can be minutes; warm the service and consider `min_containers=1` to reduce latency.
- Modal apps/logs: use the Modal dashboard to inspect `serve` / `fastapi_app` / `bot_runner` logs.

### Cerebrium

What the docs show:

- `cerebrium init`, configure `cerebrium.toml`, store secrets in the Cerebrium dashboard.
- Deploy an HTTP endpoint and pass Daily `room_url` + `token` into your agent entry.

Latency/scaling note:

- Docs emphasize cold-start performance and the option to run more components locally (LLM/TTS/STT) to reduce voice-to-voice latency.
