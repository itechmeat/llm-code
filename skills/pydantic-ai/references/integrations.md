# Integrations Reference

Pydantic AI integrates with MCP, Logfire, A2A, and durable execution platforms.

## Vercel AI SDK Compatibility (v1.52.0)

Compatibility with Vercel AI SDK v5 is restored by passing the SDK version parameter in requests.

### Vercel tool approvals (v1.62.0)

Vercel AI adapter integrates tool approval flows, enabling safer gated execution patterns in UI-driven chats.

---

## MCP (Model Context Protocol)

Connect agents to external tools and services via standardized protocol.

Recent migration note (`1.97.0+`): prefer `MCPToolset` for new client integrations. `FastMCPToolset` and the older `MCPServer*` wrappers are now legacy migration surfaces.

Dependency note (`v2.19.0`): the `fastmcp` optional group now constrains `fastmcp<4`; pin your own `fastmcp` version accordingly if you install it separately.

`MCPToolset` clients can pass `prefer_tasks=False` (v2.22.0) to skip optional MCP background-task negotiation for servers that don't support it.

Patch note (`1.103.0+`): maintained `McpServer` integrations can call `list_prompts` and `get_prompt`. Use this for legacy MCP server wrappers that expose prompt catalogs, but keep new client code on `MCPToolset` unless a migration constraint requires direct `McpServer` access.

### Installation

```bash
pip install "pydantic-ai-slim[mcp]"
```

### Legacy MCP server wrappers

| Type                      | Transport             | Use Case         |
| ------------------------- | --------------------- | ---------------- |
| `MCPServerStreamableHTTP` | HTTP                  | Remote servers   |
| `MCPServerSSE`            | HTTP SSE (deprecated) | Legacy servers   |
| `MCPServerStdio`          | stdio                 | Local subprocess |

Use these only when you are maintaining older code. For new code, start with `MCPToolset`.

### Recommended client API (`MCPToolset`)

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

remote = MCPToolset(url='http://localhost:8000/mcp')
local = MCPToolset(command='python', args=['mcp_server.py'], timeout=10)

agent = Agent('openai:gpt-4o', toolsets=[remote, local])
```

### HTTP Client (Streamable)

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

server = MCPServerStreamableHTTP('http://localhost:8000/mcp')
agent = Agent('openai:gpt-4o', toolsets=[server])

async def main():
    async with agent:  # Opens MCP connection
        result = await agent.run('What is 7 + 5?')
```

### Stdio Client (Subprocess)

```python
from pydantic_ai.mcp import MCPServerStdio

server = MCPServerStdio(
    'python',
    args=['mcp_server.py'],
    timeout=10,
)
agent = Agent('openai:gpt-4o', toolsets=[server])
```

### Load from Config

```json
{
  "mcpServers": {
    "calculator": {
      "url": "http://localhost:8000/mcp"
    },
    "weather": {
      "command": "python",
      "args": ["weather_server.py"]
    }
  }
}
```

```python
from pydantic_ai.mcp import load_mcp_servers

servers = load_mcp_servers('mcp_config.json')
agent = Agent('openai:gpt-4o', toolsets=servers)
```

### Tool Prefixes (Avoid Conflicts)

```python
weather = MCPToolset(url='http://localhost:3001/mcp', tool_prefix='weather')
calc = MCPToolset(url='http://localhost:3002/mcp', tool_prefix='calc')

# Tools: weather_get_data, calc_get_data
agent = Agent('openai:gpt-4o', toolsets=[weather, calc])
```

### MCP Resources

```python
async with server:
    resources = await server.list_resources()
    content = await server.read_resource('resource://data.txt')
```

### MCP Sampling

Allow MCP server to make LLM calls through client:

```python
server = MCPServerStdio('python', args=['server.py'])
agent = Agent('openai:gpt-4o', toolsets=[server])

agent.set_mcp_sampling_model()  # Enable sampling
```

---

## Building MCP Servers

### With FastMCP + Pydantic AI Agent

