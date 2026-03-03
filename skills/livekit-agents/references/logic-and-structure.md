# Logic and structure

LiveKit Agents provides primitives to keep complex realtime agents maintainable: sessions (orchestration), tasks (typed sub-goals), workflows (multi-step / multi-agent patterns), tools (external actions), and pipeline nodes/hooks (customization points).

## Components (mental model)

- **Agent session**: orchestrates input collection, pipeline execution, and output delivery.
- **Tasks / task groups**: focused units that temporarily take control to achieve a goal and return typed results.
- **Workflows**: repeatable patterns using agents, handoffs, and tasks (useful for complex routing / phases).
- **Tools**: functions the LLM can call for side effects or data.
- **Pipeline nodes & hooks**: override/customize STT/LLM/TTS behavior and lifecycle moments.
- **Turn detection & interruptions**: natural conversation timing, or manual turn control.
- **Agents & handoffs**: multiple specialized agents and controlled transfers.
- **External data & RAG**: load initial context and fetch external knowledge safely.

## Agent sessions (how to think about `AgentSession`)

### What it does

- `AgentSession` is the main orchestrator: collects user input, runs the voice pipeline, invokes the LLM, sends output, and emits events for control/observability.

### Lifecycle (states)

- Initializing → Listening → Thinking → Speaking → Closing.
- Close behavior includes draining speech (if requested), committing any remaining transcripts, and closing I/O.

### I/O configuration (Room options)

- Input toggles: text/audio/video input.
  - Video input is commonly disabled by default.
- Output toggles: audio output + text/transcription output.
- You can override default text input behavior (default is “interrupt and respond”).

### Linked participant selection

- Default linked participant: the first participant to join a room.
- Ways to control:
  - set `participant_identity` in room options
  - swap at runtime via `RoomIO.set_participant()`
- Filters: `participant_kinds` (docs mention SIP + STANDARD by default).

### Events you can rely on

- `agent_state_changed`, `user_state_changed`
- `user_input_transcribed`
- `conversation_item_added`
- `close`

### Session-level toggles worth knowing

- `max_tool_steps`: cap consecutive tool calls per LLM turn (docs: default 3).
- `preemptive_generation`: start generation earlier (latency tradeoff).
- `user_away_timeout`: mark user away after silence (docs: default 15s; `None` disables).
- `tts_text_transforms`: filters like `filter_markdown` / `filter_emoji` (can disable).
- `video_sampler`: customize frame sampling strategy when video input is enabled.
- Cleanup behaviors: close-on-disconnect, optional delete-room-on-close (Python-only).

## Tasks and task groups

### Tasks (`AgentTask[T]`)

- A task is a focused, reusable unit that achieves one objective and returns a **typed** result.
- Runs inside an agent and takes control only until it completes.
- Define by subclassing `AgentTask[T]`:
  - start interaction in `on_enter()`
  - call `complete(result)` to finish
- Tasks can define their own tools via `@function_tool` (same tool-calling model as agents).
- Running model: instantiate/await the task inside an active agent context; awaiting yields the result.

### Result types

- Can be primitives (e.g., `bool`) or structured (docs show `dataclass` for complex results).

### Collecting multiple fields

- You can collect several pieces of information in any order in a single task.
- Use tool functions to record partial results and “check completion”; ask follow-ups for missing fields.

### TaskGroup (experimental)

- Ordered multi-step flows with built-in ability to **regress** (go back to earlier steps for corrections).
- All tasks share conversation context; by default, the group can summarize its context back into the main chat context.
- Key knobs:
  - `summarize_chat_ctx` (default true)
  - `return_exceptions` (default false; when true, errors are captured and sequence continues)
- Add tasks in order using factories (docs recommend lambdas so tasks can be re-initialized on revisit).
- Each task needs an `id` + `description` so the LLM can understand what to revisit.

## Workflows (multi-step / multi-agent)

### Choosing the right primitive

- Use **agents** for long-lived control (persona, reasoning behavior, tool access).
- Use **tasks** for discrete operations that must complete before proceeding (consent, verification, structured capture).
- Use **tools** for side effects and external integrations; make return values meaningful for downstream reasoning.
- Use **task groups** for ordered multi-step flows with “go back and correct” UX.

### Best practices

- Map conversation phases first (what is continuous vs discrete).
- Separate agents when you need different tool access or different constraints.
- Be intentional about context across handoffs (full continuity vs clean slate).
- Make handoffs explicit to the user (“I’m transferring you to…”), and preserve only relevant context.
- Build incrementally and backstop with tests/evals (especially for tool calls and handoff triggers).

## Tools (LLM tool use)

### Tool types

- **Function tools**: your code (Python decorator `@function_tool()`; Node uses `llm.tool(...)`).
- **Provider tools**: vendor-specific tools executed by the model provider (only work with that provider’s models).

### Definition best practices

- Be specific about:
  - when the tool should/shouldn’t be used
  - argument meanings
  - return value shape/semantics
- Tool args map from function parameters by name; type hints/schemas improve reliability.

### Return values and handoffs

- Tool returns are serialized to a string for the LLM.
- Return `None` to complete silently (no additional LLM reply required).
- Handoff patterns:
  - Python: return `(NewAgent(), tool_result)` or `NewAgent()`.
  - Node: return `llm.handoff({ agent, returns })`.

