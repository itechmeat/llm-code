# API Reference

## Base URL

```
https://api.inworld.ai/tts/v1
```

## Authentication

```
Authorization: Basic {INWORLD_API_KEY}
```

## Endpoints

### Synthesize Speech

**POST** `/voice`

```json
{
  "text": "Hello, world!",
  "voiceId": "Ashley",
  "modelId": "inworld-tts-2"
}
```

**Response:**

```json
{
  "audioContent": "base64-encoded-audio",
  "timestampInfo": {...}
}
```

### Streaming

**POST** `/voice:stream`

Same body. Returns chunked audio + alignment per chunk.

## Audio Formats

| Format        | Sample Rate | Use Case              |
| ------------- | ----------- | --------------------- |
| MP3 (default) | 16-48kHz    | Broad compatibility   |
| LINEAR16      | 8-48kHz     | Low latency streaming |
| OPUS          | 8-48kHz     | Web/mobile            |
| MULAW/ALAW    | 8kHz        | Telephony             |

```json
{ "audio_config": { "audio_encoding": "LINEAR16", "sample_rate_hertz": 48000 } }
```

## Request Parameters

| Parameter                        | Default  | Description                      |
| -------------------------------- | -------- | -------------------------------- |
| `text`                           | required | Text to synthesize               |
| `voiceId`                        | required | Voice ID (built-in or cloned)    |
| `modelId`                        | required | Model ID                         |
| `audio_config.audio_encoding`    | `MP3`    | MP3, LINEAR16, OPUS, MULAW, ALAW |
| `audio_config.sample_rate_hertz` | varies   | 8000-48000                       |
| `temperature`                    | 1.1      | Expressiveness (0.0-2.0)         |
| `talking_speed`                  | 1.0      | Speed (0.5-1.5)                  |
| `timestampType`                  | none     | WORD, CHARACTER                  |
| `deliveryMode`                   | varies   | `STABLE`, `BALANCED`, `CREATIVE` |
| `language`                       | auto     | Target language / locale hint    |

## Models

| Model        | ID                     | Latency | Price    |
| ------------ | ---------------------- | ------- | -------- |
| TTS-2        | `inworld-tts-2`        | latest  | see docs |
| TTS 1.5 Max  | `inworld-tts-1.5-max`  | legacy  | legacy   |
| TTS 1.5 Mini | `inworld-tts-1.5-mini` | legacy  | legacy   |

**Languages:** en, zh, ja, ko, ru, it, es, pt, fr, de, pl, nl, hi, he, ar

`TTS-2` notes:

- `deliveryMode` lets you choose consistency vs expressiveness.
- Set `language` explicitly when reusing a voice across multiple languages or when localizing a voice for a specific target language.

## Integrations

| Platform   | Type                |
| ---------- | ------------------- |
| Pipecat    | `InworldTTSService` |
| LiveKit    | Agents plugin       |
| Ultravox   | Native              |
| Vapi       | Native              |
| Voximplant | Native              |