```python
from mcp.server.fastmcp import FastMCP
from pydantic_ai import Agent

server = FastMCP('My AI Server')
agent = Agent('anthropic:claude-haiku-4-5', system_prompt='Reply in rhyme')

@server.tool()
async def poet(theme: str) -> str:
    """Generate a poem about the theme."""
    result = await agent.run(f'Write a poem about {theme}')
    return result.output

if __name__ == '__main__':
    server.run()  # stdio transport by default
```

### With MCP Sampling

Server uses client's LLM via `MCPSamplingModel`:

```python
from mcp.server.fastmcp import Context, FastMCP
from pydantic_ai import Agent
from pydantic_ai.models.mcp_sampling import MCPSamplingModel

server = FastMCP('Sampling Server')
agent = Agent(system_prompt='Reply in rhyme')

@server.tool()
async def poet(ctx: Context, theme: str) -> str:
    """Generate poem using client's LLM."""
    result = await agent.run(
        f'Write poem about {theme}',
        model=MCPSamplingModel(session=ctx.session),
    )
    return result.output
```

---

## Background MCP work (`1.101.0+`)

- MCP integrations can now run background tasks. Use this when a server needs to continue work after the main model turn has already returned.
- Pair background work with explicit lifecycle/logging so queued tasks are observable instead of silently detached.

---

## Logfire Integration

Built-in observability for agent runs.

### OTel alignment (v1.60.0)

Instrumentation version 4 aligns with OTel GenAI semantic conventions, including multimodal request traces.

### Instrumentation settings (v2.13.0/v2.17.0)

- `include_model_request_parameters`: set to `False` on your instrumentation settings to omit the (often large and repetitive) `model_request_parameters` span attribute when you don't need it.
- Per-message OTel serialization is now cached internally, avoiding the `O(n^2)` cost of re-serializing the full message history on every span in a long-running conversation — no configuration needed, it applies automatically.

```python
from pydantic_ai.models.instrumented import InstrumentationSettings

settings = InstrumentationSettings(include_model_request_parameters=False)
agent = Agent('openai:gpt-4o', instrument=settings)
```

### Setup

```bash
pip install pydantic-ai  # Logfire included
logfire configure
```

```python
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()
```

### View in Dashboard

- Agent runs with timing
- Tool calls and results
- Token usage
- Model responses

---

## Agent-to-Agent (A2A)

Protocol for agents to communicate with each other.

```bash
pip install "pydantic-ai-slim[a2a]"
```

```python
from pydantic_ai.a2a import A2AServer, A2AClient

# Server side
server = A2AServer(agent)

# Client side
client = A2AClient('http://agent-server.com')
result = await client.run('Query for remote agent')
```

---

## Durable Execution

Persist agent state across failures/restarts.

### Capability-based durability (v2.14.0+)

Durability now attaches to a regular `Agent` as a capability — `TemporalDurability`, `DBOSDurability`, or `PrefectDurability` — instead of wrapping the agent in a dedicated class:

```python
agent = Agent(
    'openai:gpt-5.6',
    name='geography',
    capabilities=[TemporalDurability()],  # or DBOSDurability() / PrefectDurability()
)
```

This replaces the older wrapper-agent pattern (`TemporalAgent`, `DBOSAgent`, `PrefectAgent`), which is deprecated and scheduled for removal in v3. Workflows built on the wrapper classes keep replaying correctly after switching to the capability, so there is no need to drain or re-version them first. The capability form composes with other capabilities (hooks, ordering, thinking, etc.) using the same rules as the rest of the harness, whereas the wrapper classes could only stand alone. All three integrations also support `DynamicCapability` toolsets and round-trip tool control-flow exceptions (`ModelRetry`, approvals, deferrals) across the durability boundary.

### Installation

```bash
pip install "pydantic-ai-slim[temporal]"
pip install "pydantic-ai-slim[dbos]"
pip install "pydantic-ai-slim[prefect]"
```

---

## Temporal (Durable Execution)

### Overview

Temporal provides durable execution via workflows (deterministic) and activities (non-deterministic I/O).

