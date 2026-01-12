---
name: pydantic-ai
description: "Pydantic AI agent framework for Python: type-safe agents, dependency injection, function tools, structured output, multi-model support (OpenAI, Anthropic, Gemini, Groq, Mistral), MCP client/server, A2A, Logfire, evals, graphs, UI streams (AG-UI, Vercel AI), thinking/reasoning, HTTP retries, Temporal durable execution. Keywords: Pydantic AI, pydantic-ai, agent framework, LLM agents, function tools, structured output, dependency injection, RunContext, MCP, MCPServerStdio, MCPServerStreamableHTTP, A2A, Agent2Agent, Logfire, pydantic-graph, BaseNode, GraphRunContext, AG-UI, Vercel AI, TemporalAgent, thinking, WebSearchTool, CodeExecutionTool."
---

# Pydantic AI

Python agent framework for building production-grade GenAI applications with the "FastAPI feeling".

## Quick Navigation

| Topic        | Reference                                     |
| ------------ | --------------------------------------------- |
| Agents       | [agents.md](references/agents.md)             |
| Tools        | [tools.md](references/tools.md)               |
| Models       | [models.md](references/models.md)             |
| Evals        | [evals.md](references/evals.md)               |
| Integrations | [integrations.md](references/integrations.md) |
| Graphs       | [graphs.md](references/graphs.md)             |
| UI Streams   | [ui.md](references/ui.md)                     |

## When to Use

- Building AI agents with structured output
- Need type-safe, IDE-friendly agent development
- Require dependency injection for tools
- Multi-model support (OpenAI, Anthropic, Gemini, etc.)
- Production observability with Logfire
- Complex workflows with graphs

## Installation

**Requires Python 3.10+**

```bash
# Full install (all model dependencies)
pip install pydantic-ai

# With examples
pip install "pydantic-ai[examples]"
```

### Slim Install

Use `pydantic-ai-slim` for minimal dependencies:

```bash
# Single model
pip install "pydantic-ai-slim[openai]"

# Multiple models
pip install "pydantic-ai-slim[openai,anthropic,logfire]"
```

**Optional Groups:**

| Group         | Dependency                |
| ------------- | ------------------------- |
| `openai`      | OpenAI models             |
| `anthropic`   | Anthropic Claude          |
| `google`      | Google Gemini             |
| `groq`        | Groq models               |
| `mistral`     | Mistral models            |
| `bedrock`     | AWS Bedrock               |
| `vertexai`    | Google Vertex AI          |
| `cohere`      | Cohere models             |
| `huggingface` | Hugging Face Inference    |
| `logfire`     | Pydantic Logfire          |
| `evals`       | Pydantic Evals            |
| `mcp`         | MCP protocol              |
| `fastmcp`     | FastMCP                   |
| `a2a`         | Agent-to-Agent            |
| `tavily`      | Tavily search             |
| `duckduckgo`  | DuckDuckGo search         |
| `cli`         | CLI tools                 |
| `dbos`        | DBOS durable execution    |
| `prefect`     | Prefect durable execution |

## Quick Start

### Basic Agent

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    instructions='Be concise, reply with one sentence.'
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
```

### With Structured Output

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class CityInfo(BaseModel):
    name: str
    country: str
    population: int

agent = Agent('openai:gpt-4o', output_type=CityInfo)
result = agent.run_sync('Tell me about Paris')
print(result.output)  # CityInfo(name='Paris', country='France', population=2161000)
```

### With Tools and Dependencies

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class Deps:
    user_id: int

agent = Agent('openai:gpt-4o', deps_type=Deps)

@agent.tool
async def get_user_name(ctx: RunContext[Deps]) -> str:
    """Get the current user's name."""
    return f"User #{ctx.deps.user_id}"

result = agent.run_sync('What is my name?', deps=Deps(user_id=123))
```

## Key Features

| Feature              | Description                     |
| -------------------- | ------------------------------- |
| Type-safe            | Full IDE support, type checking |
| Model-agnostic       | 25+ providers supported         |
| Dependency Injection | Pass context to tools           |
| Structured Output    | Pydantic model validation       |
| Logfire Integration  | Built-in observability          |
| MCP Support          | External tools and data         |
| Evals                | Systematic testing              |
| Graphs               | Complex workflow support        |

## Supported Models

| Provider  | Models                   |
| --------- | ------------------------ |
| OpenAI    | GPT-4o, GPT-4, o1, o3    |
| Anthropic | Claude 4, Claude 3.5     |
| Google    | Gemini 2.0, Gemini 1.5   |
| Groq      | Llama, Mixtral           |
| Mistral   | Mistral Large, Codestral |
| Azure     | Azure OpenAI             |
| Bedrock   | AWS Bedrock models       |
| Ollama    | Local models             |

## Best Practices

1. **Use type hints** — enables IDE support and validation
2. **Define output types** — guarantees structured responses
3. **Use dependencies** — inject context into tools
4. **Add tool docstrings** — LLM uses them as descriptions
5. **Enable Logfire** — for production observability
6. **Use `run_sync` for simple cases** — `run` for async
7. **Override deps for testing** — `agent.override(deps=...)`
8. **Set usage limits** — prevent infinite loops with `UsageLimits`

## Prohibitions

- Do not expose API keys in code
- Do not skip output validation in production
- Do not ignore tool errors
- Do not use `run_stream` without handling partial outputs
- Do not forget to close MCP connections (`async with agent`)

## Common Patterns

### Streaming Response

```python
async with agent.run_stream('Query') as response:
    async for text in response.stream_text():
        print(text, end='')
```

### Fallback Models

```python
from pydantic_ai.models.fallback import FallbackModel

fallback = FallbackModel(openai_model, anthropic_model)
agent = Agent(fallback)
```

### MCP Integration

```python
from pydantic_ai.mcp import MCPServerStdio

server = MCPServerStdio('python', args=['mcp_server.py'])
agent = Agent('openai:gpt-4o', toolsets=[server])
```

### Testing with TestModel

```python
from pydantic_ai.models.test import TestModel

agent = Agent(model=TestModel())
result = agent.run_sync('test')  # Deterministic output
```

## Links

- [Documentation](https://ai.pydantic.dev/)
- [GitHub](https://github.com/pydantic/pydantic-ai)
- [Slack](https://slack.pydantic.dev/)