### `RunContext`

- Tools can accept a special `context: RunContext` with access to:
  - current session
  - function_call metadata
  - speech_handle
  - userdata

### Interruptions

- By default, tools can be interrupted when the user speaks.
- On interruption, the tool call is removed from history and the result is ignored.
- Pattern for external work:
  - wait on work via `speech_handle.wait_if_not_interrupted(...)`
  - if interrupted, cancel/cleanup and return
- If you perform irreversible side effects, call `run_ctx.disallow_interruptions()`.

### Dynamic / programmatic tools

- You can pass tools explicitly (shared tools across agents).
- You can replace tool sets at runtime:
  - Python: `agent.update_tools(...)` (replaces all tools)
  - Node: `agent.updateTools(...)`
- You can generate tools programmatically or from raw JSON schema (for external registries).

### Error handling

- Raise `ToolError` to return a structured error to the LLM with a recovery hint.

### Frontend RPC (tool forwarded to client)

- Tools can call frontend RPC for data only available on the client (e.g., geolocation).
- Use `perform_rpc(...)` / `performRpc(...)` and enforce timeouts.

### MCP servers (Python)

- Optional dependency: `livekit-agents[mcp]~=1.4`.
- Configure `mcp_servers=[mcp.MCPServerHTTP("https://...")]` on `AgentSession` or `Agent`.

### Provider tools

- Provider tools are mentioned for some providers (for example Gemini and xAI Grok Voice Agent API).

## Pipeline nodes & hooks (customization points)

### Lifecycle hooks

- `on_enter()`: agent becomes active in a session.
- `on_exit()`: before handing off to another agent.
- `on_user_turn_completed(turn_ctx, new_message)`: after user turn ends, before agent reply.
  - Use for RAG/context injection into `turn_ctx`.
  - Mutate `new_message.content` to sanitize or append context (persists to chat history).
  - Abort generation (e.g., push-to-talk / manual turn control) by raising `StopResponse`.

### Node override pattern

- Override node methods in your `Agent` subclass.
- Call `Agent.default.<node>(...)` to keep default behavior and wrap with pre/post transforms.

### Common pipeline nodes

- `stt_node(...)`: audio → transcript events (optionally normalize audio/text).
- `llm_node(...)`: chat context + tools → streamed model output.
- `tts_node(...)`: text → audio frames (filters, pronunciation, processors).
- `transcription_node(...)`: post-process transcript deltas.

### Realtime model nodes

- `realtime_audio_output_node(...)`: modify realtime model audio output before publishing (for example volume).
- If you need `on_user_turn_completed` with a realtime model, ensure turn detection is handled by your agent (not only by the model).

## Agents & handoffs (multi-agent control)

### When to split into multiple agents

- Different roles/personas.
- Different permissions (e.g., only one agent can call payment APIs).
- Model specialization (light triage → heavier specialist).
- Different constraints per phase.

### Active agent

- The active agent controls the session.
- You can switch explicitly (docs: `session.update_agent(...)` / `session.updateAgent(...)`).

### Handoffs

- A handoff transfers control from one agent to another.
- Common pattern: return a new agent from a tool call so the LLM can decide when to transfer.
- On handoff, an `AgentHandoff` item is added to chat context (old/new agent ids).
- Full conversation history remains available via `session.history`.

### Context preservation (`chat_ctx`)

- By default, a new agent/task starts with a **fresh** conversation history for its LLM prompt.
- Pass `chat_ctx` explicitly when you want continuity.
- You can also construct a new `ChatContext` from business logic (not always “everything”).

### Session state (`userdata`)

- Store custom per-session state in `session.userdata`.
- Recommended: typed structure (Python `dataclass`, TypeScript interface).
- Accessible from tools via `RunContext` and across handoffs.

### Overriding plugins per agent/task

- You can override STT/LLM/TTS/etc per agent or task by passing plugin instances in their constructors.
- Useful for changing voice/model for an escalation agent without rebuilding the whole session.

## External data & RAG

### Injecting initial context

- Sessions start with an empty chat context by default.
- Load user/task-specific context before `session.start(...)` (commonly from job metadata).

### Load-time optimization tips (docs)

- Static data: load in `prewarm`.
- User-specific data: prefer job metadata, room metadata, or participant attributes.
- If you must call external APIs in the entrypoint, do it **before** `ctx.connect()` so the user doesn’t see an agent participant that isn’t ready.

### Tool calls vs turn hook retrieval

- Tools are best for precise, explicit actions (CRUD, payments, external systems).
- For STT→LLM→TTS pipelines, you can do retrieval in `on_user_turn_completed(...)`:
  - run your search/vector lookup on the user’s latest message
  - inject retrieved context into `turn_ctx` before the LLM generates the reply
- This can be faster than tool-call round trips, but quality depends on your retrieval function.

### User feedback during long operations

- If something takes > a few hundred ms or is a write action, proactively give brief status updates.
- Pattern (docs): schedule a short-delay “status update” speech; cancel it if the operation finishes quickly.
- Optional: use “thinking sounds” via `BackgroundAudioPlayer` while tools are running.
