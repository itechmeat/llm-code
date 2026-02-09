# Integrations Reference

Pydantic AI integrates with MCP, Logfire, A2A, and durable execution platforms.

## Vercel AI SDK Compatibility (v1.52.0)

Compatibility with Vercel AI SDK v5 is restored by passing the SDK version parameter in requests.

---

## MCP (Model Context Protocol)

Connect agents to external tools and services via standardized protocol.

### Installation

```bash
pip install "pydantic-ai-slim[mcp]"
```

### MCP Server Types

| Type                      | Transport             | Use Case         |
| ------------------------- | --------------------- | ---------------- |
| `MCPServerStreamableHTTP` | HTTP                  | Remote servers   |
| `MCPServerSSE`            | HTTP SSE (deprecated) | Legacy servers   |
| `MCPServerStdio`          | stdio                 | Local subprocess |

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
weather = MCPServerSSE('http://localhost:3001/sse', tool_prefix='weather')
calc = MCPServerSSE('http://localhost:3002/sse', tool_prefix='calc')

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

## FastMCP Toolset

Alternative MCP client using FastMCP library.

```bash
pip install "pydantic-ai-slim[fastmcp]"
```

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import FastMCPToolset

toolset = FastMCPToolset('http://localhost:8000/mcp')
agent = Agent('openai:gpt-4o', toolsets=[toolset])
```

---

## Logfire Integration

Built-in observability for agent runs.

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

### Temporal

```bash
pip install "pydantic-ai-slim[temporal]"
```

### DBOS

```bash
pip install "pydantic-ai-slim[dbos]"
```

### Prefect

```bash
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

### TemporalAgent

Wrap any agent for durable execution:

```python
import uuid
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import (
    PydanticAIPlugin,
    PydanticAIWorkflow,
    TemporalAgent,
)

# Define agent (name required for Temporal!)
agent = Agent(
    'openai:gpt-4o',
    instructions="You're an expert in geography.",
    name='geography',  # Required for stable activity names
)

# Wrap for durable execution
temporal_agent = TemporalAgent(agent)

# Define workflow
@workflow.defn
class GeographyWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [temporal_agent]

    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await temporal_agent.run(prompt)
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
            id=f'geography-{uuid.uuid4()}',
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

# Pre-register models for TemporalAgent
default_model = OpenAIResponsesModel('gpt-4o')
fast_model = AnthropicModel('claude-sonnet-4-5')

temporal_agent = TemporalAgent(
    agent,
    models={
        'fast': fast_model,
        'reasoning': reasoning_model,
    },
    provider_factory=my_provider_factory,  # Optional for dynamic config
)

# In workflow: select by name or instance
result = await temporal_agent.run(prompt, model='fast')
result = await temporal_agent.run(prompt, model=fast_model)
result = await temporal_agent.run(prompt, model='openai:gpt-4.1-mini')  # model string
```

### Activity Configuration

```python
from temporalio.common import RetryPolicy
from temporalio.workflow import ActivityConfig

temporal_agent = TemporalAgent(
    agent,
    activity_config=ActivityConfig(start_to_close_timeout=120),  # Base config
    model_activity_config=ActivityConfig(start_to_close_timeout=300),  # Model requests
    toolset_activity_config={'my_toolset': ActivityConfig(...)},  # Per toolset
    tool_activity_config={
        ('my_toolset', 'fast_tool'): False,  # Disable activity for sync tools
    },
)
```

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

temporal_agent = TemporalAgent(agent, run_context_type=MyRunContext)
```

### Logfire Integration

```python
from pydantic_ai.durable_exec.temporal import LogfirePlugin, PydanticAIPlugin

client = await Client.connect(
    'localhost:7233',
    plugins=[PydanticAIPlugin(), LogfirePlugin()],
)
```

### Prohibitions

- ❌ Streaming (`run_stream()`, `run_stream_events()`, `iter()`)
- ❌ HTTP retries (disable in provider: `max_retries=0`)
- ❌ Changing agent name/toolset id after deployment
- ❌ Non-serializable dependencies
- ❌ Non-async tools outside activities

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
