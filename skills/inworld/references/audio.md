# Audio Generation

## Supported Formats

| Format        | Sample Rate          | Notes                 |
| ------------- | -------------------- | --------------------- |
| MP3 (default) | 16-48kHz, 32-320kbps | Broad compatibility   |
| LINEAR16      | 8-48kHz, 16-bit      | Low latency streaming |
| OPUS          | 8-48kHz, 32-192kbps  | Web/mobile apps       |
| MULAW         | 8kHz                 | Telephony             |
| ALAW          | 8kHz                 | Telephony             |

## Audio Config

```json
{
  "audio_config": {
    "audio_encoding": "LINEAR16",
    "sample_rate_hertz": 48000
  }
}
```

## Voice Parameters

| Parameter       | Default | Range   | Effect                       |
| --------------- | ------- | ------- | ---------------------------- |
| `temperature`   | 1.1     | 0.0-2.0 | Higher = more expressive     |
| `talking_speed` | 1.0     | 0.5-1.5 | 0.5 = half speed, 1.5 = 1.5x |

## Emphasis

Use asterisks to emphasize words:

```json
{ "text": "I *really* need this done today" }
```

## Languages

```
en, ar, zh, nl, fr, de, he, hi, it, ja, ko, pl, pt, ru, es
```

**Best Practice:** Match voice language to text language for best quality.

## Built-in Voices

Available in TTS Playground. For custom voices, use voice cloning (min 5 seconds audio).
