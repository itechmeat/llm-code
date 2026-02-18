# OpenClaw Concepts (Additional Coverage)

## Confirmed concepts (content extracted)

### Agent loop

- Agent loop is a serialized run path: intake, prompt assembly, model inference, tools, streaming, persistence.
- Queue lanes prevent race conditions across concurrent requests.
- Lifecycle/tool/assistant streams provide observability and wait/timeout semantics.

### System prompt and context

- System prompt is OpenClaw-composed per run and supports `full` / `minimal` / `none` prompt modes.
- Context window includes prompt, transcript, tool results, attachments, and schema overhead.
- Bootstrap files are injected into context and should remain concise.

### Workspace, OAuth, and memory

- Workspace is default execution root and memory surface, but not a hard sandbox by itself.
- OAuth profiles are per-agent and refreshed with lock-safe credential handling.
- Memory is markdown-first (daily + durable layers) with optional semantic/hybrid retrieval.

### Session pruning and compaction

- Session pruning trims old tool results in-memory (non-persistent).
- Compaction summarizes older context and persists the summary in transcript.
- Use both as complementary controls for long-running sessions.

### Presence and messages

- Presence is best-effort gateway/client/node visibility; stable `instanceId` prevents duplicate entries.
- Message flow includes dedupe, optional inbound debounce, queue modes, and channel-aware outbound behavior.

## Source availability notes

The following Concepts URLs were listed in navigation during ingestion but returned 404 or non-extractable content:

- `https://docs.openclaw.ai/concepts/agent-runtime`
- `https://docs.openclaw.ai/concepts/bootstrapping`
- `https://docs.openclaw.ai/concepts/session-management`
- `https://docs.openclaw.ai/concepts/sessions`
- `https://docs.openclaw.ai/concepts/session-tools`
- `https://docs.openclaw.ai/concepts/multi-agent-routing`
- `https://docs.openclaw.ai/concepts/streaming-and-chunking`
- `https://docs.openclaw.ai/concepts/retry-policy`
- `https://docs.openclaw.ai/concepts/command-queue`

Fallback coverage for these topics is integrated in `SKILL.md` and supporting references (`architecture`, `operations`, `tools`, `gateway`).
