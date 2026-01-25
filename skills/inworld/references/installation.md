# Installation & Quickstart

## API Key

1. Sign up at https://platform.inworld.ai/
2. Go to Settings → API Keys
3. Create and copy Base64 credentials

```bash
export INWORLD_API_KEY='your-base64-api-key-here'
```

## Basic Request (Python)

```python
import requests
import base64
import os

response = requests.post(
    "https://api.inworld.ai/tts/v1/voice",
    headers={
        "Authorization": f"Basic {os.getenv('INWORLD_API_KEY')}",
        "Content-Type": "application/json"
    },
    json={
        "text": "Hello, world!",
        "voiceId": "Ashley",
        "modelId": "inworld-tts-1.5-max"
    }
)

audio_content = base64.b64decode(response.json()['audioContent'])
with open("output.mp3", "wb") as f:
    f.write(audio_content)
```

## Streaming Request

```python
import requests
import base64
import os
import json

response = requests.post(
    "https://api.inworld.ai/tts/v1/voice:stream",
    headers={
        "Authorization": f"Basic {os.getenv('INWORLD_API_KEY')}",
        "Content-Type": "application/json"
    },
    json={
        "text": "Your text here...",
        "voiceId": "Ashley",
        "modelId": "inworld-tts-1.5-max",
        "audio_config": {
            "audio_encoding": "LINEAR16",
            "sample_rate_hertz": 48000,
        }
    },
    stream=True
)

for line in response.iter_lines():
    chunk = json.loads(line)
    audio_chunk = base64.b64decode(chunk["result"]["audioContent"])
    # Process audio_chunk (skip first 44 bytes WAV header)
```
