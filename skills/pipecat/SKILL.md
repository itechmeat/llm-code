---
name: pipecat
description: "Pipecat realtime voice/multimodal bots. Covers pipelines/frames, transports, RTVI, Pipecat Cloud deploy. Use when building real-time voice bots (STT/LLM/TTS pipelines), multimodal AI agents, WebRTC/WebSocket transports, or deploying to Pipecat Cloud. Keywords: pipecat, pipecat-ai, RTVI, WebRTC, voice bot."
metadata:
  version: "1.5.0"
  release_date: "2026-07-04"
---

# Pipecat

Pipecat is an open-source Python framework for building real-time voice and multimodal bots.
It composes streaming speech/LLM/TTS services into a low-latency pipeline, connected via transports (WebRTC/WebSocket) and client SDKs using the RTVI message standard.

## Links

- [Documentation](https://docs.pipecat.ai/getting-started/introduction)
- [Changelog](https://github.com/pipecat-ai/pipecat/blob/main/CHANGELOG.md)
- [GitHub](https://github.com/pipecat-ai/pipecat)

## Quick navigation

- Installation (packages/extras/CLI): `references/installation.md`
- Migration to 1.0: `references/migration-1-0.md`
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
- Do not assume deprecated import shims or service-specific context classes still exist in `1.0.0`; audit imports before upgrading.
- Do not keep VAD/turn-detection logic on transport params; current releases route that control through `LLMUserAggregator` strategies.
- Do not assume `OpenAIResponsesLLMService` is HTTP-based anymore; WebSocket is now the default implementation.

## Release Highlights (0.0.109 -> 1.2.0)

### Runtime and service additions

- **`OpenAIResponsesLLMService`** now defaults to a persistent WebSocket connection; the prior HTTP behavior moved to `OpenAIResponsesHttpLLMService`.
- **Inworld Realtime LLM** adds a WebSocket cascade STT/LLM/TTS path with semantic VAD and function calling.
- **`MistralTTSService`** adds streaming Voxtral TTS, and TTS/STT services gained more runtime-update and sample-rate options.
- The development runner now exports a module-level FastAPI `app` for custom routes before `main()`.

### Tooling and context changes

- Function calling now supports grouped parallel tool batches, async tool completion after interruption, and streaming intermediate tool results.
- Context editing now has `LLMMessagesTransformFrame`, and the framework standardizes on universal `LLMContext` / `LLMContextAggregatorPair`.
- OpenAI tool schemas can now include provider-specific `custom_tools`.
- `1.2.0` adds `add_tool_change_messages` for LLM aggregators, widens `tool_resources` into deprecated `app_resources`, and extends async-tool compatibility across more realtime providers.

### Turn-taking and client protocol

- `1.2.0` adds explicit inference/finalization turn hooks (`on_user_turn_inference_triggered`, `LLMTurnCompletionUserTurnStopStrategy`, `FilterIncompleteUserTurnStrategies`) for smarter end-of-turn gating.
- RTVI grows first-class UI Agent Protocol support with `ui-event`, `ui-snapshot`, `ui-cancel-task`, `ui-command`, and `ui-task`, bumping the protocol to `1.3.0`.
- The development runner and runner arguments now carry a stable `session_id`, which is useful for per-session tracing across local and cloud-like flows.

### Breaking migrations

- Deprecated service-specific context classes, transport params, RTVI shims, frame aliases, and interruption/VAD helpers were removed across the stack.
- Turn detection and mute behavior moved toward `LLMUserAggregator` strategies instead of transport-level configuration.
- Some legacy providers and helpers were removed entirely (`OpenPipeLLMService`, `TTSService.say()`, `FrameProcessor.wait_for_task()`, older beta/alias modules).

## Release Highlights (1.4.0 -> 1.5.0)

- **Pipecat Flows in core (`1.5.0`)**: Pipecat Flows is integrated into the main package, so structured conversation flows no longer require a separate install.
- **Behavioral eval framework (`1.4.0`)**: a testing framework for evaluating bot behavior, plus `on_user_turn_message_added` event handlers and realtime LLM-service metadata frames.
- **New services (`1.5.0`)**: Together AI STT/TTS services and NVIDIA per-sentence synthesis, with TTFA (time-to-first-audio) metrics for latency tracking.

## Release Highlights (1.3.0)

- **Workers and multi-agent pipelines**: `PipelineTask` / `PipelineRunner` are renamed toward `PipelineWorker` / `WorkerRunner`, and `pipecat.workers` makes pipelines peers on a typed-message bus for `@job` dispatch, handoffs, sidecars, UI workers, and distributed Redis/PGMQ patterns.
- **UIWorker and RTVI UI protocol**: `UIWorker` can observe client accessibility snapshots and drive UI commands over RTVI; the UI worker vocabulary moves from `task`/`agent` to `job`/`worker` (`ui-task` -> `ui-job-group`, `cancelUITask` -> `cancelUIJobGroup`).
- **Development runner**: one runner can serve WebRTC, Daily, telephony, and plain WebSocket clients; `/start` accepts a `transport` field, `/ws-client` supports protobuf WebSocket clients, `/status` reports enabled transports, and the Daily redirect moved to `/daily`.
- **Service surface**: adds Vonage Video Connector transport, Inception Mercury 2 LLM service, Cartesia turn-based STT, Rime `coda` TTS defaults, Soniox endpoint-delay settings, `LLMService.append_system_instruction()`, and `STTService.supports_ttfs`.
- **Operational migration notes**: optional service/transport extras now raise `ImportError`, `transformers` is no longer a base dependency, Rime defaults to `coda`, OpenRouter defaults to `openai/gpt-4.1` and maps `developer` messages to `user` unless explicitly supported.

## Links

- Docs: https://docs.pipecat.ai/getting-started/introduction
- Full-text extract used for this skill: https://docs.pipecat.ai/llms-full.txt
- Changelog: https://github.com/pipecat-ai/pipecat/blob/main/CHANGELOG.md
- GitHub: https://github.com/pipecat-ai/pipecat
- PyPI (framework): https://pypi.org/project/pipecat-ai/
- PyPI (cloud SDK): https://pypi.org/project/pipecatcloud/
