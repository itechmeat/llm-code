# Context management

## What “context” means

In Pipecat, context is the conversation history the LLM uses to respond: a sequence of role-tagged messages (system/user/assistant/tool).

## Automatic context updates

The Learn guide describes a default automatic flow:

- User audio → STT → transcription frames → user context aggregator stores a new user message.
- LLM output → TTS → TTS text frames → assistant context aggregator stores what was actually spoken.

Important detail: storing **TTS text** keeps context aligned with what the user heard (especially when output is interrupted).

## Aggregators and placement

- Place the **user** context aggregator downstream from STT (so it can collect transcription frames).
- Place the **assistant** context aggregator after `transport.output()` so it can observe the post-TTS text frames and update word-by-word when supported.

This placement also helps keep context correct when interruptions cut off the bot mid-sentence.

## Function calling and context

- Tool/function definitions live in the context as a schema.
- Tool calls and results are also stored in history so the conversation remains complete.

## Manual control via frames

Learn docs mention control frames that let you:

- append new messages to the existing context
- replace the entire message list

Use cases:

- bot should speak first at session start
- system-mode changes (“you are now…”) applied mid-session
- injecting external events into the conversation

## Context summarization

For long sessions, the guide describes built-in summarization that compresses older history while keeping recent turns. Enable it via assistant aggregator params.

Pipecat 0.0.105 also exposes an `on_summary_applied` event on `LLMAssistantAggregator`, so you can observe summarization without reaching into private members.

## Practical checklist

- Keep assistant aggregation after output to store what was actually spoken.
- Be explicit about whether `system_instruction` lives on the service, in the context, or both; service-level instruction now wins if both are present.
- If you mutate context manually, decide whether it should trigger an immediate LLM run.
- Enable summarization early for long-running agents to control token growth.
