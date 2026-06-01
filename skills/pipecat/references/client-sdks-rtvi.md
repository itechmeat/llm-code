# Client SDKs, RTVI messaging, and function calling

## Connection flow

A typical pattern in client SDKs:

1. `startBot(startParams)` — call your server endpoint to start a session and receive connection parameters.
2. `connect(connectParams)` — connect the chosen transport.
3. Or use `startBotAndConnect(startParams)` to do both.

## Messaging primitives

- **Client → server message**: fire-and-forget
- **Client → server request**: request/response with a timeout
- Event handlers for server messages and connection state

`1.2.0` note:

- RTVI adds first-class UI Agent Protocol messages. Expect client-to-server `ui-event`, `ui-snapshot`, and `ui-cancel-task`, plus server-to-client `ui-command` and `ui-task`.
- The RTVI protocol version moves to `1.3.0`. If your client/server pins protocol behavior, upgrade both ends together.
- Default UI command payloads now cover actions such as toast, navigate, scroll, highlight, focus, click, set input value, and select text.

`1.3.0` note:

- `UIWorker` (`pipecat.workers.ui`) observes the client's accessibility snapshots, routes client UI events to `@ui_event` handlers, drives UI commands such as scroll/highlight/click/input selection, and can answer screen-grounded questions.
- The UI worker protocol vocabulary changed from `task`/`agent` to `job`/`worker`: `ui-task` -> `ui-job-group`, `ui-cancel-task` -> `ui-cancel-job-group`, `task_id` -> `job_id`, `agents` -> `workers`, and React/JS APIs such as `cancelUITask` / `useUITasks` become `cancelUIJobGroup` / `useUIJobGroups`.
- Use `ReplyToolMixin`, `respond_to_job(..., tts_speak=True)`, and `ui_job_group(...)` when a voice agent delegates UI-grounded work and wants cancellable progress cards in the client.

## Context updates

Docs highlight a “send text” style call for appending user text to the conversation, with options like:

- Run immediately vs wait for normal turn-taking
- Whether to also produce an audio response

If you see older APIs that directly append context, treat them as deprecated and prefer the current “send text” approach.

## Function calling

End-to-end shape:

- LLM emits a function call request.
- Client registers a handler for a specific function name.
- Client sends a function-call result back to the bot.

Docs mention message evolution where “in-progress” and “stopped” events replace older message types; expect version differences across SDKs.

## Useful events

The docs mention callbacks/events such as:

- Bot ready/connected/disconnected
- User transcript updates
- Bot output (including whether it was spoken)
- Function call started/in-progress/stopped
- Media/device events and audio level events

When using the UI Agent Protocol additions, expect a parallel event path for UI state snapshots and task cancellation in addition to the older transcript/function-call events.
