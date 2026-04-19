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
- `timeout_secs`: override the global function-call timeout per tool when a specific integration needs a tighter or looser budget.
- `group_parallel_tools`: when left at the default `True`, tool calls from the same LLM response batch share one group and Pipecat re-runs the LLM once after the last grouped tool completes.

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

For async handlers that continue after interruption (`cancel_on_interruption=False`), Pipecat can stream intermediate updates back into the conversation:

- call `result_callback(..., properties=FunctionCallResultProperties(is_final=False))` for partial progress;
- call it once more with the final result (`is_final=True`, the default) when the work is complete.

When you allow a function to outlive the current turn, Pipecat injects the eventual result back as a `developer` message and triggers another LLM inference.

## Advanced control: chaining calls

Docs mention result properties such as:

- `run_llm`: if set to false, you can prevent the LLM from running immediately after a tool result (useful for back-to-back tool calls).
- `on_context_updated`: callback that runs after the function result has been added to the context.

If you skip LLM execution, you must explicitly trigger the next step when appropriate (otherwise the conversation may stall).

## Migration notes for 1.0.0

- Single-argument function call support was removed; tools must expose named parameters.
- Prefer the async flow above instead of bespoke background-task side channels.
- If you relied on older `handle_function_call*` RTVI/processor helpers, move to the current processor API and universal context flow.

## Practical checklist

- Keep handlers idempotent and cancel-safe.
- Set per-function `timeout_secs` for slow or third-party tools instead of relaxing the global timeout for everything.
- Decide whether user interruptions should cancel long-running tools.
- Log tool call ids for tracing and debugging.
