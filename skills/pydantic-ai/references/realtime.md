# Realtime (Speech-to-Speech)

Pydantic AI's realtime API runs a conversation directly with a speech-to-speech model: audio in, audio out, with tool calls in the middle. Between `2.48.0` and `2.59.0` the realtime surface gained a new provider family, session-level controls, and two lifecycle events.

## Model support

| Model | Class | Since |
| --- | --- | --- |
| OpenAI GPT-Live | `OpenAILiveModel` | `2.51.0` |
| Gemini Live | `GoogleModel` (live mode) | earlier; `gemini-3.8-live` added in `2.50.0` |
| ElevenLabs Realtime | `ElevenLabsRealtimeModel` | `2.58.0` |
| Azure AI Voice Live | `azure_voice_live_voice` on the Azure provider | `2.52.0` |
| Amazon Nova Sonic | via the Bedrock provider | earlier |

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAILiveModel

model = OpenAILiveModel('gpt-live')
agent = Agent(model)
```

- `2.52.0` enables **browser WebRTC** on OpenAI GPT-Live, so a browser client can talk to the model directly.
- `2.52.0` adds the realtime `async_tool_call_mode` profile setting, which decides whether tool calls run asynchronously while the model keeps speaking.
- `2.52.0` adds `azure_voice_live_voice` to the Azure provider for Azure AI Voice Live sessions.

## Session control

- `RealtimeSession.wait_for_reply()` (`2.49.0`) - await the model's next reply instead of consuming the event stream manually.
- `context_window_used` (`2.51.0`) - how much of the context window the session has consumed so far.
- `UsageLimitUnavailableWarning` (`2.59.0`) - raised when a provider reports no usage at all. It distinguishes "the provider omitted usage" from "the provider reported zero", so a billing check is not triggered by a missing field.

## Lifecycle events

`2.59.0` added two realtime lifecycle events:

- `AnswersRevised` - the provider revised an answer it had already produced (common with live reasoning models).
- `OutputItemCut` - the provider cut an output item short.

Handle both explicitly; a client that assumes every answer is final will show text that the provider later retracts.

## Provider-neutral errors (`2.59.0`)

Realtime sessions now raise the same provider-neutral error categories as the rest of the framework:

| Error | Meaning |
| --- | --- |
| `ModelRateLimitError` | the provider rate-limited the request |
| `ModelUnavailableError` | the model is not currently served |
| `ModelServerError` | the provider failed on its side |
| `ModelContextWindowExceededError` | the context window is full |

`ModelHTTPError.for_category` maps a raw provider HTTP error onto one of those categories, so a `try/except ModelRateLimitError` works across providers.

## MCP tool calls in a realtime session

`ToolKind` typed tool parts (`2.58.0`) let any module emit a typed tool part, which is what a realtime session needs to surface a tool call without going through the text tool-call format.

## Practical notes

- Speech-to-speech models bill differently from chat models; check the provider's realtime pricing before routing a whole call center through them.
- Tool calls in realtime sessions are a latency source: the model keeps the audio turn alive while the tool runs.
- `2.57.0` added `MetaProvider` for Meta Muse models - a non-realtime provider, useful as a fallback when the live model is unavailable.
