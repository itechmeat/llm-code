# Reference (Agent CLI, Events)

## Agent CLI (LiveKit Cloud)

Use the Agent CLI when you need to create/build/deploy and operate LiveKit Cloud agents from the terminal.

### Baseline

- Commands are prefixed with `lk agent ...`.
- The CLI typically uses the current working directory; you can pass a directory path as the final argument to target another folder.
- If a `livekit.toml` exists, it is used as the agent/project configuration. Without it, many commands require `--id` to target an existing agent.

### Common commands (operator view)

- `create`: create a new agent (can generate a `Dockerfile` if missing).
- `deploy`: build + deploy a new version (expects `livekit.toml` + `Dockerfile` in the working dir).
- `status`: inspect agent status/metadata.
- `update` / `update-secrets`: update configuration and/or secrets (typically restarts servers without interrupting active sessions).
- `restart`: restart server pool (typically does not interrupt active sessions).
- `logs` / `tail`: inspect deployment/build logs (log type commonly `deploy` or `build`).
- `versions` + `rollback`: list versions and roll back to a specific version.
- `list`: list agents in the current project.
- `config`: generate a `livekit.toml` for an existing agent.
- `dockerfile`: generate `Dockerfile` and `.dockerignore`.
- `delete` / `destroy`: delete an agent.

### Flags you’ll use often

- `--id <AGENT_ID>`: target an agent when `livekit.toml` is not present.
- `--region <REGION>`: choose deployment region (create).
- `--secrets KEY=VALUE`: inline secrets (can be repeated; typically overrides file-based secrets).
- `--secrets-file <PATH>`: secrets file with `KEY=VALUE` pairs.
- `--secret-mount <PATH>`: mount a secret file into the container.
- `--overwrite`: overwrite when generating files or updating secrets.
- `--silent`: skip interactive confirmations.
- `--log-type <deploy|build>`: select log stream.

### Operational notes

- “Sleeping/Waking” states often indicate scale-to-zero behavior; plan for cold-starts.
- Keep the LiveKit CLI updated; older versions may not support Agent operations.

## Events (AgentSession)

Use events to observe transcription, tool calls, state changes, metrics, and failures at runtime.

### Subscribe

- Subscribe on the `AgentSession` event emitter.
- Track agent state via the `agent_state_changed` event (agent states commonly include: initializing, listening, thinking, speaking).

### High-signal events to wire first

- `user_input_transcribed`: user transcript updates (watch `is_final`).
- `conversation_item_added`: anything appended to the conversation (useful for debugging content flow).
- `function_tools_executed`: tool calls + tool outputs (pairs are often easiest to log together).
- `speech_created`: when agent speech is created (and what triggered it: e.g., “say”, “generate_reply”, “tool_response”).
- `metrics_collected`: telemetry (STT/LLM/TTS/VAD/end-of-utterance).
- `agent_state_changed` and `user_state_changed`: state machine visibility; “away” timeouts may be configurable.
- `error`: provider/model errors; look for a “recoverable” signal to decide whether to retry, fail fast, or inform the user.
- `close`: terminal event; may include an error when a session ends unexpectedly.

### Operational guidance

- Always log: event name, timestamps, job/session identifiers, and whether errors are recoverable.
- Use `metrics_collected` to correlate latency/quality regressions with provider changes.