```text
            +---------------------+
            |   Temporal Server   |      (Stores workflow state,
            +---------------------+       schedules activities)
                     ^
                     |
+------------------------------------------------------+
|                      Worker                          |
|   +----------------------------------------------+   |
|   |              Workflow Code                   |   |
|   |       (Agent Run Loop - deterministic)       |   |
|   +----------------------------------------------+   |
|          |          |                |               |
|   +-----------+ +------------+ +-------------+       |
|   | Activity  | | Activity   | |  Activity   |       |
|   | (Tool)    | | (MCP Tool) | | (Model API) |       |
|   +-----------+ +------------+ +-------------+       |
+------------------------------------------------------+
```

### Installation

```bash
pip install "pydantic-ai[temporal]"
# Start local Temporal server
brew install temporal
temporal server start-dev
```

### TemporalDurability

Attach the capability to a regular agent, then run it from inside a Temporal workflow:

```python
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import (
    PydanticAIPlugin,
    PydanticAIWorkflow,
    TemporalDurability,
)

# Define agent (name required for Temporal)
agent = Agent(
    'openai:gpt-5.6',
    instructions="You're an expert in geography.",
    name='geography',  # Required for stable activity names
    capabilities=[TemporalDurability()],
)

# Define workflow
@workflow.defn
class GeographyWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await agent.run(prompt)
        return result.output

# Run workflow
async def main():
    client = await Client.connect(
        'localhost:7233',
        plugins=[PydanticAIPlugin()],
    )

    async with Worker(
        client,
        task_queue='geography',
        workflows=[GeographyWorkflow],
    ):
        output = await client.execute_workflow(
            GeographyWorkflow.run,
            args=['What is the capital of Mexico?'],
            id='geography-workflow-1',
            task_queue='geography',
        )
        print(output)  # Mexico City
```

### Key Requirements

| Requirement       | Description                                            |
| ----------------- | ------------------------------------------------------ |
| Agent `name`      | Required for stable activity names                     |
| Toolset `id`      | Required for dynamic toolsets                          |
| Serializable deps | Dependencies must be Pydantic-serializable             |
| No streaming      | `run_stream()` not supported, use event_stream_handler |

### Model Selection at Runtime

```python
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.models.anthropic import AnthropicModel

# Pre-register models on the capability
fast_model = AnthropicModel('claude-sonnet-4-5')

agent = Agent(
    OpenAIResponsesModel('gpt-5.6'),
    name='geography',
    capabilities=[
        TemporalDurability(
            models={'fast': fast_model, 'reasoning': reasoning_model},
            provider_factory=my_provider_factory,  # Optional for dynamic config
        )
    ],
)

# In workflow: select by name or instance
result = await agent.run(prompt, model='fast')
result = await agent.run(prompt, model=fast_model)
result = await agent.run(prompt, model='openai:gpt-4.1-mini')  # model string
```

### Activity Configuration

```python
from temporalio.common import RetryPolicy
from temporalio.workflow import ActivityConfig

agent = Agent(
    'openai:gpt-5.6',
    name='geography',
    capabilities=[
        TemporalDurability(
            activity_config=ActivityConfig(start_to_close_timeout=120),  # Base config
            model_activity_config=ActivityConfig(start_to_close_timeout=300),  # Model requests
            event_stream_handler_activity_config=ActivityConfig(...),  # Streaming handlers
            toolset_activity_config={'my_toolset': ActivityConfig(...)},  # Per toolset
            tool_activity_config={
                ('my_toolset', 'fast_tool'): False,  # Disable activity for sync tools
            },
        )
    ],
)
```

Unknown `ActivityConfig` keys are now rejected instead of silently ignored, and activities heartbeat during tool, MCP, dynamic-toolset, and event-stream work so long-running steps aren't mistaken for a stuck worker.

### RunContext in Activities

Limited fields available in activities:

- ✅ `deps`, `run_id`, `metadata`, `retries`, `tool_call_id`, `tool_name`
- ✅ `tool_call_approved`, `retry`, `max_retries`, `run_step`, `usage`, `partial_output`
- ❌ `model`, `prompt`, `messages`, `tracer` — raise error

