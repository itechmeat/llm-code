# Models

Voice agents need models for speech input/output and intelligence. LiveKit Agents supports two main approaches:

- **Pipeline**: STT → LLM → TTS (mix-and-match specialized models)
- **Realtime**: speech-to-speech models (lower latency, can support live video on some providers)

## LiveKit Inference vs plugins

- **LiveKit Inference** (LiveKit Cloud): access many providers/models without installing extra plugins.
- **Plugins** (open source): connect directly to providers; Python uses optional extras on `livekit-agents`, Node uses separate `@livekit/agents-plugin-*` packages.

## Configuration model (AgentSession)

- `AgentSession` takes `stt`, `llm`, `tts`.
- You can mix inference + plugins in one session.
- You can change models across phases (often via workflows/agent handoffs).

## OpenAI-compatible endpoints

- Many providers implement OpenAI-style APIs. Docs note you can often use the OpenAI plugin with `base_url` + provider API key.
- Ensure you select the right “API mode” for the provider’s implementation (docs refer to an API modes guide).

## Realtime models (speech-to-speech)

### Provider support (docs)

- Amazon Nova Sonic (Python)
- Azure OpenAI Realtime (Python, Node)
- Gemini Live (Python, Node)
- OpenAI Realtime (Python, Node)
- Ultravox Realtime (Python)
- xAI Grok Voice Agent API (Python)

### Full realtime vs “half-cascade”

- Full realtime: model consumes + produces audio directly (no STT/TTS pipeline).
- Half-cascade: use realtime model for speech understanding but keep speech output controlled via a separate TTS:
  - configure realtime model with `modalities=["text"]`
  - provide a TTS instance in `AgentSession`

### Practical caveats

- Realtime models typically don’t support a strict scripted “say this exact text” API; `generate_reply(instructions=...)` is not guaranteed to follow a script word-for-word.
  - If you need exact scripts, prefer half-cascade (text output → TTS).
- Turn detection: docs recommend using the realtime model’s built-in turn detection when possible.
- Transcriptions: realtime models generally do not provide interim transcripts; user transcripts can arrive delayed (sometimes after the agent response).
  - If you need realtime transcripts, use a pipeline (STT→LLM→TTS) or add a separate STT plugin.

## LiveKit Inference (LiveKit Cloud)

### What it provides

- Access to many STT/LLM/TTS providers via LiveKit Cloud without installing extra plugins.

### How to configure

- Use `inference.STT(...)`, `inference.LLM(...)`, `inference.TTS(...)` in `AgentSession`.
- Shortcut: pass string descriptors instead of classes.

### Model descriptor format (examples)

- LLM: `openai/gpt-4.1-mini`, `google/gemini-3-pro`, `deepseek-ai/deepseek-v3`.
- STT: `deepgram/nova-3:en` (provider/model + language suffix).
- TTS: `cartesia/sonic-3:<voice-id>` (provider/model + voice).

### Billing note

- Docs state Inference billing is usage-based; pricing depends on LiveKit Cloud plan.
