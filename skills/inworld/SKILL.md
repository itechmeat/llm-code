---
name: inworld
description: "Inworld TTS API. Covers voice cloning, audio markups, timestamps. Use when integrating Inworld text-to-speech, cloning voices, adding audio markups (SSML-like), or aligning viseme timestamps. Keywords: Inworld, text-to-speech, TTS, voice cloning, visemes."
metadata:
  version: "2"
  release_date: "2026-05-05"
---

# Inworld AI

Text-to-Speech platform with voice cloning, audio markups, and timestamp alignment.

## Quick Navigation

| Topic         | Reference                                       |
| ------------- | ----------------------------------------------- |
| Installation  | [installation.md](references/installation.md)   |
| Voice Cloning | [cloning.md](references/cloning.md)             |
| Voice Control | [voice-control.md](references/voice-control.md) |
| API Reference | [api.md](references/api.md)                     |

## When to Use

- Text-to-speech audio generation
- Voice cloning from 5-15 seconds of audio
- Emotion-controlled speech (`[happy]`, `[sad]`, etc.)
- Word/phoneme timestamps for lip sync
- Custom pronunciation with IPA

## Models

| Model        | ID                     | Latency | Price       |
| ------------ | ---------------------- | ------- | ----------- |
| TTS-2        | `inworld-tts-2`        | latest  | see pricing |
| TTS 1.5 Max  | `inworld-tts-1.5-max`  | legacy  | legacy      |
| TTS 1.5 Mini | `inworld-tts-1.5-mini` | legacy  | legacy      |

## Minimal Example

```python
import requests, base64, os

response = requests.post(
    "https://api.inworld.ai/tts/v1/voice",
    headers={"Authorization": f"Basic {os.getenv('INWORLD_API_KEY')}"},
    json={"text": "Hello!", "voiceId": "Ashley", "modelId": "inworld-tts-1.5-max"}
)
audio = base64.b64decode(response.json()['audioContent'])
```

## Key Features

- **15 languages** — en, zh, ja, ko, ru, it, es, pt, fr, de, pl, nl, hi, he, ar
- **Instant cloning** — 5-15 seconds audio, no training
- **Audio markups** — `[happy]`, `[laughing]`, `[sigh]` (English only)
- **Timestamps** — word, phoneme, viseme timing for lip sync
- **Streaming** — `/voice:stream` endpoint
- **TTS-2 steering** — natural-language bracketed directions such as `[say excitedly]` or `[whisper in a hushed style]`
- **Delivery mode** — `STABLE`, `BALANCED`, `CREATIVE` trade consistency for emotional range
- **Cross-lingual synthesis** — reuse one voice across multiple languages; voice localization improves native-sounding output

## Release Highlights (TTS-2)

- `Realtime TTS-2` becomes the new primary model line via `modelId="inworld-tts-2"`.
- Steering moves beyond the older fixed emotion tags: free-form bracketed directions can control style, pitch, speed, intensity, and non-verbals.
- Multilingual coverage expands with production quality across 15 languages and broader experimental coverage beyond that.
- `deliveryMode` adds a stability-vs-creativity knob, and specifying `language` matters more for cross-lingual output quality.

## Prohibitions

- Audio markups work **only in English**
- Use **ONE** emotion markup at text **beginning**
- Match voice language to text language
- Instant cloning may not work for children's voices or unique accents

## Links

- [Documentation](https://docs.inworld.ai/docs/tts/tts)
- [Changelog](https://docs.inworld.ai/docs/release-notes/tts)
- [Platform](https://platform.inworld.ai/)
