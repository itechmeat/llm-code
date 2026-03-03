# Server APIs: supported services (how to think about integrations)

## Service categories

Server docs organize integrations into categories such as:

- Transports (audio/video exchange)
- Serializers (frame ↔ media stream conversion for websockets)
- Speech-to-text (STT)
- Large language models (LLM)
- Text-to-speech (TTS)
- Speech-to-speech (multimodal realtime models)
- Image generation
- Video/avatar
- Memory
- Vision
- Analytics & monitoring

## Setup pattern: optional dependencies via extras

Integrations are typically installed via provider-specific extras (e.g. `pipecat-ai[openai]`).
See: `references/installation.md`.

This implies:

- base install may be minimal
- each provider integration can pull its own dependency set

## Practical checklist

- Decide your transport first (WebRTC vs telephony websocket) because it shapes latency and reliability.
- Then pick STT/LLM/TTS based on whether you need streaming + timestamps, and how you will handle interruptions.
- Keep dependencies explicit by using the documented extras rather than ad-hoc installs.

## Links

- Server API reference: https://reference-server.pipecat.ai/
