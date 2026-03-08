---
name: pipecat
description: "Pipecat realtime voice/multimodal bots. Covers pipelines/frames, transports, RTVI, Pipecat Cloud deploy. Use when building real-time voice bots (STT/LLM/TTS pipelines), multimodal AI agents, WebRTC/WebSocket transports, or deploying to Pipecat Cloud. Keywords: pipecat, pipecat-ai, RTVI, WebRTC, voice bot."
metadata:
  version: "0.0.104"
  release_date: "2026-03-03"
---

# Pipecat

Pipecat is an open-source Python framework for building real-time voice and multimodal bots.
It composes streaming speech/LLM/TTS services into a low-latency pipeline, connected via transports (WebRTC/WebSocket) and client SDKs using the RTVI message standard.

## Quick navigation

- Installation (packages/extras/CLI): `references/installation.md`
- Concepts & architecture: `references/core-concepts.md`
- Session initialization (runner/bot/client): `references/session-initialization.md`
- Pipeline & frames: `references/pipeline-and-frames.md`
- Transports: `references/transports.md`
- Speech input & turn detection: `references/speech-input-and-turn-detection.md`
- Client SDKs + RTVI messaging: `references/client-sdks-rtvi.md`
- CLI (init/tail/cloud): `references/cli.md`
- Function calling (server): `references/function-calling.md`
- Context management: `references/context-management.md`
- LLM inference: `references/llm-inference.md`
- Text to speech (TTS): `references/text-to-speech.md`
- Deployment (pattern/platforms): `references/deployment.md`
- Server APIs (supported services): `references/server-services.md`
- Server Utilities (runner): `references/server-runner.md`
- Server APIs (pipeline/task/params): `references/server-pipeline-apis.md`
- Pipecat Cloud ops: `references/pipecat-cloud.md`
- Troubleshooting: `references/troubleshooting.md`

## Mental model (cheat sheet)

- **Pipeline**: ordered **processors** that consume/emit **frames**.
- **Frames**: the streaming units (audio/text/video/context/events) flowing through the pipeline.
- **Transport**: connectivity + media IO + session state (WebRTC/WebSocket/provider realtime).
- **Runner**: HTTP service that starts sessions and spawns a bot process with transport credentials.
- **Client SDK**: starts the bot, connects transport, sends messages/requests, receives events.

## Recipes

### 1) Keep secrets server-side

- Put provider API keys (LLM/STT/TTS) only on the server/bot container.
- The client should call a server start endpoint (`startBot` / `startBotAndConnect`) to receive **transport credentials** (e.g., a room URL + token), not provider keys.

### 2) Use WebRTC for production voice

- Prefer a WebRTC transport (e.g., Daily) for resilience and media quality.
- Use a WebSocket transport mostly for server↔server, prototypes, or constrained environments.

### 2b) Design for streaming + overlap

- Keep the pipeline fully streaming (avoid batching whole turns when you can).
- If your services support it, start TTS from partial LLM output to reduce perceived latency.

### 3) Initialize and evolve context via RTVI

- Initialize the bot’s pipeline context from the server start request payload.
- For ongoing interaction, prefer a dedicated “send text” style API (when available) instead of deprecated context append methods.

### 4) Function calling: end-to-end flow

- LLM requests a function call.
- Client registers a handler by function name.
- Client returns a function-call result message back to the bot.

### 5) Pipecat Cloud deployment basics

- Build/push an image that matches the expected platform (Pipecat Cloud requires `linux/arm64` in the docs).
- Use a deployment config file for repeatability.
- Configure pool sizing with `min_agents` (warm capacity) and `max_agents` (hard limit).

## Critical gotchas / prohibitions

- Do not embed sensitive API keys in client apps.
- Expect and handle “at capacity” responses (HTTP 429) when the pool is exhausted.
- Plan for cold-start latency if `min_agents = 0`.
- Ensure secrets and image-pull credentials are created in the same region as the deployed agent.

## Links

- Docs: https://docs.pipecat.ai/getting-started/introduction
- Full-text extract used for this skill: https://docs.pipecat.ai/llms-full.txt
- Changelog: https://github.com/pipecat-ai/pipecat/blob/main/CHANGELOG.md
- GitHub: https://github.com/pipecat-ai/pipecat
- PyPI (framework): https://pypi.org/project/pipecat-ai/
- PyPI (cloud SDK): https://pypi.org/project/pipecatcloud/
