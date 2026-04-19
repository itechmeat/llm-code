# Speech input & turn detection

This page explains how Pipecat decides when the user starts/stops a “turn”, and how interruptions work.

## Turn strategies: start vs end

Pipecat separates:

- **Turn start detection**: decide when the user started speaking
- **Turn end detection**: decide when the user finished the thought and expects a response

Signals can combine:

- VAD (voice activity)
- Transcription events (as fallback)
- Minimum words / gating (to avoid triggering on noise)

## VAD (Voice Activity Detection)

Docs highlight a local Silero VAD analyzer (CPU-friendly). Configuration is typically provided via user aggregator params.

`1.0.0` completes the move away from transport-owned VAD/turn analysis: `vad_analyzer`, `turn_analyzer`, and older transport-side mute/interruption helpers were removed.

Key tuning knobs (names from docs):

- `start_secs`: how long speech must continue to confirm a start
- `stop_secs`: how much silence is needed to confirm a stop
- `confidence` and `min_volume`: sensitivity thresholds

Rule of thumb from docs: defaults are usually good; tune only for specific audio conditions and validate with real recordings.

## Turn boundary frames

Docs describe multiple layers of “speech vs turn”:

- Raw VAD speech/silence events (VAD-level start/stop)
- Higher-level turn start/stop decisions:
  - `UserStartedSpeakingFrame`
  - `UserStoppedSpeakingFrame`

## Turn end strategies

Docs mention:

- **Smart Turn (default)**: a turn analyzer model that decides when the user is done (better conversational feel).
- **Speech timeout**: simpler strategy that triggers end after a silence timeout.

## Runtime STT updates (0.0.105)

- Runtime `STTUpdateSettingsFrame` updates now reconnect correctly for a wider set of STT/TTS services instead of only mutating local state.
- Deepgram Flux settings can be updated mid-stream without a reconnect.
- `BaseWhisperSTTService` and `OpenAISTTService` can optionally push empty transcripts downstream when VAD fires but no speech was actually transcribed.
- `AssemblyAIConnectionParams` adds `vad_threshold` for U3 Pro, which helps align provider-side detection with external VAD.

These changes matter when you tune speech sensitivity live or need the agent to resume speaking cleanly after a false-positive VAD event.

## Interruptions

When interruptions are enabled (docs say default enabled), starting a user turn can:

- stop the bot from speaking
- clear pending audio/text output
- allow natural “barge-in” behavior

You can disable interruptions on the start strategy for experiences where barge-in is undesirable.

In `1.0.0`, interruptions are effectively always allowed at the pipeline level. Control now lives in `LLMUserAggregator` strategy selection (`user_turn_strategies`, `user_mute_strategies`) instead of the older `allow_interruptions`, `interruption_strategies`, `STTMuteFilter`, or transport params.

## Practical checklist

- Keep interruptions enabled unless you have a strong UX reason to disable them.
- Prefer Smart Turn when you want fewer awkward cutoffs / long waits.
- If your environment is noisy, adjust `start_secs` and `min_volume` conservatively and re-test.
- If you are upgrading, migrate configuration before tuning thresholds; otherwise you may be changing knobs that no longer exist.
