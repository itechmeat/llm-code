# Agents Reference

Core interface for interacting with LLMs in Pydantic AI.

## Agent Components

| Component      | Description                            |
| -------------- | -------------------------------------- |
| Instructions   | Developer-written prompts for LLM      |
| Function Tools | Functions LLM can call during response |
| Output Type    | Structured datatype LLM must return    |
| Dependencies   | Context passed to tools and prompts    |
| Model          | Default LLM (can override at runtime)  |
| Model Settings | Temperature, max_tokens, timeout, etc. |

## Multimodal Input

Support for image, audio, video, and document input.

### Image Input

```python
from pydantic_ai import Agent, ImageUrl, BinaryContent

agent = Agent('openai:gpt-4o')

# URL
result = agent.run_sync([
    'What is this?',
    ImageUrl(url='https://example.com/image.png'),
])

# Local file
result = agent.run_sync([
    'Describe this image',
    BinaryContent(data=Path('photo.png').read_bytes(), media_type='image/png'),
])
```

### Audio/Video/Document Input

```python
from pydantic_ai import AudioUrl, VideoUrl, DocumentUrl

# Audio
agent.run_sync(['Transcribe this', AudioUrl(url='https://...')])

# Video
agent.run_sync(['Describe', VideoUrl(url='https://...')])

# Document (PDF)
agent.run_sync(['Summarize', DocumentUrl(url='https://...pdf')])
```

### Force Download

If provider can't fetch URL directly:

```python
ImageUrl(url='https://...', force_download=True)
```

### Provider Support

| Model         | URL Direct                 | Download Required     |
| ------------- | -------------------------- | --------------------- |
| OpenAI        | ImageUrl                   | AudioUrl, DocumentUrl |
| Anthropic     | ImageUrl, DocumentUrl(PDF) | DocumentUrl(text)     |
| Google Vertex | All URLs                   | —                     |
| Mistral       | ImageUrl, DocumentUrl(PDF) | —                     |

## Creating Agents

```python
from pydantic_ai import Agent, RunContext

agent = Agent(
    'openai:gpt-4o',           # model identifier
    deps_type=int,              # dependency type
    output_type=bool,           # structured output type
    system_prompt='Your instructions here',
    model_settings=ModelSettings(temperature=0.5),
    retries=2,                  # default retry count
)
```

## Dependencies

Dependency injection system for passing data/services to prompts, tools, validators.

### Defining Dependencies

```python
from dataclasses import dataclass
import httpx

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,  # pass TYPE, not instance
)
```

### Accessing via RunContext

```python
@agent.system_prompt
async def get_prompt(ctx: RunContext[MyDeps]) -> str:
    response = await ctx.deps.http_client.get(
        'https://api.example.com',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'}
    )
    return f"Context: {response.text}"

@agent.tool
async def fetch_data(ctx: RunContext[MyDeps], query: str) -> str:
    # ctx.deps available in tools
    return await ctx.deps.http_client.get(f'/search?q={query}')

@agent.output_validator
async def validate(ctx: RunContext[MyDeps], output: str) -> str:
    # ctx.deps available in validators
    return output
```

### Passing Dependencies at Runtime

```python
async with httpx.AsyncClient() as client:
    deps = MyDeps(api_key='secret', http_client=client)
    result = await agent.run('Query', deps=deps)
```

### Async vs Sync Dependencies

Both work. Non-async functions run in thread pool via `run_in_executor`.

```python
# Async (preferred for IO)
@agent.tool
async def async_tool(ctx: RunContext[MyDeps]) -> str:
    return await ctx.deps.http_client.get('/data')

# Sync (also works)
@agent.tool
def sync_tool(ctx: RunContext[MyDeps]) -> str:
    return ctx.deps.sync_client.get('/data')
```

### Overriding Dependencies (Testing)

