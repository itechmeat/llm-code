# Function calling (server-side)

This page focuses on function calling inside the server pipeline (LLM service + context aggregators).

## Where it fits in the pipeline

Typical placement:

- User text enters context aggregation.
- LLM decides to call a function/tool.
- Your handler runs and returns results.
- LLM incorporates the result into the response which continues to TTS/output.
- Context aggregators store calls + results in history.

## Registering function handlers

Docs describe registering a named function handler on the LLM service.

Behavioral knob:

- `cancel_on_interruption`: cancel the function call if the user interrupts mid-flight (docs say default enabled).

## FunctionCallParams: what you get

Docs show a params object with:

- function name and call/tool id
- parsed arguments from the LLM
- access to the current LLM context (conversation history)
- a reference to the LLM service
- a `result_callback` used to return a structured result

## Returning results

- Your handler should return the final result via `result_callback(result)`.
- Treat required configuration (API keys, endpoints) as mandatory and fail fast if missing.

## Advanced control: chaining calls

Docs mention result properties such as:

- `run_llm`: if set to false, you can prevent the LLM from running immediately after a tool result (useful for back-to-back tool calls).
- `on_context_updated`: callback that runs after the function result has been added to the context.

If you skip LLM execution, you must explicitly trigger the next step when appropriate (otherwise the conversation may stall).

## Practical checklist

- Keep handlers idempotent and cancel-safe.
- Decide whether user interruptions should cancel long-running tools.
- Log tool call ids for tracing and debugging.
