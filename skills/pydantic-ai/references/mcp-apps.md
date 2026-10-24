# MCP Apps

MCP Apps (`2.57.0`) extend MCP tool results with **resources** and **app** surfaces that frontends can render. A tool call can now return not just text, but content the AG-UI or Vercel AI frontend knows how to display.

## Reading MCP resources from a toolset

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset('my-server')
agent = Agent('openai:gpt-5', toolsets=[toolset])

@agent.tool
async def show_resource(ctx: RunContext, uri: str) -> str:
    result = await toolset.read_resource_contents(uri)
    return result
```

- `MCPToolset.read_resource_contents(uri)` (`2.57.0`) reads a resource exposed by the MCP server.
- `MCPToolset.call_tool_for_app(...)` (`2.57.0`) calls a tool that produces an app surface instead of plain text.

## Frontend forwarding

From `2.57.0`, MCP Apps tool results are forwarded to the AG-UI and Vercel AI frontends. The frontend receives the resource/app payload instead of a flattened string, so a UI can render the tool output natively.

For a custom frontend, the same payload is available on the run result - read it rather than stringifying it.

## Typed tool parts

`2.58.0` introduced `ToolKind`, typed tool parts that any module can emit. A tool that returns an MCP resource or an app surface declares its kind, and the framework (or the frontend adapter) routes it accordingly instead of guessing.

## Security

MCP Apps widen the blast radius of an MCP server: a tool result can now carry executable-looking UI payloads rather than plain text.

- Treat every MCP resource as untrusted content and sanitize it before rendering.
- The advisory `GHSA-5pfm-2g3g-gh85` (fixed in `2.58.0`) affected exactly this area: with server-side `message_history` and `manage_system_prompt='server'`, the Vercel AI and AG-UI adapters could execute an available tool with client-chosen arguments. See `references/security.md`.
- Tools that require approval are not executed through that path, but tools without approval are - mark side-effecting tools as approval-required.

## Combining with the rest of the stack

```python
agent = Agent(
    'openai:gpt-5',
    toolsets=[MCPToolset('apps-server')],
    deps_type=MyDeps,
)
```

MCP Apps compose with `TypeSafeModel` output, with structured results, and with the UI adapters - the app surface survives the same pipeline as plain tool output.
