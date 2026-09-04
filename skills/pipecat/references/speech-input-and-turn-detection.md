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

`1.2.0` adds a cleaner separation between “start inference now” and “finalize the turn now”:

- `on_user_turn_inference_triggered` fires as soon as a strategy decides the LLM can start thinking.
- `LLMTurnCompletionUserTurnStopStrategy` waits for `UserTurnInferenceCompletedFrame` before emitting the final stop event, with a timeout safety net.
- `FilterIncompleteUserTurnStrategies()` is the new high-level preset when you want tentative stop detection filtered through an LLM completion check.

## Runtime STT updates (0.0.105)

- Runtime `STTUpdateSettingsFrame` updates now reconnect correctly for a wider set of STT/TTS services instead of only mutating local state.
- Deepgram Flux settings can be updated mid-stream without a reconnect.
- `BaseWhisperSTTService` and `OpenAISTTService` can optionally push empty transcripts downstream when VAD fires but no speech was actually transcribed.
- `AssemblyAIConnectionParams` adds `vad_threshold` for U3 Pro, which helps align provider-side detection with external VAD.

These changes matter when you tune speech sensitivity live or need the agent to resume speaking cleanly after a false-positive VAD event.

## STT and turn updates (1.3.0)

- `CartesiaTurnsSTTService` supports Cartesia Streaming ASR v2 turn-based WebSocket sessions and maps `turn.start`, `turn.update`, `turn.end`, eager-end, and resume events into Pipecat speech/turn frames.
- `SonioxSTTService.Settings.max_endpoint_delay_ms` controls the maximum endpointing delay before a turn finalizes, and Soniox settings updates now reconnect gracefully instead of hard disconnecting.
- `STTService.supports_ttfs` lets turn-based STT services opt out of TTFS latency semantics; when false, `STTMetadataFrame` uses `ttfs_p99_latency=0.0` without noisy warnings.
- Smart Turn v3 no longer imports `transformers` at module import time; cold start and memory footprint are much lower, and `transformers` is no longer part of the base install.

## Strategy reset() deprecated (1.6.0)

`reset()` on `BaseUserTurnStartStrategy` and `BaseUserTurnStopStrategy` is deprecated. Reset logic should move to the new `handle_user_turn_started()` / `handle_user_turn_stopped()` lifecycle callbacks. For backward compatibility, the base classes' default `handle_user_turn_started()` / `handle_user_turn_stopped()` still call `reset()`, so existing custom strategies keep working, but overriding `reset()` now emits a `DeprecationWarning` when the class is defined. Planned removal is `2.0.0`; migrate custom turn strategies to the lifecycle callbacks rather than adding new logic to `reset()`.

## Proposed turn frames and external strategies (1.8.0)

Since `1.8.0`, every in-repo service with built-in turn detection emits **proposal** frames (`ProposedUserStartedSpeakingFrame` / `ProposedUserStoppedSpeakingFrame`) instead of real turn frames, and `ExternalUserTurnStrategies` resolves those proposals into `UserStartedSpeakingFrame` / `UserStoppedSpeakingFrame`. Turn strategy configuration is now a single subclassable place that decides when turns start and stop.

- Services affected: the AssemblyAI, Cartesia Ink-2, Deepgram Flux, Gladia, Sarvam, Soniox, Speechmatics, and OpenAI Realtime STT services, plus the OpenAI, xAI, and Inworld realtime LLM services.
- Third-party services that still emit `UserStartedSpeakingFrame` / `UserStoppedSpeakingFrame` directly keep working unchanged; switching them to proposal frames hands interruption handling back to the pipeline.
- `OpenAIRealtimeSTTService` (transcription-only) and `SarvamSTTService` recommend `ExternalUserTurnStrategies` when their server-side VAD is enabled.
- See `examples/turn-management/turn-management-custom-external-turn-strategy.py` for a stop strategy that holds the turn open past the service's proposal so a trailing afterthought can reopen it.

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
- For half-finished utterances or barge-in heavy UX, prefer `FilterIncompleteUserTurnStrategies` over legacy `filter_incomplete_user_turns` flags.
