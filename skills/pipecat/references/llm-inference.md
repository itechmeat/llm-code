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

## Parallelism for tool calls

An LLM service option controls whether multiple tool calls run in parallel or sequentially. Use sequential execution for dependent tool chains.

## Event handlers

Docs mention events such as:

- completion timeout
- function calls started

Use these to implement user feedback and recovery (retry/backoff/fallback) as needed.

## Practical checklist

- Keep completion streaming enabled if you want low perceived latency.
- If you skip TTS for specific outputs, ensure your client still receives a useful text channel.
- Decide whether tool calls must be parallel or sequential based on dependencies.
