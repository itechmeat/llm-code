# Files and images (RTVI send-file, FileResolver, FileStorage)

`1.13.0` adds the ability for a client to send a **file or an image to the bot**
and have it become part of the LLM context.

The pipeline is deliberately split in two halves:

- **Capture** (client → bot): the client uploads bytes and sends an RTVI
  `send-file` message. The bot stores the payload as a frame.
- **Resolution** (bot → provider): the LLM service resolves the URL *right
  before each completion*, because only the service knows what its provider
  can consume.

The context itself stays canonical: it holds only the URL. The downloaded bytes
live in a resolver cache, not in the conversation history.

## Frames

Three new frames carry the payload:

- `FileRawFrame` — base class.
- `InputFileRawFrame` — a file entering the pipeline from the client side.
- `UserFileRawFrame` — a file attributed to the user.

A frame carries the file payload either as **inline base64 bytes** or as a
**URL**.

## LLMContext methods

Three new methods on the universal `LLMContext`:

- `create_file_message()` — a message holding a file given as bytes.
- `create_file_url_message()` — a message holding a file given as a URL.
- `add_file_frame_message()` — add a message built from a file frame.

They produce two universal content items:

- `file_base64` — the file inline, as a base64 **data URL**.
- `file_url` — the file as a URL.

Every adapter translates these two items into whatever its provider wants:
Anthropic, AWS Bedrock, Gemini, OpenAI Chat and OpenAI Responses are supported.

Two rules that matter when debugging:

- An **unsupported MIME type raises during conversion** instead of being
  silently dropped, so the bad message can be cleaned up (see
  `remove_invalid_file_message()` below).
- **AWS Bedrock document names are sanitized** to satisfy Bedrock's character
  restrictions for document names.

## When resolution happens

File URLs are resolved **at the LLM service, right before each completion** —
not when the file arrives, and not when the context is built.

Each adapter declares which URLs its provider can consume **directly**:

| Provider | URLs passed through to the provider |
| --- | --- |
| OpenAI Chat / Responses, Anthropic, Gemini (public) | public `http(s)` URLs, per supported MIME type |
| AWS Bedrock | `s3://` URLs, fetched with Bedrock's IAM role |
| Vertex AI (Gemini) | `gs://` URLs, fetched with the service account's IAM |
| Gemini | Files API URIs |

Those URLs are passed through and **the provider fetches them itself** — the
bot never downloads them.

Any **other** URL is downloaded by the service's `FileResolver`
(`pipecat.utils.file_resolver`) and inlined at conversion time.

## FileResolver

`FileResolver` is configured **per LLM service**, through the new
`file_resolver` parameter:

```python
from pipecat.utils.file_resolver import FileResolver

llm = OpenAILLMService(api_key=..., file_resolver=FileResolver())
```

Behavior:

- **Cache**: each file is fetched and decoded **once, not per turn**. The
  downloaded bytes live in an in-memory cache **keyed by URL**.
- **Sharing**: services that share one resolver instance (for example services
  switched between mid-session) reuse each other's downloads, while each still
  makes its own per-provider pass-through decision.
- **Immutability**: a URL is assumed to identify **immutable content**. Upload
  flows mint a fresh URL each time, so this holds by construction.
- **`forget(url)`**: forces a re-fetch when the application knows a URL's
  content changed.

### SSRF guard

`FileResolver` downloads `http(s)` URLs **only** when the resolved address is:

- publicly routable, or
- inside one of its `allowed_url_networks` CIDR ranges.

`allowed_url_networks` defaults to the `PIPECAT_ALLOWED_FILE_URL_NETWORKS`
environment variable. Other rules:

- **Redirects are refused.**
- **50 MB cap** on a downloaded file.
- Any **other scheme** is delegated to the resolver's `FileStorage`.

Subclass `FileResolver` to fetch from credentialed backends.

## FileStorage

`FileStorage` (`pipecat.utils.file_storage`) is the interface behind
`save()`:

- `LocalFileStorage` is the default implementation.
- `save()` returns a **URL the backend can later resolve**. For local storage
  that URL is `pipecat:<id>`.
- A custom backend can mint, for example, `gs://` or `s3://` URLs. The LLM
  provider may then fetch them itself, **without the bot in the loop**.
- A backend whose URLs are all uploads it owns can set **`delete_after_load`**
  (as `LocalFileStorage` does): the file is removed once its bytes are cached
  by the resolver, which then serves every later use of the file. Leave it off
  for backends whose URLs may point at shared data.

## Runner upload endpoints

The development runner gains a **session-scoped** upload endpoint that mirrors
Pipecat Cloud's session routes:

- `POST /sessions/{session_id}/files` — 50 MB cap.
- `POST /files` — a flat endpoint for transports whose clients never learn a
  session id. **No session-end cleanup** happens there.

Enable uploads with the new flag, or the env var:

- `-u/--uploads-folder <dir>`
- `PIPECAT_UPLOADS_FOLDER=<dir>`

The endpoint responds with an **RTVI file source** the client passes straight
back in `send-file`:

```json
{"type": "url", "url": "pipecat:<id>"}
```

Cleanup and limits:

- A session's uploads are **deleted when its bot session ends**.
- `--uploads-folder-max-files` (default `10`) trims the oldest uploads as a
  backstop.

Discovery: `/start` responses **advertise the route to use** as
`fileUploadUrl`, relative to the `/start` endpoint's origin. It is omitted when
uploads are disabled. Clients never reconstruct upload routes themselves.

## Custom storage: `create_file_storage()`

To back the upload endpoints with a custom `FileStorage` (a cloud bucket, for
example), define a `create_file_storage()` function **alongside your `bot()`**:

```python
def create_file_storage():
    return MyBucketFileStorage()


async def bot(runner_args):
    ...
```

Whichever host runs the bot discovers and calls it the same way, so the bot
code stays identical across hosts.

The active backend is injected into the bot as **`runner_args.file_storage`**.
Hand it to your LLM service's `FileResolver`, so `send-file` messages can
resolve the URLs it mints:

```python
resolver = FileResolver(storage=runner_args.file_storage)
llm = OpenAILLMService(api_key=..., file_resolver=resolver)
```

## Recovering from a rejected request

`LLMContext.remove_invalid_file_message()` removes the **oldest file or image
message added since the model's last successful reply**.

The OpenAI, Anthropic, AWS Bedrock and Gemini LLM services call it when they
determine a request was rejected — **including a local resolution or
conversion failure that never reached the API**. Without it, the context would
stay permanently stuck on a message the provider will always reject.

## Practical checklist

- Give the LLM service a `FileResolver` that has the same `FileStorage` the
  upload endpoints wrote to, or `pipecat:<id>` URLs cannot be resolved.
- Keep URLs immutable. Mint a new URL per upload; call
  `FileResolver.forget(url)` only when the content behind a URL really changed.
- Leave `delete_after_load` on for upload-owned backends and off for shared
  buckets.
- Expect conversion to **raise** on an unsupported MIME type — catch it at the
  boundary rather than assuming a silent skip.
- Read `fileUploadUrl` from the `/start` response instead of building upload
  routes in the client.

## Links

- Changelog: https://github.com/pipecat-ai/pipecat/blob/main/CHANGELOG.md
- RTVI protocol: https://docs.pipecat.ai/guides/learn/rtvi
