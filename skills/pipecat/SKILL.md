---
name: pipecat
description: "Pipecat realtime voice/multimodal bots. Covers pipelines/frames, transports, RTVI, Pipecat Cloud deploy. Use when building real-time voice bots (STT/LLM/TTS pipelines), multimodal AI agents, WebRTC/WebSocket transports, or deploying to Pipecat Cloud. Keywords: pipecat, pipecat-ai, RTVI, WebRTC, voice bot."
metadata:
  version: "1.13.0"
  release_date: "2026-10-18"
---

# Pipecat

Pipecat is an open-source Python framework for building real-time voice and multimodal bots.
It composes streaming speech/LLM/TTS services into a low-latency pipeline, connected via transports (WebRTC/WebSocket) and client SDKs using the RTVI message standard.

## Links

- [Documentation](https://docs.pipecat.ai/getting-started/introduction)
- [Changelog](https://github.com/pipecat-ai/pipecat/blob/main/CHANGELOG.md)
- [GitHub](https://github.com/pipecat-ai/pipecat)
- [PyPI (framework)](https://pypi.org/project/pipecat-ai/)
- [PyPI (cloud SDK)](https://pypi.org/project/pipecatcloud/)
- [Full-text extract used for this skill](https://docs.pipecat.ai/llms-full.txt)

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
- Files & images in the LLM context (send-file, FileResolver, uploads): `references/files-and-images.md`
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
- Do not send a single `button` field in the RTVI `dtmf` client message; as of `1.6.0` it requires `buttons` (a list), and `RTVI.PROTOCOL_VERSION` is `2.1.0`.
- Do not filter OTel dashboards on old GenAI span attribute names (`az.ai.openai`, `xai`, `mistral`, `gen_ai.usage.reasoning_tokens`, bare `tokens.*`); `1.6.0` renamed these to standard `gen_ai.*` conventions.
- Do not use `UninterruptibleFrame`, `BaseUIWorker`, `ReplyToolMixin`, `EvalJudge(llm)`, `VoicemailDetector(llm=...)`, the `BACKEND_PAIRING_INSTRUCTION` / `FRONTEND_PAIRING_INSTRUCTION` constants, or the startup warmup timing hooks; they are deprecated in `1.13.0` and removed in `2.0.0`.
- Do not rely on the `mcp` extra with the 1.x SDK; `1.13.0` requires `mcp[cli]>=2.1.1,<3`.
- Do not let the LLM fetch arbitrary URLs: `FileResolver` only downloads publicly routable addresses or CIDR ranges listed in `allowed_url_networks` / `PIPECAT_ALLOWED_FILE_URL_NETWORKS`, and it refuses redirects.

## Release Highlights (1.12.0 -> 1.13.0)

### Files and images in the conversation (1.13.0)

- **RTVI `send-file`**: clients can now send files and images to the bot, and they enter the LLM context. New frames `FileRawFrame`, `InputFileRawFrame` and `UserFileRawFrame` carry the payload as inline base64 or as a URL.
- **Context methods**: `LLMContext.create_file_message()`, `create_file_url_message()` and `add_file_frame_message()` produce universal `file_base64` (base64 data URL) and `file_url` content items that each adapter translates (Anthropic, AWS Bedrock, Gemini, OpenAI Chat, OpenAI Responses). Unsupported MIME types fail during conversion instead of being dropped silently.
- **Resolution at request time**: each adapter declares which URLs its provider can fetch itself (public `http(s)` per MIME type, `s3://` via Bedrock IAM, `gs://` via Vertex Gemini IAM, Gemini Files API URIs) and those pass through. Everything else is downloaded by the new `FileResolver` (`pipecat.utils.file_resolver`) and inlined at conversion time, so the context keeps only the URL while the bytes live in an in-memory cache keyed by URL. Each file is fetched once, not per turn; services sharing one resolver reuse each other's downloads. A URL is assumed to identify immutable content - `FileResolver.forget(url)` forces a re-fetch.
- **SSRF guard**: the resolver downloads `http(s)` URLs only when the resolved address is publicly routable or falls inside its `allowed_url_networks` CIDR ranges (default from `PIPECAT_ALLOWED_FILE_URL_NETWORKS`); redirects are refused and the download is capped at 50 MB. Other schemes go to its `FileStorage`.
- **Storage**: `FileStorage` (`pipecat.utils.file_storage`) with a `LocalFileStorage` default. `save()` returns a URL the backend can resolve later (`pipecat:<id>` for local storage); a custom backend can mint `gs://` or `s3://` URLs the provider may fetch itself. A backend whose URLs it owns can set `delete_after_load` (as `LocalFileStorage` does) so the file is deleted once its bytes are cached.
- **Runner uploads**: the development runner gains `POST /sessions/{session_id}/files` (50 MB cap), enabled with `-u/--uploads-folder` or `PIPECAT_UPLOADS_FOLDER`, answering with an RTVI file source. A flat `POST /files` exists for transports whose clients never learn a session id. `/start` responses advertise the route as `fileUploadUrl`; `--uploads-folder-max-files` (default 10) trims the oldest uploads.
- **Custom storage**: define a `create_file_storage()` function next to `bot()`; whichever host runs the bot discovers it, so bot code stays identical across hosts. The active backend is injected as `runner_args.file_storage`.
- **Rejected requests**: `LLMContext.remove_invalid_file_message()` drops the oldest file or image message added since the last successful reply when OpenAI, Anthropic, Bedrock or Gemini rejects the request.

See `references/files-and-images.md` for the full flow.

### Backend LLM (1.13.0)

- **`LLMWithBackend`** (`pipecat.pipeline.llm_with_backend`, alpha): a conversational frontend LLM (text or speech-to-speech) with a backend LLM (in a `BackendLLMWorker`) it delegates to for deeper thinking and tool orchestration. The frontend keeps the conversation moving while the backend does the heavy lifting and sends messages to the frontend as it works. It drops into a pipeline where a standalone LLM would go.
- **Pairing configuration**: `pairing_instruction` on `BackendLLMWorker` and `frontend_pairing_instruction` on `BackendConnector` replace the `BACKEND_PAIRING_INSTRUCTION` / `FRONTEND_PAIRING_INSTRUCTION` constants; the request strategies take their own texts as arguments (`frontend_instruction`, `tool_description`, `request_instruction`).
- **External function calls**: new frames report calls that ran outside the pipeline - `ExternalFunctionCallsStartedFrame`, `ExternalFunctionCallInProgressFrame`, `ExternalFunctionCallResultFrame`, `ExternalFunctionCallCancelFrame`. `RTVIObserver` turns them into the usual `llm-function-call-*` messages under the per-function report level. `LLMService.cancel_function_calls()` cancels every in-flight call, async ones included. `LLMAssistantAggregator.has_synchronous_function_calls_in_progress` tells whether a synchronous call is running.
- **Speech-to-speech**: the services now take messages appended to the conversation (`LLMMessagesAppendFrame`) into their session, each on whatever channel its provider offers - OpenAI Realtime, Azure Realtime and Grok as conversation items, Gemini Live as client content that does not complete the turn, Nova Sonic as a text event.

### Provider settings (1.12.0 - 1.13.0)

- `FishAudioTTSService.Settings` gained `chunk_length`, `min_chunk_length`, `condition_on_previous_chunks`, `prosody_normalize_loudness`.
- `OpenRouterLLMService.Settings` gained `provider` for provider routing preferences (`provider={"sort": "latency"}`).
- `GrokLLMService.Settings` gained `reasoning_effort` (`low`, `medium`, `high`; `xhigh` on `grok-4.6`+; `none` where supported).

### Deprecations and removals (removed in 2.0.0)

- **`UninterruptibleFrame`** is gone: a frame class that should not be interrupted declares `interruptible: bool = field(default=False, init=False)` instead.
- **`EvalJudge`** no longer takes an LLM service directly: pass `EvalJudge(LLMClassifier(llm=service), explainer=service)`. The judge now decides every verdict with a classifier, and the explainer LLM supplies the reason behind every `no` and every verdict below `explain_below` (`explainer: false` turns reasons off).
- **`VoicemailDetector`** is now a single processor that takes a `classifier`, instead of a parallel pipeline with its own LLM; its `llm` and `custom_system_prompt` parameters are deprecated (the `llm` is wrapped in an `LLMClassifier` meanwhile). It asks the classifier after each transcription and acts once the caller has been quiet for `decision_timeout` (default 1 s).
- **`BaseUIWorker`** is deprecated in favor of `UIWorker`, which now reports its job groups to the client on its own. **`ReplyToolMixin`** is deprecated in favor of `screen_tools`, and `UIWorker.respond_to_job` no longer takes `tts_speak`.
- **Startup warmup timings** are gone: `StartupTimingReport.warmup`, `StartupWarmupTiming`, `StartupWarmup` and the `on_startup_warmup()` hook were removed - pipecat warms no deferred imports while the pipeline sets up.
- **`max_frames`** on `TurnTrackingObserver` and `UserBotLatencyObserver` is deprecated; observers no longer keep a window of the frames they have seen.
- **Removed**: `NotifierGate`, `ClassifierGate`, `ConversationGate` and `ClassificationProcessor` from `pipecat.extensions.voicemail.voicemail_detector`, plus the `CLASSIFIER_RESPONSE_INSTRUCTION` and `DEFAULT_SYSTEM_PROMPT` attributes of `VoicemailDetector`.
- **Breaking dependency**: the `mcp` extra now requires the 2.x SDK (`mcp[cli]>=2.1.1,<3`); `MCPClient` no longer runs on the 1.x SDK.

### Fixes (1.12.0 - 1.13.0)

- An `LLMService` regression where re-advertising a tool with the same name but a different handler silently kept the previous handler - auto-registered handlers are rebound, explicit `register_function` registrations are untouched.
- `InworldRealtimeLLMService` resent a server-VAD user transcript after a fast tool result context update, duplicating user turns and responses; Inworld extensions are serialized under `providerData` instead of `provider_data`.
- NVIDIA STT settings changes now apply to the running stream (the service used to rebuild its config without reconnecting).
- Flows node transitions: an interruption could leave the LLM running with the previous node's context and tools - the queued `LLMMessagesAppendFrame`/`LLMMessagesUpdateFrame` and `LLMSetToolsFrame` are now uninterruptible.
- `TelnyxFrameSerializer` now sends `OutputTransportMessageFrame` and `OutputTransportMessageUrgentFrame` to the client as JSON instead of dropping them.
- The eval harness no longer treats the bot's earlier speech as its reply when a scenario interrupts the bot; `pipecat eval suite` keeps `concurrency` runs going at all times, taking the next run in manifest order.
- `MoondreamService` with transformers 5: loading the model on a GPU or Apple Silicon failed, and a loaded model produced garbage descriptions.
- A bridged `PipelineWorker` reported every frame from its LLM twice over RTVI - `enable_rtvi` now defaults to off for a bridged pipeline worker.
- TTS word tracking no longer falls out of step on markdown-heavy replies (Cartesia's trailing period, provider-specific symbols).
- `WorkerRunner` no longer skips a worker added while the runner was still starting; `pcm_to_wav()` no longer drops samples with a typed `memoryview`; `is_silence()` no longer misclassifies full-scale negative int16 samples as silence.
- `MOQTransport` no longer ends the call when a relay refuses a subscription with `dropped` - it retries and redials as for any relay loss.
- `RTVIObserver` remembers only the frames it handles, and observers no longer keep the IDs of every frame for the life of the session; `on_user_turn_idle` fires again after a turn that ended with no transcript.

## Release Highlights (1.9.0 -> 1.11.0)

- **Latency attribution (`1.9.0`)**: `LatencyBreakdown.contributions` is a timeline of the user-to-bot interval whose durations sum to the measured latency — it names the time no service reports (VAD silence, turn detection, turn-completion markers and holds, sentence aggregation, function handlers).
- **Smallest AI continuation (`1.10.0`)**: `SmallestTTSService` shares a `context_id` across text fragments of the same LLM turn so the server joins them into one continuous generation instead of resetting prosody per request; optional `max_buffer_delay_ms` bounds the fragment buffer.
- **Resampler stream boundaries (`1.11.0`)**: `BaseAudioResampler.flush()` returns audio the resampler still holds when a stream has ended and `reset()` starts a fresh stream — callers mark boundaries explicitly instead of relying on `SOXRStreamAudioResampler`'s inactivity timeout.

## Release Highlights (1.7.0 -> 1.8.1)

### Turn detection and tools (1.8.0)

- **Turn detection redesign**: every in-repo service with built-in turn detection now emits `ProposedUserStartedSpeakingFrame` / `ProposedUserStoppedSpeakingFrame`, and `ExternalUserTurnStrategies` resolves them into real turn frames — one subclassable place that decides turns. Third-party services emitting turn frames directly keep working unchanged.
- **MCP made trivial**: `MCPClient.tools()` now auto-connects, registers tools, and closes the connection at pipeline end (just `LLMContext(tools=await mcp.tools())`); `MCPClient(tools_arguments=...)` injects fixed arguments into every call of a tool, hidden from the model's schema. New `KeenableWebSearch` service (`keenable` extra) adds live web search + page reading via a hosted MCP server.
- **MoQ client mode**: dial a shared relay instead of serving your own socket — works behind NAT (`--moq-connect <relay>`, plus `MOQParams.response_path`/`request_path`).

### Workers and error handling (1.8.0)

- **Workers**: `JobParams`/`JobGroupParams` bundle job dispatch metadata, `BaseUIWorker` surfaces jobs on a client UI without an LLM, `WorkerRunner.get_worker(name)` finds peers by name, and `request_cancel_job_group()` allows external cancellation.
- **Error/usable-state model**: `ErrorCategory` (AUTHENTICATION/SERVER/APPLICATION/UNKNOWN), `FrameProcessor.is_usable`, and `on_usable_changed` let handlers tell a briefly-struggling processor from one to retire; `PipelineWorker(processor_unusable_policy=CONTINUE|END|CANCEL)` decides what happens when a processor goes unusable. `AudioVolumeTracker` measures rolling 400ms volume.

### v1.7.0 additions

- **STT usage metrics**: `STTUsageMetricsData` carries `audio_seconds`; enable with `enable_usage_metrics=True` (forwarded to RTVI clients as `stt_usage`, logged by `MetricsLogObserver`, attached to OTel `stt` spans). AWS Nova Sonic LLM adds `LLMUsageMetricsData` token deltas.
- **New/updated TTS/STT settings**: `PocketTTSService` (local CPU-only TTS, 6 languages + voice cloning); `XTTSService` deprecated (removal `2.0.0`, use Kokoro/Piper); `reach_inactive_services` on settings frames; plus per-service settings such as Google LLM `safety_settings`, Azure `force_locale`, Cartesia `keyterm`, Deepgram `numerals`, ElevenLabs `filter_background_audio`, and Smol `endpointing`/`keywords`/`format`.
- **Breaking-behavior changes**: `TavusParams.audio_out_faster_than_realtime` now defaults to `True`; `GeminiLiveLLMService` uses `GeminiLiveLLMAdapter` (hand-crafted `LLMSpecificMessage`s need `llm="gemini-live"`); LiveKit transport adds inbound SIP DTMF (`on_dtmf_event`); `LLMSettings.filter_incomplete_user_turns` deprecated.

### Context Hub (1.8.0)

`pipecat context-hub` (alias `pipecat ch`) lets coding agents query a local index of Pipecat APIs instead of hallucinating them; it ships in the `cli` extra, and `pipecat init` offers to register it with the coding agents it finds and to build the index. `v1.8.1` fixes `pipecat eval run` to read `.yml` scenario files and settles Context Hub staleness-warning behavior.

## Release Highlights (1.6.0)

### New transport and reasoning

- **`MOQTransport`**: a Media over QUIC transport giving bots a bidirectional, low-latency audio + RTVI channel over QUIC instead of WebRTC/WebSocket (`pip install "pipecat-ai[moq]"`). The bot can run as its own MoQ server for local dev; the development runner gained `--moq-serve`, `--moq-bind`, and TLS flags.
- **`reasoning` in OpenAI Responses services**: `OpenAIResponsesLLMService` / `OpenAIResponsesHttpLLMService` accept a `ReasoningConfig(effort=..., summary=...)`; encrypted reasoning round-trips across turns and tool calls automatically, and summaries surface as thought frames / `on_assistant_thought`.

### Flows, evals, and new services

- **Pipecat Flows `NO_RESPONSE`**: a function can return `(result, NO_RESPONSE)` to finish the call without an LLM run or node transition, letting the next user utterance drive the next response.
- **Eval scenarios `absent: true`**: an expectation that passes only if no matching event arrives within `within_ms`, useful for catching duplicate-output regressions.
- **New services**: `CrusoeLLMService` and `BasetenLLMService` (OpenAI-compatible LLM services for Crusoe Cloud and Baseten), `DeepgramFluxTTSService` (websocket TTS for Deepgram Flux, token-streamed by default).
- **Audio token usage**: `LLMTokenUsage` gains `input_audio_tokens` / `output_audio_tokens` / `cache_read_input_audio_tokens`, populated by `OpenAIRealtimeLLMService` (and Azure realtime) and `GeminiLiveLLMService`.

### Breaking changes and deprecations

- RTVI `dtmf` client message uses `buttons` (a list) instead of `button`; `RTVI.PROTOCOL_VERSION` is now `2.1.0`.
- OTel GenAI span attributes were renamed to standard conventions: `gen_ai.provider.name` values for Azure/xAI/Mistral, and `gen_ai.usage.reasoning_tokens` -> `gen_ai.usage.reasoning.output_tokens`; OpenAI Realtime and Gemini Live token attributes are now standardized `gen_ai.usage.*` names instead of ad hoc `tokens.*`.
- ElevenLabs services default to TTS model `eleven_flash_v2_5` instead of the now-deprecated `eleven_turbo_v2_5`.
- `PronunciationDictionaryLocator` is deprecated in favor of `text_transforms` / `replace_text` (removal in `2.0.0`).
- Turn-strategy `reset()` is deprecated in favor of `handle_user_turn_started()` / `handle_user_turn_stopped()` lifecycle callbacks (removal in `2.0.0`).

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

## Release Highlights (1.3.0 -> 1.5.0)

- **Workers and multi-agent pipelines (`1.3.0`)**: `PipelineTask` / `PipelineRunner` are renamed toward `PipelineWorker` / `WorkerRunner`, and `pipecat.workers` makes pipelines peers on a typed-message bus for `@job` dispatch, handoffs, sidecars, UI workers, and distributed Redis/PGMQ patterns.
- **UIWorker and RTVI UI protocol (`1.3.0`)**: `UIWorker` can observe client accessibility snapshots and drive UI commands over RTVI; the UI worker vocabulary moves from `task`/`agent` to `job`/`worker` (`ui-task` -> `ui-job-group`, `cancelUITask` -> `cancelUIJobGroup`).
- **Development runner (`1.3.0`)**: one runner can serve WebRTC, Daily, telephony, and plain WebSocket clients; `/start` accepts a `transport` field, `/ws-client` supports protobuf WebSocket clients, `/status` reports enabled transports, and the Daily redirect moved to `/daily`.
- **Service surface (`1.3.0`)**: adds Vonage Video Connector transport, Inception Mercury 2 LLM service, Cartesia turn-based STT, Rime `coda` TTS defaults, Soniox endpoint-delay settings, `LLMService.append_system_instruction()`, and `STTService.supports_ttfs`. Optional service/transport extras now raise `ImportError` when their dependency is missing, and `transformers` is no longer a base dependency.
- **Behavioral eval framework (`1.4.0`)**: a testing framework for evaluating bot behavior, plus `on_user_turn_message_added` event handlers and realtime LLM-service metadata frames.
- **Pipecat Flows in core (`1.5.0`)**: Pipecat Flows is integrated into the main package, so structured conversation flows no longer require a separate install. **New services (`1.5.0`)**: Together AI STT/TTS services and NVIDIA per-sentence synthesis, with TTFA (time-to-first-audio) metrics for latency tracking.
