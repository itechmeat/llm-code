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

As of 0.0.105, word timestamp handling is effectively built into the base TTS flow rather than something you opt into with older word/audio-context subclasses.

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

Recent service notes (`1.6.0` line):

- **`DeepgramFluxTTSService`** (new): websocket TTS service for Deepgram's Flux TTS (early access) at `wss://api.deepgram.com/v2/speak`. LLM tokens stream straight to the server as they arrive (`TextAggregationMode.TOKEN` is the default for this service; pass `text_aggregation_mode=TextAggregationMode.SENTENCE` to aggregate sentences instead), and each bot response is synthesized as a discrete turn with prosody carried across turns on a single connection. Flux has no way to cancel the active turn yet, so interruptions reconnect the websocket. See `examples/voice/voice-deepgram-flux.py` (all-Flux STT + TTS bot).
- **ElevenLabs default model changed**: `ElevenLabsTTSService` and `ElevenLabsHttpTTSService` now default to `eleven_flash_v2_5` instead of `eleven_turbo_v2_5`, since ElevenLabs deprecated `eleven_turbo_v2_5`. Only affects callers that don't explicitly set `model`; pass `model="eleven_turbo_v2_5"` explicitly if you still need the old default.
- **`PronunciationDictionaryLocator` deprecated**: the `pronunciation_dictionary_locators` parameter on `ElevenLabsTTSService` / `ElevenLabsHttpTTSService` is deprecated because dictionary substitutions can rewrite spoken words in ways that break alignment-based word-completion tracking (used to attribute spoken text back to conversation context). Use the `text_transforms` parameter with `replace_text` (added in `1.5.0`) instead — those transforms run client-side and are tracked correctly. Removal is planned for `2.0.0`.

Recent service notes (`1.7.0` line):

- **`PocketTTSService`** (new): local CPU-only TTS built on kyutai-labs [pocket-tts](https://github.com/kyutai-labs/pocket-tts). Supports English, French, German, Italian, Portuguese, and Spanish, predefined voices, and voice cloning from a wav file or `hf://` voice prompt. Install with `pip install "pipecat-ai[pocket-tts]"`.
- **`XTTSService` deprecated**: the [Coqui XTTS streaming server](https://github.com/coqui-ai/xtts-streaming-server) it connects to has been unmaintained since early 2024 and pins a commit of the discontinued `coqui-ai/TTS`, and the XTTS-v2 model is licensed for non-commercial use only. Use `KokoroTTSService` / `PiperTTSService` for local TTS, or the community-maintained [`pipecat-xtts-vllm`](https://docs.pipecat.ai/api-reference/server/services/tts/xtts-vllm) package to stay on XTTS. Removal planned for `2.0.0`.
- `AzureTTSService` / `AzureHttpTTSService` gain an opt-in `force_locale` setting (`AzureTTSSettings`) that wraps synthesized text in SSML's `<lang xml:lang>` element, so multilingual voices (e.g. `en-US-EmmaMultilingualNeural`) speak in the configured locale instead of auto-detecting per segment.

Recent service notes (`1.3.0` line):

- Rime `RimeTTSService` / `RimeHttpTTSService` default to the `coda` model instead of `arcana`; set `model="arcana"` explicitly to preserve old behavior.
- Rime `coda` ignores `temperature`, `top_p`, and `repetition_penalty`, while `timeScaleFactor` controls playback speed for `arcana` and `coda`.
- Gradium defaults to voice `_6Aslh2DxfmnRLmP`.
- Azure TTS completion now waits for the word-boundary queue so the final word is observed before `TTSStoppedFrame`.
- Skipped TTS frames keep their order until previous spoken frames finish, and `TTSTextFrame.raw_text` preserves original LLM text structure when word timestamps are enabled.

Recent service notes (`1.0.0` line):

- `MistralTTSService` adds SSE-based streaming TTS with automatic resampling.
- ElevenLabs services now support `pcm_32000` / `pcm_48000` and an `enable_logging=False` zero-retention mode.

## Audio context changes (0.0.105)

- Audio context management now lives in `TTSService` rather than `AudioContextTTSService`.
- WebSocket TTS providers now inherit from `WebsocketTTSService` directly.
- `AudioContextTTSService`, `AudioContextWordTTSService`, `WordTTSService`, `WebsocketWordTTSService`, and `InterruptibleWordTTSService` are deprecated.
- `supports_word_timestamps` was removed from `TTSService.__init__()`; do not pass it from custom subclasses anymore.

If you maintain custom TTS classes, update inheritance and constructor calls before upgrading.

## Concurrent audio contexts (Cartesia, 0.0.105)

`CartesiaTTSService` can synthesize the next sentence while the previous one is still playing by disabling frame-processing pauses and routing each sentence through its own audio context queue. Use this when you want lower perceived latency without waiting for the prior sentence to finish playback.

## Practical checklist

- Use WebSocket TTS providers when latency is critical.
- Capture spoken text (not just LLM text) in context for correctness under interruptions.
- Decide upfront how you will handle URLs/code/structured output so the bot doesn’t read garbage aloud.
- If you still call `TTSService.say()`, migrate to pushing `TTSSpeakFrame` into the pipeline.
