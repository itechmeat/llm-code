# Hook system

PicoClaw supports a hook system for intercepting and observing agent lifecycle events. Two mounting modes:

1. **In-process hooks** — Go code compiled into the binary
2. **Out-of-process hooks** — external processes via JSON-RPC over stdio

## Supported hook types

| Type             | Interface         | Stage                        | Can modify data        |
| ---------------- | ----------------- | ---------------------------- | ---------------------- |
| Observer         | `EventObserver`   | EventBus broadcast           | No                     |
| LLM interceptor  | `LLMInterceptor`  | `before_llm` / `after_llm`   | Yes                    |
| Tool interceptor | `ToolInterceptor` | `before_tool` / `after_tool` | Yes                    |
| Tool approver    | `ToolApprover`    | `approve_tool`               | No, returns allow/deny |

Synchronous hook points: `before_llm`, `after_llm`, `before_tool`, `after_tool`, `approve_tool`. Everything else is exposed as read-only events.

## Execution order

`HookManager` priority: in-process first → process hooks second → lower `priority` first → name order as tie-breaker.

## Timeouts

Global defaults under `hooks.defaults`:

- `observer_timeout_ms`
- `interceptor_timeout_ms`
- `approval_timeout_ms`

Per-process-hook `timeout_ms` is not currently supported.

## Config example (out-of-process)

```json
{
  "hooks": {
    "enabled": true,
    "processes": {
      "py_review_gate": {
        "enabled": true,
        "priority": 100,
        "transport": "stdio",
        "command": ["python3", "/tmp/review_gate.py"],
        "observe": ["tool_exec_start", "tool_exec_end", "tool_exec_skipped"],
        "intercept": ["before_tool", "approve_tool"],
        "env": {
          "PICOCLAW_HOOK_LOG_FILE": "/tmp/picoclaw-hook-review-gate.log"
        }
      }
    }
  }
}
```

## Common use cases

- **Logging/auditing**: observe all tool executions without modifying behavior
- **Tool approval gate**: require explicit approval for dangerous tools before execution
- **LLM request/response filtering**: modify prompts or responses in-flight
- **Cost tracking**: intercept LLM calls to log token usage

## Direct tool responses (v0.2.6)

- `before_tool` hooks can now return `action: "respond"` with a final tool result payload.
- Use this for plugin-style tools implemented completely inside the hook process, result caching, or controlled mock responses during testing.
- `respond` skips the actual tool execution path and does not trigger `after_tool`, so treat it as a terminal decision for that tool call.
- The upstream JSON-RPC hook protocol documents the response envelope fields (`for_llm`, `for_user`, `silent`, `is_error`) explicitly; keep your hook output aligned with that structure.
