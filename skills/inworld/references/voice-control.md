# Voice Control

## Audio Markups (English only, experimental)

### Emotion & Delivery Style

Place at **beginning** of text. Use only ONE per request:

```text
[happy] I can't believe this is happening!
[sad] I really miss those days.
[angry] This is unacceptable!
[surprised] You did what?!
[fearful] I heard something outside...
[disgusted] That's revolting.
[laughing] Oh that's hilarious!
[whispering] Don't let them hear us.
```

**Split multiple emotions into separate API calls.**

### Non-Verbal Sounds

Can be used anywhere in text:

```text
[clear_throat] Did you hear me? [sigh] You never listen!
[breathe] Let me think... [cough] Excuse me.
[laugh] That's so funny! [yawn] I'm tired.
```

## Custom Pronunciation (IPA)

Use `/phonemes/` for uncommon words:

```json
{ "text": "Your adventure in /kri:t/ begins today." }
```

**Finding IPA:**

- Ask LLM: "What are the IPA phonemes for Crete, pronounced like kreet?"
- Use Vocabulary.com IPA guide

## Timestamps (English only)

Enable with `timestampType`:

| Type        | Returns                          | Use Case |
| ----------- | -------------------------------- | -------- |
| `WORD`      | Word timing + phonemes + visemes | Lip sync |
| `CHARACTER` | Character timing                 | Karaoke  |

**Note:** Increases latency (especially non-streaming).

### Request

```json
{
  "text": "Hello, world!",
  "voiceId": "Ashley",
  "modelId": "inworld-tts-1.5-max",
  "timestampType": "WORD"
}
```

### Response (TTS 1.5)

```json
{
  "timestampInfo": {
    "wordAlignment": {
      "words": ["Hello,", "world!"],
      "wordStartTimeSeconds": [0, 0.28],
      "wordEndTimeSeconds": [0.28, 0.8],
      "phoneticDetails": [
        {
          "wordIndex": 0,
          "phones": [
            { "phoneSymbol": "h", "startTimeSeconds": 0, "durationSeconds": 0.07, "visemeSymbol": "aei" },
            { "phoneSymbol": "l", "startTimeSeconds": 0.1, "durationSeconds": 0.09, "visemeSymbol": "l" }
          ],
          "isPartial": false
        }
      ]
    }
  }
}
```

## Viseme Symbols

| Viseme       | Sounds                    |
| ------------ | ------------------------- |
| `aei`        | Open vowels (a, e, i, ə)  |
| `o`          | Rounded vowels (o, ʊ)     |
| `ee`         | Front vowels (i, ɪ)       |
| `bmp`        | Bilabial (b, m, p)        |
| `fv`         | Labiodental (f, v)        |
| `l`          | Lateral (l)               |
| `r`          | Rhotic (r, ɝ)             |
| `th`         | Dental (θ, ð)             |
| `qw`         | Rounded (w)               |
| `cdgknstxyz` | Alveolar/velar consonants |