```python
class TestDeps(MyDeps):
    async def system_prompt_factory(self) -> str:
        return "test prompt"

async def test_app():
    test_deps = TestDeps('test_key', None)
    with agent.override(deps=test_deps):
        result = await application_code('Query')
```

## Run Methods

| Method                | Description                             |
| --------------------- | --------------------------------------- |
| `run()`               | Async, returns `RunResult`              |
| `run_sync()`          | Synchronous wrapper                     |
| `run_stream()`        | Async context manager, streams response |
| `run_stream_sync()`   | Sync streaming                          |
| `run_stream_events()` | Async iterable of all events            |
| `iter()`              | Iterate over graph nodes                |

### Basic Run

```python
# Synchronous
result = agent.run_sync('What is 2+2?', deps=my_deps)
print(result.output)

# Async
result = await agent.run('What is 2+2?')
print(result.output)
```

### Streaming

```python
async with agent.run_stream('Tell me a story') as response:
    async for text in response.stream_text():
        print(text, end='')
```

### Stream Events

```python
from pydantic_ai import (
    AgentStreamEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    TextPartDelta,
)

async for event in agent.run_stream_events('Query'):
    if isinstance(event, PartDeltaEvent):
        if isinstance(event.delta, TextPartDelta):
            print(event.delta.content_delta)
    elif isinstance(event, FunctionToolCallEvent):
        print(f'Tool: {event.part.tool_name}')
```

### Iterate Over Graph

```python
from pydantic_graph import End

async with agent.iter('Query') as agent_run:
    async for node in agent_run:
        print(node)
print(agent_run.result.output)
```

## System Prompts vs Instructions

| Feature         | system_prompt         | instructions           |
| --------------- | --------------------- | ---------------------- |
| Message history | Preserved across runs | Only current agent's   |
| Use case        | Multi-agent handoffs  | Fresh context each run |

### Static System Prompt

```python
agent = Agent(
    'openai:gpt-4o',
    system_prompt="You are a helpful assistant."
)
```

### Dynamic System Prompt

```python
@agent.system_prompt
def add_context(ctx: RunContext[Deps]) -> str:
    return f"User: {ctx.deps.user_name}"
```

### Instructions

```python
agent = Agent(
    'openai:gpt-4o',
    instructions="Be concise."
)

@agent.instructions
def add_date() -> str:
    return f"Date: {date.today()}"

# Runtime instructions
result = agent.run_sync('Query', instructions="Extra context")
```

## Usage Limits

```python
from pydantic_ai import UsageLimits, UsageLimitExceeded

try:
    result = agent.run_sync(
        'Query',
        usage_limits=UsageLimits(
            response_tokens_limit=100,  # max response tokens
            request_limit=5,            # max model turns
            tool_calls_limit=10,        # max tool executions
        )
    )
except UsageLimitExceeded as e:
    print(f"Limit exceeded: {e}")
```

## Model Settings

Settings merge: model defaults → agent defaults → run overrides

```python
from pydantic_ai import ModelSettings

# Agent-level
agent = Agent(
    'openai:gpt-4o',
    model_settings=ModelSettings(temperature=0.5, max_tokens=500)
)

# Run-level override
result = agent.run_sync(
    'Query',
    model_settings=ModelSettings(temperature=0.0)
)
```

## Run Metadata

```python
from dataclasses import dataclass

@dataclass
class Deps:
    tenant: str

agent = Agent[Deps](
    'openai:gpt-4o',
    deps_type=Deps,
    metadata=lambda ctx: {'tenant': ctx.deps.tenant},
)

result = agent.run_sync(
    'Query',
    deps=Deps(tenant='acme'),
    metadata={'extra': 'data'},  # merged with agent metadata
)
print(result.metadata)  # {'tenant': 'acme', 'extra': 'data'}
```

Run context now exposes output validation retry count for observability (v1.52.0).

## Reflection and Self-Correction

