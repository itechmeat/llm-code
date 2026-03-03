# Get started

## What LiveKit Agents is

- Framework for realtime voice/video (and physical) AI agents.
- Your agent runs as a realtime participant in a LiveKit room, receiving/sending audio/video/data.
- SDKs: Python and Node.js, plus a browser-based Agent Builder for quick prototyping.

## How it fits into LiveKit

- Transport: LiveKit WebRTC between frontend clients and agents.
- Agents join the same room as users; they can consume user media and publish responses.
- Optional telephony/SIP lets users join via phone instead of a web/mobile app.

## Core components (mental model)

- **Agent Server**: manages starting/stopping agents, scaling, and dispatching work.
- **Job**: a subprocess started by the Agent Server; it joins a target room and acts as the agent participant.
- **Pipelines**: typical voice pipeline is STT → LLM → TTS; extended with nodes, hooks, tools, and multimodal inputs.
- **Logic primitives**: sessions, tasks/task-groups, workflows, tool definitions.

## Typical production flow

1. Agent Server runs (cloud or self-hosted).
2. A dispatch request targets a specific room / job type.
3. Agent Server spawns a job subprocess.
4. The job joins the LiveKit room and exchanges realtime media/data with clients.
5. When the job ends, the server cleans up lifecycle and resources.

## Vocabulary you will see everywhere

- `room`, `participant`, `job`, `dispatch`
- `pipeline node`, `hook`, `tool`, `tool call`, `plugin`
- `agent session`, `task`, `workflow`
- `turn detection`, `interruptions`, `handoffs`

## Voice AI quickstart (practical checklist)

### Prerequisites

- LiveKit Cloud project (or your own LiveKit server).
- LiveKit credentials in env:
  - `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `LIVEKIT_URL`
- Model/provider keys as needed (commonly `OPENAI_API_KEY`).
- Toolchain + package installation: see `references/installation.md`.

### Run modes you will use

- `download-files`: fetch local model assets used by some plugins/extras.
- `console` (Python-only): local terminal audio I/O for fast iteration.
- `dev`: connect to LiveKit and join rooms for development.
- `start`: production entrypoint (often paired with Agent Server/cloud deploy).

### Common pitfalls

- Link your LiveKit Cloud project in CLI before cloud deploy (`lk cloud auth`).
- If self-hosting, avoid assuming cloud-only plugins (e.g., “enhanced noise cancellation”);
  configure provider plugins explicitly.

## Agent Builder (no-code) workflow

- Use when you need a quick prototype or a simple production voice agent without custom logic.
- Where: LiveKit Cloud project → Agents dashboard → “Deploy new agent”.

### What you can configure

- Prompt/instructions, optional greeting, and STT → LLM → TTS model pipeline.
- Tools/actions:
  - HTTP tools (REST endpoints, params in query/body, headers)
  - Client tools (client-side RPC calls)
  - MCP servers (tools auto-discovered; supports streaming HTTP/SSE)
- Variables:
  - Job metadata JSON exposed as `{{metadata.key}}`.
  - Secrets exposed as `{{secrets.KEY}}` (use project secrets store; do not inline tokens).

### Test, deploy, export

- Live preview applies changes automatically; preview uses inference credits and is not part of production observability.
- Deploy to LiveKit Cloud from the Builder.
- Export: download a ZIP with generated Python code compatible with LiveKit CLI deployment.

### Known limitations (Builder vs SDK)

- Not supported in Builder: workflows/handoffs/tasks, vision, realtime models/plugins, tests.

## Agents playground (test UI)

- Purpose: a ready-made web UI to test your agent (audio/text/video) before building your own app.
- Requirement: you must already have an agent running in `dev` or `start` mode.
- Options: use the hosted playground (tight LiveKit Cloud integration) or run the open-source playground yourself.
