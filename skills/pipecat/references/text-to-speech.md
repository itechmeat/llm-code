# Text to speech (TTS)

## Placement

Learn guide places TTS:

- after the LLM (so it can consume streamed LLM text frames)
- before `transport.output()` (to produce audio frames)
- before the assistant context aggregator (so spoken text can be captured accurately)

## Two common input modes

- **Streamed LLM output**: TTS aggregates streaming LLM tokens into speakable chunks (often sentence-like), sends to the provider, and streams audio back.
- **Direct speak**: a dedicated “speak this text now” frame bypasses the LLM/context (useful for system prompts and immediate cues).

## Typical outputs

Docs describe TTS emitting:

- raw audio frames for playback
- TTS text frames representing what was actually spoken
- boundary frames that mark speech start/stop

## Word timestamps

Some providers expose word timestamps. The guide emphasizes these for:

- accurate context updates when output is interrupted
- tighter sync for captions/subtitles and other post-output processing

## Pipeline-level audio configuration

Prefer setting output sample rate and related audio settings at the pipeline/task level so all processors stay consistent.

## Text shaping: what gets spoken

The guide outlines multiple ways to control spoken content:

- customize aggregation before TTS (e.g., group URLs/code separately)
- skip selected aggregated types (do not speak them)
- apply just-in-time text transforms for pronunciation/clarity (numbers, acronyms, URLs)

Note: transforms may affect what ends up in assistant context when context is based on spoken output.

## Skipping TTS (voice ↔ text toggles)

Docs describe a `skip_tts` flag that can be applied:

- globally for a stretch of conversation (via an LLM configuration frame)
- per-frame for selective silencing

Useful for:

- structured metadata that should be processed but not spoken
- text-only replies
- audio-less testing pipelines

## Dynamic updates

The guide shows a settings-update frame to change TTS parameters mid-conversation.

## Practical checklist

- Use WebSocket TTS providers when latency is critical.
- Capture spoken text (not just LLM text) in context for correctness under interruptions.
- Decide upfront how you will handle URLs/code/structured output so the bot doesn’t read garbage aloud.