```python
from pydantic_ai import ModelRetry

@agent.tool(retries=3)
def lookup_user(ctx: RunContext[Deps], name: str) -> int:
    user = ctx.deps.db.find(name)
    if not user:
        raise ModelRetry(f"User {name} not found. Try full name.")
    return user.id
```

## Error Handling

```python
from pydantic_ai import UnexpectedModelBehavior, capture_run_messages

with capture_run_messages() as messages:
    try:
        result = agent.run_sync('Query')
    except UnexpectedModelBehavior as e:
        print(f"Error: {e}")
        print(f"Messages: {messages}")
```

## Agent Constructor Parameters

| Parameter            | Type             | Description                    |
| -------------------- | ---------------- | ------------------------------ |
| `model`              | str or Model     | Model identifier or instance   |
| `deps_type`          | type             | Dependency type for RunContext |
| `output_type`        | type             | Pydantic model for output      |
| `system_prompt`      | str              | Static system prompt           |
| `instructions`       | str              | Instructions (not in history)  |
| `model_settings`     | ModelSettings    | Default model settings         |
| `retries`            | int              | Default retry count            |
| `metadata`           | dict or callable | Run metadata                   |
| `end_strategy`       | str              | 'early' or 'exhaustive'        |
| `history_processors` | list             | Message history processors     |

---

## Messages and Chat History

### Accessing Messages

```python
result = agent.run_sync('Tell me a joke')

# All messages including prior runs
all_msgs = result.all_messages()

# Only messages from current run
new_msgs = result.new_messages()

# JSON serialization
json_bytes = result.all_messages_json()
```

### Continuing Conversations

```python
result1 = agent.run_sync('Tell me a joke')
print(result1.output)

# Continue with message history
result2 = agent.run_sync(
    'Explain?',
    message_history=result1.new_messages()
)
print(result2.output)
```

### Serialize/Deserialize Messages

```python
from pydantic_core import to_jsonable_python
from pydantic_ai import ModelMessagesTypeAdapter

# Serialize
history = result.all_messages()
as_python = to_jsonable_python(history)

# Deserialize
restored = ModelMessagesTypeAdapter.validate_python(as_python)

# Use restored history
result = agent.run_sync('Continue', message_history=restored)
```

### History Processors

Intercept and modify message history before each request:

```python
from pydantic_ai import Agent, ModelMessage, ModelRequest

def keep_recent(messages: list[ModelMessage]) -> list[ModelMessage]:
    """Keep only last 5 messages."""
    return messages[-5:] if len(messages) > 5 else messages

def filter_responses(messages: list[ModelMessage]) -> list[ModelMessage]:
    """Remove ModelResponse, keep only requests."""
    return [m for m in messages if isinstance(m, ModelRequest)]

agent = Agent(
    'openai:gpt-4o',
    history_processors=[filter_responses, keep_recent],
)
```

### Context-Aware Processor

```python
def token_aware(ctx: RunContext[None], messages: list[ModelMessage]) -> list[ModelMessage]:
    if ctx.usage.total_tokens > 1000:
        return messages[-3:]  # Keep recent when high token usage
    return messages
```

### Summarize Old Messages

```python
summarizer = Agent('openai:gpt-4o-mini', instructions='Summarize conversation.')

async def summarize_old(messages: list[ModelMessage]) -> list[ModelMessage]:
    if len(messages) > 10:
        oldest = messages[:10]
        summary = await summarizer.run(message_history=oldest)
        return summary.new_messages() + messages[-1:]
    return messages
```

**Warning:** When slicing history, ensure tool calls and returns are paired.

---

## Direct Model Requests

Low-level API for making requests without full Agent functionality.

### When to Use

- Need direct control over model interactions
- Building custom abstractions
- Don't need tool execution, retrying, structured output

### Basic Usage

