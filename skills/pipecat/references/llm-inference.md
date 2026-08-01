# LLM inference

## What the LLM service does

- Consumes an LLM context frame (conversation history)
- Streams response tokens downstream as LLM text frames
- Optionally triggers function/tool calls when tools are available

## Placement in the pipeline

The Learn guide places LLM after the user context aggregator and before downstream consumers (TTS, output).

## Streaming boundaries and output control

Docs describe lifecycle/boundary frames around a streamed completion:

- “full response start” marker
- streaming token/text frames
- “full response end” marker

There is also a configuration frame that can mark output as **not to be spoken** (skip TTS) while still flowing through the pipeline.

## Function call lifecycle frames

The Learn guide mentions frames signaling:

- function calls started
- function call in progress
- function call result

This is useful for UI/UX (“thinking…”) and tracing.

## Provider switching: OpenAI-compatible base URL

Docs describe an OpenAI-compatible base service pattern where you can point at an OpenAI-spec endpoint via a `base_url` without rewriting pipeline code.

`1.0.0` changes the default OpenAI Responses integration: `OpenAIResponsesLLMService` now uses a persistent WebSocket connection and incremental context via `previous_response_id`. If you explicitly want the prior request/response model, use `OpenAIResponsesHttpLLMService`.

## Service switching and fallback (0.0.105)

Pipecat adds `ServiceSwitcherStrategyFailover`, which automatically moves to the next service after a non-fatal provider error. Use the `on_service_switched` event to log or react to the failover.

## Parallelism for tool calls

An LLM service option controls whether multiple tool calls run in parallel or sequentially. Use sequential execution for dependent tool chains.

OpenAI-oriented tool schemas can also include `custom_tools` when you need provider-specific capabilities alongside standard function tools.

## Event handlers

Docs mention events such as:

- completion timeout
- function calls started

Use these to implement user feedback and recovery (retry/backoff/fallback) as needed.

## System instruction behavior (0.0.105)

- `system_instruction` is now wired consistently across the OpenAI, Anthropic, and AWS Bedrock LLM services as a default system prompt.
- `run_inference` now accepts a one-shot `system_instruction` override.
- If you set both constructor-level `system_instruction` and a system message in context, the constructor value takes precedence and Pipecat logs a warning.

## Reasoning support (1.6.0)

`OpenAIResponsesLLMService` and `OpenAIResponsesHttpLLMService` gain `reasoning` configuration:

- Set `settings.reasoning` to a `ReasoningConfig(effort=..., summary=...)` to control reasoning depth and optionally request a summary of the model's thinking.
- Summaries surface the same way as Anthropic/Gemini thinking: as thought frames and the `on_assistant_thought` event.
- Only reasoning-capable models support it (the gpt-5.x series and the o-series); the default model, `gpt-4.1`, does not reason. If you set `reasoning` on a model that does not support it, the service logs a clear error up front instead of surfacing a raw API failure.
- The model's encrypted reasoning is captured and sent back automatically on subsequent turns, preserving reasoning context across the conversation and across tool-call turns.
- When `reasoning` is not configured, mainline gpt models from gpt-5 onward default to `effort="none"` (disabled) to keep real-time voice latency low, mirroring how Gemini disables thinking by default; other models keep their provider default.
- See `examples/thinking/thinking-openai-responses.py` (plus the `-http` and `-functions-` variants).

## New LLM services (1.6.0)

- **`CrusoeLLMService`**: OpenAI-compatible LLM service for Crusoe Cloud's Managed Inference API.
- **`BasetenLLMService`**: OpenAI-compatible LLM service for Baseten's Model APIs and dedicated deployments. Defaults to Baseten's serverless Model APIs endpoint (open-weights models such as GLM, Kimi, DeepSeek, Nemotron, gpt-oss); for a dedicated deployment, pass its `/sync/v1` URL as `base_url` and set `settings.model` to the served model name.

## Audio token usage in `LLMTokenUsage` (1.6.0)

- `LLMTokenUsage` gains optional `input_audio_tokens`, `output_audio_tokens`, and `cache_read_input_audio_tokens` fields for cost attribution with realtime models.
- `OpenAIRealtimeLLMService` (including Azure realtime) populates them from the Realtime API's `response.done` usage details.
- `GeminiLiveLLMService` populates them from the AUDIO entries in `usage_metadata`'s per-modality breakdowns; absent modalities report as unset rather than zero, and text tokens are never derived from totals.
- Values flow through usage debug logs, RTVI client metrics (only present when populated), and OTel span attributes (`gen_ai.usage.audio.input_tokens`, `gen_ai.usage.audio.output_tokens`, `gen_ai.usage.audio.cache_read.input_tokens`). See `references/server-pipeline-apis.md` for the wider OTel attribute changes in `1.6.0`.

## LLM service updates (1.3.0)

- `LLMService.append_system_instruction(...)` appends durable system text that is included on every inference and survives context resets. Prefer it when a worker needs persistent task guidance without rewriting the whole context.
- `InceptionLLMService` supports Inception Mercury 2 diffusion reasoning with `reasoning_effort` and `realtime` settings.
- `OpenRouterLLMService` now defaults to `openai/gpt-4.1` and converts `developer` messages to `user` by default for broader model compatibility. Set `llm.supports_developer_role = True` or subclass when the target model actually supports the developer role.
- `InworldRealtimeLLMService` defaults STT to `inworld/inworld-stt-1`; verify any explicit STT override before removing old defaults.

## Practical checklist

- Keep completion streaming enabled if you want low perceived latency.
- If you skip TTS for specific outputs, ensure your client still receives a useful text channel.
- Decide whether tool calls must be parallel or sequential based on dependencies.
- If you migrate from older OpenAI Responses code, verify connection lifecycle, proxy compatibility, and reconnect behavior under WebSocket transport.
