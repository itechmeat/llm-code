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
