---
name: livekit-agents
description: "LiveKit Agents realtime AI agents. Covers voice/vision pipelines, Agent Server jobs, models & tools. Use when building or operating LiveKit voice/video AI agents, configuring Agent Server pipelines, or integrating speech/vision models. Keywords: LiveKit, agents, voice AI, Agent Server."
metadata:
  version: "1.4.4"
  release_date: "2026-03-03"
---

# LiveKit Agents

Operator-focused playbook for building and running LiveKit Agents (voice/video AI agents) with the LiveKit Agent Server.

## Quick Navigation

- Installation & setup: [references/installation.md](./references/installation.md)
- Getting started: [references/get-started.md](./references/get-started.md)
- Components (Agents UI): [references/components.md](./references/components.md)
- Prompting & evaluation: [references/prompting-and-testing.md](./references/prompting-and-testing.md)
- Multimodality: [references/multimodality.md](./references/multimodality.md)
- Logic (sessions/tasks/workflows/tools): [references/logic-and-structure.md](./references/logic-and-structure.md)
- Prebuilt tasks & tools: [references/prebuilt.md](./references/prebuilt.md)
- Agent Server (jobs, lifecycle, options): [references/agent-server.md](./references/agent-server.md)
- Models (realtime/inference/integrations): [references/models.md](./references/models.md)
- CLI + events/errors: [references/reference.md](./references/reference.md)

## When to Use

Use this skill when you need to:

- Build a voice agent or multimodal agent on LiveKit
- Structure agent logic (sessions, tasks, workflows) and tool calling
- Run agents in production via the Agent Server (job lifecycle, dispatch)
- Choose/operate models (realtime, inference) and connect STT/TTS/LLMs
- Design prompts and run tests/evaluations

## Core Recipes

### Recipe: Voice agent quickstart (minimal)

- Goal: get an agent into a LiveKit room, capture audio, and respond.
- Use: [references/get-started.md](./references/get-started.md)

### Recipe: Production Agent Server (jobs + lifecycle)

- Goal: run agents reliably, handle startup mode, dispatch, and job lifecycle.
- Use: [references/agent-server.md](./references/agent-server.md)

### Recipe: Tool calling (safe + debuggable)

- Goal: define tools, validate inputs/outputs, and avoid prompt/tool drift.
- Use: [references/logic-and-structure.md](./references/logic-and-structure.md)

## Critical Prohibitions

- Do not mirror vendor docs verbatim; keep references actionable.
- Do not hardcode secrets (API keys, LiveKit keys) into prompts or code snippets.
- Do not rely on silent fallbacks for model/provider selection; fail fast.

## Links

- Documentation: https://docs.livekit.io/agents/
- Python SDK (reference): https://docs.livekit.io/reference/python/livekit/agents/index.html
- GitHub (agents): https://github.com/livekit/agents