```python
from pydantic_ai import ModelRequest
from pydantic_ai.direct import model_request_sync

response = model_request_sync(
    'anthropic:claude-haiku-4-5',
    [ModelRequest.user_text_prompt('What is the capital of France?')]
)

print(response.parts[0].content)  # Paris
print(response.usage)  # RequestUsage(input_tokens=56, output_tokens=7)
```

### Async Request

```python
from pydantic_ai.direct import model_request

response = await model_request(
    'openai:gpt-4o',
    [ModelRequest.user_text_prompt('Hello')]
)
```

### With Tool Definitions

```python
from pydantic import BaseModel
from pydantic_ai import ModelRequest, ToolDefinition
from pydantic_ai.direct import model_request
from pydantic_ai.models import ModelRequestParameters

class Divide(BaseModel):
    """Divide two numbers."""
    numerator: float
    denominator: float

response = await model_request(
    'openai:gpt-4o',
    [ModelRequest.user_text_prompt('What is 123 / 456?')],
    model_request_parameters=ModelRequestParameters(
        function_tools=[
            ToolDefinition(
                name='divide',
                description=Divide.__doc__,
                parameters_json_schema=Divide.model_json_schema(),
            )
        ],
        allow_text_output=True,
    ),
)
```

### Available Functions

| Function                    | Description        |
| --------------------------- | ------------------ |
| `model_request`             | Async non-streamed |
| `model_request_sync`        | Sync non-streamed  |
| `model_request_stream`      | Async streamed     |
| `model_request_stream_sync` | Sync streamed      |

---

## Multi-Agent Patterns

Five levels of complexity:

1. **Single agent** — Basic agent workflows
2. **Agent delegation** — Agent calls another via tools
3. **Programmatic hand-off** — App code orchestrates agents
4. **Graph-based control** — State machine controls agents
5. **Deep agents** — Autonomous with planning, files, code exec

### Agent Delegation

Parent agent delegates to child agent via tool:

```python
from pydantic_ai import Agent, RunContext

parent_agent = Agent('openai:gpt-4o', system_prompt='Use joke_factory to get jokes.')
child_agent = Agent('anthropic:claude-sonnet-4-5', output_type=list[str])

@parent_agent.tool
async def joke_factory(ctx: RunContext[None], count: int) -> list[str]:
    result = await child_agent.run(
        f'Generate {count} jokes',
        usage=ctx.usage,  # Share usage tracking
    )
    return result.output
```

**Key points:**

- Pass `usage=ctx.usage` to track combined usage
- Pass `deps=ctx.deps` if child needs same dependencies
- Different models allowed (cost calculation manual)

### Programmatic Hand-off

Sequential agents with app logic between:

```python
from pydantic_ai import Agent, ModelMessage

flight_agent = Agent('openai:gpt-4o', output_type=FlightDetails | Failed)
seat_agent = Agent('openai:gpt-4o', output_type=SeatPreference | Failed)

async def main():
    # First agent
    flight_result = await flight_agent.run('Find flight to Paris')

    if isinstance(flight_result.output, FlightDetails):
        # Second agent (independent)
        seat_result = await seat_agent.run('Window seat please')
```

### Agent with Shared Dependencies

```python
@dataclass
class SharedDeps:
    http_client: httpx.AsyncClient
    api_key: str

parent = Agent('openai:gpt-4o', deps_type=SharedDeps)
child = Agent('anthropic:claude-sonnet-4-5', deps_type=SharedDeps)

@parent.tool
async def delegate(ctx: RunContext[SharedDeps], task: str) -> str:
    result = await child.run(
        task,
        deps=ctx.deps,   # Share dependencies
        usage=ctx.usage, # Share usage
    )
    return result.output
```

### Deep Agent Capabilities

| Capability   | Implementation           |
| ------------ | ------------------------ |
| Planning     | Task management toolsets |
| File ops     | FileSystemToolset        |
| Delegation   | Sub-agents via tools     |
| Code exec    | Sandboxed containers     |
| Context mgmt | History processors       |
| Approval     | ApprovalRequiredToolset  |
| Durability   | Temporal, DBOS, Prefect  |

