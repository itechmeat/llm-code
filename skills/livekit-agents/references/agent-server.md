# Agent Server

## What it is

The Agent Server architecture is how LiveKit runs and scales many concurrent agent sessions (or other “programmatic participants”) reliably.

## Why you use it

- Run multiple concurrent jobs with lifecycle management and cleanup.
- Dispatch agents to rooms automatically or explicitly.
- Horizontal scaling and load balancing for agent workloads.

## Programmatic participants (not only AI)

- Any code that joins a LiveKit room as a participant to process realtime media/data:
  - audio analysis
  - video processing/moderation
  - data routing/aggregation
  - bridges to external APIs/databases

## Core concepts

- **Dispatch**: how work is assigned to an agent/job and which room it joins.
- **Job lifecycle**: entrypoint execution, session management, shutdown/cleanup.
- **Server options**: permissions, dispatch rules, initialization (prewarm), behavior.

## Startup modes (CLI)

Docs describe a CLI-driven server that can run in multiple modes:

- `start`: production mode (INFO logging by default, graceful shutdown/drain, production optimizations).
- `dev`: development mode (DEBUG logging, auto-reload).
- `console` (Python-only): local single-session testing without connecting to LiveKit.
- `connect`: single-session mode that connects directly to a specific room (targeted debugging).

### Authentication / env

- Server connection credentials (env vars or CLI args):
  - `LIVEKIT_URL` (`--url`)
  - `LIVEKIT_API_KEY` (`--api-key`)
  - `LIVEKIT_API_SECRET` (`--api-secret`)
- Note: `console` mode doesn’t connect to LiveKit for media, but still needs credentials for LiveKit Inference.

### Graceful shutdown (production)

- On SIGINT/SIGTERM: stop accepting new jobs → wait for active jobs (Python has `--drain-timeout`) → cleanup → exit.

## Download files (plugin assets)

- Some plugins require runtime model/assets (docs mention `turn-detector`, `silero`, `noise-cancellation`).
- `download-files` calls each plugin’s `download-files()` hook; run it in build steps or before first local run.

## Server lifecycle (high level)

- Agent server registers with the LiveKit server, then waits for requests.
- When a user connects to a room, LiveKit dispatches a job request to an available agent server.
- The first available agent server accepts the job and starts a new process to handle it.

### Job isolation + load balancing

- One agent server can run multiple concurrent jobs.
- Each job runs in its own process; a crash should not take down other jobs.
- Agent servers exchange capacity/availability with LiveKit to enable load balancing.

### Shutdown/drain behavior

- Rooms typically close when the last non-agent participant leaves; agents disconnect.
- On deploy/update, agent servers drain active sessions before shutting down to avoid interruptions.

## Agent dispatch

### Automatic dispatch (default)

- By default, an agent is dispatched automatically to each new room.
- Best when you want “same agent joins every room”.

### Explicit dispatch

- Set `agent_name` for an entrypoint/session to require explicit dispatch.
- Important: setting `agent_name` turns off automatic dispatch for that agent — it must be dispatched.

### Ways to dispatch

- Agent Dispatch API / SDKs (AgentDispatchService).
- LiveKit CLI (`lk dispatch create ...`).
- Include agent dispatch in a participant token / room configuration to auto-dispatch on participant connection.
- For inbound SIP calls: use SIP dispatch rules (docs recommend explicit dispatch to support multiple agents in one project).

### Job metadata

- Explicit dispatch can pass `metadata` (string; docs recommend JSON).
- Metadata is available in `JobContext` and is a primary way to pass user info into initial context.

## Job lifecycle (entrypoint + context)

### Entrypoint

- Entrypoint runs as the main function of the process for each job.
- Python: decorated with `@server.rtc_session(...)`.
- Node: `defineAgent({ entry: async (ctx) => ... })`.

### Connection control

- If you use `AgentSession`, it connects automatically on `session.start(...)`.
- If you need precise connection timing (e.g., end-to-end encryption) or you are not using `AgentSession`, call `await ctx.connect(...)` yourself.
- Set up room event listeners before connecting (docs show subscribing handlers before `ctx.connect`).

### `JobContext` fields you’ll use

- `ctx.room`: LiveKit room object (events, remote participants, local participant).
- `ctx.job.metadata`: dispatch metadata string (often JSON).
- `ctx.wait_for_participant()`: wait for a participant.
- Shutdown hooks: `ctx.add_shutdown_callback(...)` / `ctx.addShutdownCallback(...)`.

### Participant attributes / room metadata

- Use participant attributes for user settings (e.g., language); listen for attribute changes if needed.

### Shutdown patterns

- Jobs run until all standard/SIP participants leave or you explicitly shutdown.
- `shutdown(drain=True)` drains pending speech (graceful).
- `aclose()` closes immediately (awaitable).

### Shutdown hooks and timeouts

- Shutdown hooks should finish quickly.
- Docs mention a default ~10s wait before process termination; configurable via `shutdown_process_timeout` in server options.

## Server options (what matters in production)

### Permissions

- Configure what the worker can do (publish/subscribe/publish data/update metadata, etc.).
- `hidden=true` hides the agent participant (and implies it cannot publish tracks because it’s not visible).

### Draining / shutdown

- `drain_timeout`: max time to wait for active jobs to finish after SIGTERM/SIGINT.
  - Docs: default is 30 minutes.

### Load reporting and availability

- Server reports load via `load_fnc` / `loadFunc` (returns 0..1).
- Default load function: average CPU utilization over a 5-second window.
- `load_threshold`: above this, server is marked unavailable for new jobs.
  - Docs: default 0.7.

### Prewarm / setup

- `setup_fnc` (Python) / `prewarm` (Node) runs before jobs to load heavy assets once per worker process.
- Store artifacts in `proc.userdata` / `proc.userData`, then read them in the job entrypoint.

### Agent naming + job type

- `agent_name` / `agentName`: used for explicit dispatch.
- Server type:
  - `ROOM`: new instance per room.
  - `PUBLISHER`: new instance per publisher in the room.

### Security note (docs)

- Prefer API key/secret via environment variables rather than embedding them in `ServerOptions`.
