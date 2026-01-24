# Voice Cloning

## Cloning Types

| Type                | Audio Required | Availability         |
| ------------------- | -------------- | -------------------- |
| Instant (zero-shot) | 5-15 seconds   | All users via Portal |
| Professional        | 30+ minutes    | Contact sales        |

## Instant Cloning via Portal

1. Go to **TTS Playground** → **Clone Voice**
2. Choose **Upload audio** or **Record audio**
3. Name voice, select matching language
4. Upload/record up to 3 samples (5-15 seconds each)
5. Enable "Remove background noise" if needed
6. Click Continue → wait for validation
7. Test and copy `voiceId` for API use

## Audio Requirements

- Formats: WAV, MP3, WebM
- Max total size: 16MB
- Samples > 15 seconds are auto-trimmed
- Match language to text you'll synthesize

## Recording Tips

- Find quiet environment
- Keep reasonable mic distance
- Speak expressively (varied emotions)
- Use suggested scripts (Math Tutor, AI companion, etc.)

## API Usage

```python
response = requests.post(
    "https://api.inworld.ai/tts/v1/voice",
    headers={"Authorization": f"Basic {os.getenv('INWORLD_API_KEY')}"},
    json={
        "text": "Hello!",
        "voiceId": "your-cloned-voice-id",  # From TTS Playground
        "modelId": "inworld-tts-1.5-max"
    }
)
```

## Limitations

- Instant cloning may not perform well for:
  - Children's voices
  - Unique accents
- Use professional cloning for these cases
