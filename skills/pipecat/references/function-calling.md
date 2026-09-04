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

`1.2.0` notes:

- `LLMContextAggregatorPair(..., add_tool_change_messages=True)` appends a developer-role message whenever the available standard tools change mid-conversation. Use it when tool availability is dynamic and the model tends to hallucinate removed or re-added tools.
- `tool_resources` has been broadened to `app_resources`. New code should read `params.app_resources`, `PipelineTask.app_resources`, and `self.pipeline_task.app_resources`; the old `tool_resources` aliases still work but are deprecated.
- Async tool continuation after interruption is restored/expanded across more realtime services, but streamed intermediate results are still not universally supported. Re-test `cancel_on_interruption=False` separately for each realtime provider you depend on.

## Advanced control: chaining calls

Docs mention result properties such as:

- `run_llm`: if set to false, you can prevent the LLM from running immediately after a tool result (useful for back-to-back tool calls).
- `on_context_updated`: callback that runs after the function result has been added to the context.

If you skip LLM execution, you must explicitly trigger the next step when appropriate (otherwise the conversation may stall).

## Pipecat Flows: NO_RESPONSE (1.6.0)

Pipecat Flows (integrated into the main package since `1.5.0`) adds `NO_RESPONSE`: a consolidated function can return `(result, NO_RESPONSE)` to finish the function call without transitioning to a new node and without running the LLM. Use it when a function should quietly update state and let the next user utterance (or another explicit trigger) produce the next response, instead of forcing an immediate LLM turn. The upstream `multi_worker_handoff` Flows example switched to `NO_RESPONSE` for exactly this reason: without it, the newly-deactivated worker was repeating the assistant's reply after handing control back to the router.

## Eval scenarios: `absent: true` (1.6.0)

Eval scenario expectations gain `absent: true`: the expectation passes only when no event of the given type arrives within the `within_ms` budget, and fails as soon as one does. Use it for duplicate-output regressions, e.g. asserting a bot responds exactly once after a multi-worker handoff.

## MCP tools (1.8.0)

- `MCPClient.tools()`: `LLMContext(tools=await mcp.tools())` is all you need — connecting, tool registration, and closing the connection at pipeline end are automatic.
- `MCPClient(tools_arguments=...)` injects extra arguments into every call of a tool, hidden from the schema the model sees and overriding anything the model supplies:

  ```python
  mcp = MCPClient(
      server_params=...,
      tools_arguments={"search": {"mode": "realtime"}},
  )
  ```

  The model only ever sees `search(query=...)`, while every call reaches the server as `search(query=..., mode="realtime")`. Use it for arguments the model shouldn't choose — a fixed search mode, an account id, a caller-supplied filter.

- `KeenableWebSearch` (`pipecat.services.keenable.search`, install with the `keenable` extra) gives voice agents live web search and page reading via a hosted MCP server. It exposes `search_web_pages` (with optional site and date-range filters) and `fetch_page_content`; pass `await search.tools()` to your `LLMContext` and the connection is released automatically when the pipeline ends. Works keyless (`pro` mode); pass `api_key=` for higher rate limits and `mode="realtime"`.

## Migration notes for 1.0.0

- Single-argument function call support was removed; tools must expose named parameters.
- Prefer the async flow above instead of bespoke background-task side channels.
- If you relied on older `handle_function_call*` RTVI/processor helpers, move to the current processor API and universal context flow.

## Practical checklist

- Keep handlers idempotent and cancel-safe.
- Set per-function `timeout_secs` for slow or third-party tools instead of relaxing the global timeout for everything.
- Decide whether user interruptions should cancel long-running tools.
- Log tool call ids for tracing and debugging.
- If tools appear/disappear dynamically, enable `add_tool_change_messages` instead of relying on prompt-only reminders.