---

## Thinking (Reasoning)

Enable step-by-step reasoning before final answer.

### Provider Configuration

| Provider         | Setting                    | Example                                      |
| ---------------- | -------------------------- | -------------------------------------------- |
| OpenAI Responses | `openai_reasoning_effort`  | `'low'`, `'medium'`, `'high'`                |
| Anthropic        | `anthropic_thinking`       | `{'type': 'enabled', 'budget_tokens': 1024}` |
| Google           | `google_thinking_config`   | `{'include_thoughts': True}`                 |
| Groq             | `groq_reasoning_format`    | `'raw'`, `'hidden'`, `'parsed'`              |
| OpenRouter       | `openrouter_reasoning`     | `{'effort': 'high'}`                         |
| Mistral          | Auto (magistral models)    | No config needed                             |
| Cohere           | Auto (command-a-reasoning) | No config needed                             |

### OpenAI Responses Example

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5')
settings = OpenAIResponsesModelSettings(
    openai_reasoning_effort='low',
    openai_reasoning_summary='detailed',
)
agent = Agent(model, model_settings=settings)
```

### Anthropic Example

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings

model = AnthropicModel('claude-sonnet-4-0')
settings = AnthropicModelSettings(
    anthropic_thinking={'type': 'enabled', 'budget_tokens': 1024},
)
agent = Agent(model, model_settings=settings)
```

### Google Example

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

model = GoogleModel('gemini-2.5-pro')
settings = GoogleModelSettings(google_thinking_config={'include_thoughts': True})
agent = Agent(model, model_settings=settings)
```

### Bedrock Examples

```python
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings

# Anthropic on Bedrock
model = BedrockConverseModel('us.anthropic.claude-sonnet-4-5-20250929-v1:0')
settings = BedrockModelSettings(
    bedrock_additional_model_requests_fields={
        'thinking': {'type': 'enabled', 'budget_tokens': 1024}
    }
)

# OpenAI on Bedrock
model = BedrockConverseModel('openai.gpt-oss-120b-1:0')
settings = BedrockModelSettings(
    bedrock_additional_model_requests_fields={'reasoning_effort': 'low'}
)

# Deepseek on Bedrock (always enabled)
model = BedrockConverseModel('us.deepseek.r1-v1:0')
agent = Agent(model=model)  # No settings needed
```

### Thinking Output

Thinking parts are returned as `ThinkingPart` objects in the message history:

- OpenAI Chat: `<think>` tags converted to ThinkingPart
- OpenAI Responses: Native thinking parts
- Groq `parsed`: Structured thinking parts
- Local models: `<think>` tags auto-converted

---

## Troubleshooting

### Jupyter Notebook: Event Loop Error

```python
# Error: RuntimeError: This event loop is already running
# Fix: Install and apply nest-asyncio BEFORE any agent runs
import nest_asyncio
nest_asyncio.apply()
```

**Note:** Works in Google Colab and Marimo too.

### API Key Missing

```
UserError: API key must be provided or set in the [MODEL]_API_KEY environment variable
```

Solutions:

1. Set environment variable: `export OPENAI_API_KEY=sk-...`
2. Pass directly: `OpenAIModel('gpt-4o', api_key='sk-...')`

### Monitoring HTTPX Requests

Use custom `httpx` clients for request/response inspection:

```python
import httpx
import logfire

# Install logfire httpx integration for monitoring
logfire.instrument_httpx()

client = httpx.AsyncClient()
model = OpenAIModel('gpt-4o', http_client=client)
```

### Community Support

- **Slack**: Join `#pydantic-ai` in Pydantic Slack
- **GitHub Issues**: https://github.com/pydantic/pydantic-ai/issues
- **Logfire Pro**: Private collaboration channel available
