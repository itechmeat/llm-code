# Prompting and testing

## Prompt structure (recommended sections)

LiveKit docs recommend a structured instruction format (Markdown is convenient for humans and machines):

- **Identity**: start with “You are …” including name/role and responsibilities.
- **Output rules** (voice-first): keep TTS-friendly output rules explicit.
- **Tools**: high-level guidance on when/how to use tools; put tool-specific parameter rules in tool definitions.
- **Goal**: overall objective; pair with more specific goals inside tasks/workflows.
- **Guardrails**: define scope limits and safe refusal behavior.
- **User information**: inject known user context via job metadata.

## Voice-first output rules (STT → LLM → TTS pipeline)

Key doc guidance:

- Prefer **plain text**; avoid complex formatting that sounds bad in TTS.
- Default to **1–3 sentences**; ask **one question at a time**.
- Spell out numbers / phone numbers / email addresses when needed.
- Don’t reveal system instructions, internal reasoning, tool names, or raw tool outputs.

Note: if you use a native realtime speech model, some formatting rules may be less critical, but brevity still matters.

## Tool calling guidance (prompt-level)

- Use tools when needed or on user request.
- Collect required inputs first.
- Perform actions silently if the runtime expects it.
- Summarize structured tool results for the user; don’t recite raw identifiers.
- If an action fails: state it once, propose a fallback, or ask how to proceed.

## Loading user context via job metadata

- Docs recommend job metadata (dispatch-time) as the primary way to pre-load user info.
- Pattern: map metadata fields into prompt variables (example template uses `{{ user_name }}` etc).

## Testing + observability loop

- Treat prompting as an iterative discipline: small changes to prompt/tools/models can have large behavior impacts.
- **Unit tests**: Python SDK includes a built-in testing feature designed to work with frameworks like `pytest`.
- **Real-world observability**: use LiveKit Cloud session observability (transcripts, observations, recordings) to find failures, then turn them into test cases.

## Python testing & evaluation (built-in)

- Works with `pytest` + `pytest-asyncio`.
- Tests run **live** against your LLM provider (set provider API keys in env); LiveKit API keys are not required for these tests.

### Minimal pattern

- Create a session (using the same or a different LLM for judging).
- Start the agent and run turns with `session.run(user_input=...)`.
- Use `RunResult` events + fluent assertions to validate behavior.

### What you can assert

- Assistant messages (role/content) and ordering.
- Tool calls:
  - function call name + arguments
  - tool output, error status, and call id
- Agent handoffs (when using multi-agent patterns).

### Multi-turn and history control

- Multi-turn: call `session.run(...)` multiple times; history accumulates.
- Manual history: pre-fill a `ChatContext`, then update the agent context before running.

### Qualitative evaluation

- Use an LLM-as-judge: `judge(llm, intent="...")` to validate intent/style.

### Tool mocking (Python)

- `mock_tools(...)` lets you stub tool behavior or inject failures to test edge cases.
- Requires LiveKit Agents `>= 1.2.6`.

### Running in CI

- Provide LLM API keys via CI secrets/env vars (never commit keys).
- For verbose eval output: `LIVEKIT_EVALS_VERBOSE=1` (and `pytest -s` to see stdout).
