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
  "modelId": "inworld-tts-1.5-max"
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

## Models

| Model        | ID                     | Latency | Price        |
| ------------ | ---------------------- | ------- | ------------ |
| TTS 1.5 Max  | `inworld-tts-1.5-max`  | ~200ms  | $10/1M chars |
| TTS 1.5 Mini | `inworld-tts-1.5-mini` | ~120ms  | $5/1M chars  |

**Languages:** en, zh, ja, ko, ru, it, es, pt, fr, de, pl, nl, hi, he, ar

## Integrations

| Platform   | Type                |
| ---------- | ------------------- |
| Pipecat    | `InworldTTSService` |
| LiveKit    | Agents plugin       |
| Ultravox   | Native              |
| Vapi       | Native              |
| Voximplant | Native              |