Custom serialization:

```python
from pydantic_ai.durable_exec.temporal import TemporalRunContext

class MyRunContext(TemporalRunContext):
    @classmethod
    def serialize_run_context(cls, ctx): ...
    @classmethod
    def deserialize_run_context(cls, data): ...

agent = Agent(
    'openai:gpt-5.6',
    name='geography',
    capabilities=[TemporalDurability(run_context_type=MyRunContext)],
)
```

### Logfire Integration

```python
from pydantic_ai.durable_exec.temporal import LogfirePlugin, PydanticAIPlugin

client = await Client.connect(
    'localhost:7233',
    plugins=[PydanticAIPlugin(), LogfirePlugin()],
)
```

`LogfirePlugin` now preserves the host process's existing Logfire configuration instead of overriding it inside the workflow sandbox.

### Prohibitions

- ❌ Streaming (`run_stream()`, `run_stream_events()`, `iter()`)
- ❌ HTTP retries (disable in provider: `max_retries=0`)
- ❌ Changing agent name/toolset id after deployment
- ❌ Non-serializable dependencies
- ❌ Non-async tools outside activities
- ❌ `TemporalAgent` wrapper for new code — deprecated, removed in v3, migrate to `TemporalDurability`

---

## DBOS (Durable Execution)

Attach `DBOSDurability` to a regular agent, then run it inside your own `@DBOS.workflow`:

```python
from dbos import DBOS, DBOSConfig
from pydantic_ai import Agent
from pydantic_ai.durable_exec.dbos import DBOSDurability

dbos_config: DBOSConfig = {
    'name': 'pydantic_dbos_agent',
    'system_database_url': 'sqlite:///dbostest.sqlite',
}
DBOS(config=dbos_config)

agent = Agent(
    'openai:gpt-5.6',
    instructions="You're an expert in geography.",
    name='geography',
    capabilities=[DBOSDurability()],
)

@DBOS.workflow()
async def answer(question: str) -> str:
    result = await agent.run(question)
    return result.output
```

The older `DBOSAgent` wrapper is deprecated and will be removed in v3. New code should attach `DBOSDurability` to the capabilities list and wrap `agent.run()` in your own `@DBOS.workflow`, rather than relying on an automatic wrapper; `register_legacy_workflows` on `DBOSDurability` eases migrating existing `DBOSAgent` deployments.

---

## Prefect (Durable Execution)

Attach `PrefectDurability` to a regular agent, then call it from your own `@flow`:

```python
from prefect import flow
from pydantic_ai import Agent
from pydantic_ai.durable_exec.prefect import PrefectDurability

agent = Agent(
    'openai:gpt-5.6',
    instructions="You're an expert in geography.",
    name='geography',
    capabilities=[PrefectDurability()],
)

@flow
async def answer(question: str) -> str:
    result = await agent.run(question)
    return result.output
```

Durability only activates when `agent.run()` executes inside a Prefect flow context. The older `PrefectAgent` wrapper (which applied the `@flow` automatically) is deprecated and will be removed in v3 — migrate by attaching `PrefectDurability()` to the agent's capabilities and adding your own `@flow` around the call site.

---

## Building MCP Servers

### With FastMCP

```python
from mcp.server.fastmcp import FastMCP

app = FastMCP('My Server')

@app.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == '__main__':
    app.run(transport='streamable-http')  # or 'stdio', 'sse'
```

### Expose Resources

```python
@app.resource('resource://data.txt', mime_type='text/plain')
async def get_data() -> str:
    return "Resource content"
```

### With Pydantic AI Agent

Use agents inside MCP servers:

```python
from mcp.server.fastmcp import FastMCP
from pydantic_ai import Agent

app = FastMCP('AI Server')
agent = Agent('openai:gpt-4o')

@app.tool()
async def ask_ai(question: str) -> str:
    """Ask AI a question."""
    result = await agent.run(question)
    return result.output
```
