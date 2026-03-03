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

## Interruptions

When interruptions are enabled (docs say default enabled), starting a user turn can:

- stop the bot from speaking
- clear pending audio/text output
- allow natural “barge-in” behavior

You can disable interruptions on the start strategy for experiences where barge-in is undesirable.

## Practical checklist

- Keep interruptions enabled unless you have a strong UX reason to disable them.
- Prefer Smart Turn when you want fewer awkward cutoffs / long waits.
- If your environment is noisy, adjust `start_secs` and `min_volume` conservatively and re-test.
