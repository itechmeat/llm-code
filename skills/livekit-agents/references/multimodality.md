# Multimodality

LiveKit Agents can combine modalities within one session: audio (speech), text (chat + transcripts), and vision (images/live video).

## Modalities and typical use

- **Speech & audio**: realtime mic input → STT/turn detection/interruptions → spoken output.
- **Text & transcriptions**: text chat + transcript events; useful for hybrid UX and accessibility.
- **Vision**: images and live video feeds for visual understanding (e.g., “see what the user shows”).

## Design guidance (high level)

- Decide what is the _primary_ interaction channel (voice vs text) and enforce consistent output rules.
- When mixing voice + text, treat transcripts as _state_ (context) and text messages as _commands_ unless you explicitly design otherwise.
- For vision, be explicit about what the agent should do with frames/images (describe, extract, answer, detect) to avoid vague model behavior.

## Speech & audio (latency + interruption control)

### Frontend: “instant connect” (pre-connect audio buffer)

- Microphone capture can start locally _while the agent is connecting_.
- Buffered audio/transcripts are sent on connect (topic `lk.agent.pre-connect-audio-buffer`).
- If no agent connects before timeout, the buffer is discarded.

### Preemptive generation

- Lets the agent start generating a response as soon as the **final transcript** is ready (before end-of-speech is committed).
- If your pipeline mutates context/tools in `on_user_turn_completed`, the preemptive response may be cancelled and regenerated.
- Not guaranteed to reduce latency; verify in observability.

### Speaking APIs (session)

- `session.say(...)`: speak a predefined message.
  - Can be text (TTS), audio-only (no transcript/history), or text+audio.
  - For realtime models: `say()` still requires a TTS plugin; otherwise prefer `generate_reply()`.
- `session.generate_reply(...)`: ask the LLM to generate a response.
  - `instructions=...`: instructions are _not_ recorded in chat history.
  - `user_input=...`: input is recorded in chat history.

### SpeechHandle (cancellation + orchestration)

- `say()` and `generate_reply()` return a `SpeechHandle` you can await to know when playout finished.
- Interruption-aware patterns:
  - check `handle.interrupted` and cancel long-running work (HTTP calls, background tasks)
  - wait for playout before ending a call/job (graceful hangup)

### Background audio

- `BackgroundAudioPlayer` can play ambient/thinking sounds aligned to the agent lifecycle.
- Sources: local files, built-in clips, or raw audio frames.
- Limitation: “thinking sounds” not supported in Node.js (per docs).

### TTS quality controls

- Pronunciation: many providers support SSML (phoneme, say-as, lexicon, emphasis, break, prosody).
- Volume: adjust in the `tts_node` / `realtime_audio_output_node` (or in the frontend playback).

## Text & transcriptions (topics + hybrid UX)

### What gets published

- When using `AgentSession`, transcriptions and agent text output are typically enabled by default.
- Transcript stream topic: `lk.transcription`.
  - Attributes include `lk.transcribed_track_id` and the transcribed participant identity.
- Incoming chat messages are received on topic: `lk.chat`.

### Enable/disable knobs

- Disable transcription output:
  - Python: `RoomOptions(text_output=False)`
  - Node: `outputOptions: { transcriptionEnabled: false }`
- Disable text input:
  - Python: `RoomOptions(text_input=False)`
  - Node: `RoomInputOptions: { textEnabled: false }`

### Synchronization options

- With voice+text enabled, the agent’s speech text can be synchronized word-by-word.
- If interrupted, transcription truncates to match what was spoken.
- If you need early text output (not tied to playout), disable sync via `sync_transcription = false`.
- Some TTS plugins can improve alignment (word-level timing); docs call out Cartesia and ElevenLabs.

### Handling incoming text while speaking

- Default behavior: interrupt current speech and respond to the text message.
- Common pattern: `session.interrupt()` then `session.generate_reply(user_input=message)`.

### Text-only or hybrid sessions

- You can disable audio input/output for the whole session or toggle dynamically.
- Use `session.input.set_audio_enabled(...)` and `session.output.set_audio_enabled(...)`.
- When audio output is disabled, text responses are sent without speech synchronization.

### Interim vs final transcripts (avoid duplicates)

- A segment can emit interim and final streams.
- Use `lk.transcription_final` to distinguish:
  - interim: `false`
  - final: `true`
- Interim and final share `segment_id` and `transcribed_track_id`; replace interim with final to avoid duplicate logs/UI.

## Vision (images, sampled frames, live video)

### Images in chat context

- Chat context supports images alongside text.
- Use `ImageContent(...)` inside a chat message.
- Image sources:
  - base64 data URL
  - external URL (provider support varies)
  - a frame from a video track
- Keep context window size in mind: more/larger images can slow responses.

### Upload images from frontend

- Frontend can upload files (e.g., `sendFile` in LiveKit SDK).
- Agent pattern: register a byte stream handler for a topic (e.g., `"images"`), read bytes, base64-encode, then update chat context with an `ImageContent(data-url)`.
- Operational note: keep references to tasks to avoid GC of in-flight async tasks.

### Video via sampled frames (pipeline models)

- Many LLMs can “see” still images but are not trained for motion; don’t expect strong temporal reasoning from many sequential frames.
- A pragmatic pattern: store only the **latest** frame and attach it to the user turn when the turn completes.

### Live video input (realtime models)

- Requires a realtime model with video support (docs mention Gemini Live / OpenAI Realtime).
- Enable with `RoomOptions(video_input=True)` (Python docs).
- Default sampling: 1 fps while user speaks, 1 frame per 3s otherwise.
- Only the most recently published video track is used.
- Video input is passive (does not affect turn detection). For non-conversational vision tasks, use manual turn control and trigger actions on a schedule.

### Frame encoding and cost controls

- Default `ImageContent` encoding: JPEG at native size.
- Resize controls: `inference_width` / `inference_height` (fit within dimensions while preserving aspect ratio).
- For more control: encode frames manually (e.g., PNG + resize strategy) and pass as a data URL.
- Some providers support `inference_detail` (`high`/`low`/`auto`) to trade off tokens vs quality.
