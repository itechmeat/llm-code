# Pipeline & frame model

## Pipeline model

- A **Pipeline** is a sequence of **processors**.
- Each processor consumes and emits **frames**.
- A **PipelineTask** runs the pipeline (often under a **PipelineRunner**), and you can attach observers.

## Typical voice processing flow

A common real-time flow described in the docs:

1. Transport receives streaming audio and emits audio frames
2. STT processor emits transcript/text frames
3. Context processor aggregates text + history into the LLM input
4. LLM processor emits streaming response text frames
5. TTS processor converts response text frames into audio frames
6. Transport streams output audio frames back to the user

Key insight: these steps can overlap. While later parts of the LLM response are still generating, earlier parts can already be synthesized and played.

## Frames

Frames represent “what is happening right now” in the conversation:

- Audio/video chunks
- Partial and final transcriptions
- LLM context updates
- LLM run requests
- Client/server RTVI messages
- Settings updates (e.g., STT settings)

## Frame classes and ordering

The Learn guide distinguishes frame “kinds” that affect scheduling:

- **System-like frames**: handled immediately (useful for interruptions, errors, speech start/stop events).
- **Queued frames**: processed in guaranteed order (typical audio/text/control boundaries).

Practical consequence: you can enqueue “speak then stop” and rely on the order being respected.

The docs mention example frame types such as:

- `LLMContextFrame`, `LLMRunFrame`
- `RTVIClientMessageFrame`, `RTVIServerResponseFrame`
- `STTUpdateSettingsFrame`

## Context + aggregation

Common pattern:

- Maintain an **LLMContext** (system/user/assistant messages).
- Use **aggregators** to merge streaming fragments into stable “turns”.
- Separate aggregation for user input vs assistant output is a common design.

## VAD / turn detection

The docs highlight:

- VAD analyzers (e.g., Silero) to decide “is the user speaking”.
- Smart turn analyzers for better end-of-turn decisions.

## Practical checklist

- Decide your frame boundary (token, sentence, turn) for downstream TTS.
- If your TTS supports streaming, emit smaller chunks to reduce latency.
- Keep processors single-purpose and composable.

## Parallel pipelines (branching)

Use a parallel/branching pattern when multiple processors need the same upstream frames (e.g., multi-language TTS, extra recording, side-channel analytics). Each branch receives the frames and can filter/gate them.

## Execution building blocks

- **PipelineTask**: wraps a pipeline plus execution params (sample rates, metrics flags) and observers.
- **PipelineRunner**: runs the task and can optionally handle OS signals for graceful shutdown.
- **Observers**: monitor protocol events and custom metrics (useful for debugging and production visibility).

For exact parameter names (metrics, heartbeats, idle timeout), see: `references/server-pipeline-apis.md`.

Note: the Server API docs mark an older pipeline-level interruption flag as deprecated; prefer configuring interruptions via user turn strategies.

## Lifecycle patterns

- Stop on client disconnect by cancelling the running task.
- Expect a lifecycle: starting → running → stopping → stopped (with cleanup).

## Termination (graceful vs immediate)

Learn guide describes two main shutdown modes:

- **Graceful**: enqueue an “end” control frame so pending output can finish (use when the bot should say goodbye).
- **Immediate**: cancel the task to force fast shutdown and discard pending frames (use on disconnects or fatal errors).

If you need to end the task from inside the pipeline (e.g., from a tool/function handler), use the task-level termination signal and push it upstream so the pipeline source can terminate the whole chain correctly.

## Idle detection

Docs mention built-in idle detection that can auto-cancel a task after a timeout to avoid leaked sessions.

## Gotcha

Custom processors must propagate frames. If a processor forgets to push frames onward, termination frames may never reach the end of the pipeline and shutdown can hang.
