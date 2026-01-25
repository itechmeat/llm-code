# Function Tools Reference

Tools let models perform actions and retrieve information during response generation.

## Registration Methods

### 1. Decorator with Context

```python
from pydantic_ai import Agent, RunContext

agent = Agent('openai:gpt-4o', deps_type=str)

@agent.tool
def get_user_name(ctx: RunContext[str]) -> str:
    """Get the current user's name."""
    return ctx.deps
```

### 2. Decorator without Context

```python
@agent.tool_plain
def roll_dice() -> str:
    """Roll a six-sided die."""
    return str(random.randint(1, 6))
```

### 3. Via Agent Constructor

```python
from pydantic_ai import Tool

def roll_dice() -> str:
    """Roll a die."""
    return str(random.randint(1, 6))

def get_name(ctx: RunContext[str]) -> str:
    """Get name."""
    return ctx.deps

# Auto-detect context
agent = Agent('openai:gpt-4o', tools=[roll_dice, get_name])

# Explicit context specification
agent = Agent('openai:gpt-4o', tools=[
    Tool(roll_dice, takes_ctx=False),
    Tool(get_name, takes_ctx=True),
])
```

## Tool Schema

Parameters extracted from function signature. Docstrings provide descriptions.

### Docstring Formats

Supports: `google`, `numpy`, `sphinx` (auto-detected)

```python
@agent.tool_plain(docstring_format='google', require_parameter_descriptions=True)
def search(query: str, limit: int) -> str:
    """Search for items.

    Args:
        query: Search query string
        limit: Maximum results to return
    """
    return "results"
```

### Single Parameter Simplification

If tool has single object parameter, schema is simplified:

```python
from pydantic import BaseModel

class SearchParams(BaseModel):
    """Search parameters"""
    query: str
    limit: int = 10

@agent.tool_plain
def search(params: SearchParams) -> str:
    return f"Searching: {params.query}"
```

## Tool Return Types

Any JSON-serializable type works:

```python
@agent.tool_plain
def get_data() -> dict[str, list[int]]:
    return {"values": [1, 2, 3]}

@agent.tool_plain
def get_count() -> int:
    return 42
```

## RunContext Properties

```python
@agent.tool
async def my_tool(ctx: RunContext[MyDeps]) -> str:
    ctx.deps         # Dependencies
    ctx.retry        # Current retry count
    ctx.tool_name    # Name of this tool
    ctx.run_step     # Current run step
    ctx.usage        # Token usage so far
```

## Tool Retries

```python
from pydantic_ai import ModelRetry

@agent.tool(retries=3)
def fetch_user(ctx: RunContext[Deps], user_id: int) -> dict:
    """Fetch user by ID."""
    user = ctx.deps.db.get(user_id)
    if not user:
        raise ModelRetry(f"User {user_id} not found. Try different ID.")
    return user
```

## Custom Tool Configuration

```python
from pydantic_ai import Tool

tool = Tool(
    my_function,
    takes_ctx=True,
    name='custom_name',           # Override function name
    description='Custom desc',    # Override docstring
    retries=2,
)

agent = Agent('openai:gpt-4o', tools=[tool])
```

## Advanced Tool Returns

Control both return value and model content:

```python
from pydantic_ai import Agent, ToolReturn, BinaryContent

agent = Agent('openai:gpt-4o')

@agent.tool_plain
def click_and_capture(x: int, y: int) -> ToolReturn:
    """Click at coordinates and show before/after screenshots."""
    before = capture_screen()
    perform_click(x, y)
    after = capture_screen()

    return ToolReturn(
        return_value=f'Clicked at ({x}, {y})',  # Tool result for model
        content=[  # Additional context (separate user message)
            'Before:',
            BinaryContent(data=before, media_type='image/png'),
            'After:',
            BinaryContent(data=after, media_type='image/png'),
        ],
        metadata={  # Not sent to LLM, available in your app
            'coordinates': {'x': x, 'y': y},
        }
    )
```

### ToolReturn Fields

| Field          | Purpose                                                 |
| -------------- | ------------------------------------------------------- |
| `return_value` | Serialized and sent as tool's result                    |
| `content`      | Additional context (text, images, docs) as user message |
| `metadata`     | App-side data, not sent to LLM ("artifacts")            |

## Custom Tool Schema

For functions without proper documentation:

```python
from pydantic_ai import Agent, Tool

def foobar(**kwargs) -> str:
    return kwargs['a'] + kwargs['b']

tool = Tool.from_schema(
    function=foobar,
    name='sum',
    description='Sum two numbers.',
    json_schema={
        'properties': {
            'a': {'description': 'first number', 'type': 'integer'},
            'b': {'description': 'second number', 'type': 'integer'},
        },
        'required': ['a', 'b'],
        'type': 'object',
    },
    takes_ctx=False,
)

agent = Agent('openai:gpt-4o', tools=[tool])
```

## Dynamic Tools (Prepare)

Customize tool availability per-run:

```python
from pydantic_ai import Agent, RunContext, ToolDefinition

agent = Agent('openai:gpt-4o', deps_type=int)

async def only_if_42(
    ctx: RunContext[int], tool_def: ToolDefinition
) -> ToolDefinition | None:
    if ctx.deps == 42:
        return tool_def
    return None  # Hide tool

@agent.tool(prepare=only_if_42)
def hitchhiker(ctx: RunContext[int], answer: str) -> str:
    return f'{ctx.deps}{answer}'
```

### Agent-wide prepare_tools

Filter or modify all tools at once:

```python
from dataclasses import replace
from pydantic_ai import Agent, RunContext, ToolDefinition

async def turn_on_strict_if_openai(
    ctx: RunContext[None], tool_defs: list[ToolDefinition]
) -> list[ToolDefinition] | None:
    if ctx.model.system == 'openai':
        return [replace(td, strict=True) for td in tool_defs]
    return tool_defs

agent = Agent('openai:gpt-4o', prepare_tools=turn_on_strict_if_openai)
```

## Tool Timeout

```python
import asyncio
from pydantic_ai import Agent

# Default timeout for all tools
agent = Agent('openai:gpt-4o', tool_timeout=30)

@agent.tool_plain(timeout=5)  # Override per-tool
async def fast_tool() -> str:
    await asyncio.sleep(1)
    return 'Done'
```

On timeout: tool fails → retry prompt sent → counts toward retry limit.

## Tool Execution & Retries

### Validation Errors

Arguments validated by Pydantic → ValidationError → RetryPromptPart → LLM retries.

### Explicit Retry

```python
from pydantic_ai import ModelRetry

def my_tool(query: str) -> str:
    if query == 'bad':
        raise ModelRetry("Query 'bad' not allowed. Try again.")
    return 'Success!'
```

## Parallel Tool Calls

Multiple tool calls run concurrently via `asyncio.create_task`.

```python
# Force sequential execution for specific tool
@agent.tool_plain(sequential=True)
def must_run_alone() -> str:
    return 'Done'

# Or for entire run
with agent.sequential_tool_calls():
    result = await agent.run('...')
```

### Limit Tool Calls

```python
from pydantic_ai import UsageLimits

result = await agent.run('...', usage_limits=UsageLimits(tool_calls_limit=10))
```

---

## Deferred Tools

Tools that cannot/should not be executed during the same agent run.

### Use Cases

- Tool requires user approval first
- Tool depends on external service, frontend, or user
- Result takes longer than reasonable to keep agent running

### Tool Approval (Human-in-the-Loop)

```python
from pydantic_ai import (
    Agent,
    ApprovalRequired,
    DeferredToolRequests,
    DeferredToolResults,
    RunContext,
    ToolDenied,
)

agent = Agent('openai:gpt-4o', output_type=[str, DeferredToolRequests])

@agent.tool_plain(requires_approval=True)  # Always requires approval
def delete_file(path: str) -> str:
    return f'File {path!r} deleted'

@agent.tool
def update_file(ctx: RunContext, path: str, content: str) -> str:
    if path == '.env' and not ctx.tool_call_approved:
        raise ApprovalRequired(metadata={'reason': 'protected'})  # Conditional
    return f'File {path!r} updated'

# First run: ends with deferred requests
result = agent.run_sync('Delete file.txt and clear .env')
messages = result.all_messages()

assert isinstance(result.output, DeferredToolRequests)
requests = result.output

# Gather approvals and continue
results = DeferredToolResults()
for call in requests.approvals:
    if call.tool_name == 'delete_file':
        results.approvals[call.tool_call_id] = ToolDenied('Deletion not allowed')
    else:
        results.approvals[call.tool_call_id] = True  # Approve

# Second run: continue with approvals
result = agent.run_sync(
    'Continue',
    message_history=messages,
    deferred_tool_results=results,
)
```

### External Tools

Tools executed by external service/frontend:

```python
from pydantic_ai import Agent, CallDeferred, DeferredToolRequests, DeferredToolResults

agent = Agent('openai:gpt-4o', output_type=[str, DeferredToolRequests])

@agent.tool
async def long_task(ctx, query: str) -> str:
    task_id = schedule_background_task(query)  # Your task scheduler
    raise CallDeferred(metadata={'task_id': task_id})

# First run: ends with deferred calls
result = await agent.run('Calculate something complex')
requests = result.output
messages = result.all_messages()

# Wait for results (e.g., poll background worker)
task_results = await wait_for_tasks(requests)

# Build results
results = DeferredToolResults()
for call in requests.calls:
    task_id = requests.metadata[call.tool_call_id]['task_id']
    results.calls[call.tool_call_id] = task_results[task_id]

# Continue with results
result = await agent.run(message_history=messages, deferred_tool_results=results)
```

### DeferredToolRequests

Returned when agent run ends with deferred tools:

| Field       | Description                               |
| ----------- | ----------------------------------------- |
| `calls`     | List of `ToolCallPart` for external tools |
| `approvals` | List of `ToolCallPart` needing approval   |
| `metadata`  | Dict mapping tool_call_id → metadata      |

### DeferredToolResults

Provide results/approvals to continue:

| Field       | Description                                             |
| ----------- | ------------------------------------------------------- |
| `calls`     | Dict: tool_call_id → result value                       |
| `approvals` | Dict: tool_call_id → True/False/ToolApproved/ToolDenied |
| `metadata`  | Dict: tool_call_id → metadata for RunContext            |

---

## Toolsets

Collections of tools that can be registered with an agent.

### FunctionToolset

```python
from pydantic_ai.toolsets import FunctionToolset

toolset = FunctionToolset()

@toolset.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

agent = Agent('openai:gpt-4o', toolsets=[toolset])
```

### Combining Toolsets

```python
from pydantic_ai.toolsets import CombinedToolset

combined = CombinedToolset([toolset1, toolset2, mcp_server])
agent = Agent('openai:gpt-4o', toolsets=[combined])
```

### Filtering Tools

```python
from pydantic_ai.toolsets import FilteredToolset

def filter_fn(ctx, tool_def):
    return tool_def.name.startswith('safe_')

filtered = FilteredToolset(toolset, filter_fn)
# Or chain: toolset.filtered(filter_fn)
```

### Prefixing Tool Names

```python
from pydantic_ai.toolsets import PrefixedToolset

prefixed = PrefixedToolset(toolset, 'math_')
# Or chain: toolset.prefixed('math_')
```

### Renaming Tools

```python
from pydantic_ai.toolsets import RenamedToolset

renamed = RenamedToolset(toolset, {'new_name': 'original_name'})
# Or chain: toolset.renamed({'new_name': 'original_name'})
```

### Approval Required

```python
from pydantic_ai.toolsets import ApprovalRequiredToolset

def needs_approval(ctx, tool_def, args):
    return tool_def.name == 'delete_file'

approved = ApprovalRequiredToolset(toolset, needs_approval)
# Or chain: toolset.approval_required(needs_approval)
```

### Dynamic Toolsets

```python
@agent.toolset
def dynamic_tools(ctx: RunContext[Deps]):
    toolset = FunctionToolset()
    if ctx.deps.is_admin:
        @toolset.tool
        def admin_action(): ...
    return toolset
```

### External Toolsets

For tools executed by upstream service/frontend:

```python
from pydantic_ai.toolsets import ExternalToolset
from pydantic_ai import ToolDefinition, DeferredToolRequests

external = ExternalToolset([
    ToolDefinition(
        name='ui_confirm',
        description='Show confirmation dialog',
        parameters_json_schema={'type': 'object', ...},
    )
])

agent = Agent('openai:gpt-4o', toolsets=[external], output_type=[str, DeferredToolRequests])
```

### Third-Party Toolsets

| Toolset            | Description               |
| ------------------ | ------------------------- |
| `MCPServer*`       | MCP protocol servers      |
| `FastMCPToolset`   | FastMCP client            |
| `LangChainToolset` | LangChain community tools |
| `ACIToolset`       | ACI.dev tool library      |

## Tool Categories

| Category       | Description                                   |
| -------------- | --------------------------------------------- |
| Function Tools | Custom functions you define                   |
| Toolsets       | Collections of tools                          |
| Builtin Tools  | Provider-native tools (web search, code exec) |
| Common Tools   | Ready-to-use implementations                  |
| MCP Tools      | Model Context Protocol tools                  |
| Deferred Tools | Require approval before execution             |

---

# Structured Output Reference

Agent's `output_type` defines the structured data the model must return.

## Supported Types

- Pydantic `BaseModel`
- `dataclass`
- `TypedDict`
- Scalar types (`str`, `int`, `list[str]`, etc.)
- Union types (`Foo | Bar`)
- Output functions

## Basic Usage

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class CityLocation(BaseModel):
    city: str
    country: str

agent = Agent('openai:gpt-4o', output_type=CityLocation)
result = agent.run_sync('Where were the 2012 Olympics?')
print(result.output)  # CityLocation(city='London', country='UK')
```

## Multiple Output Types

```python
class Box(BaseModel):
    width: int
    height: int
    units: str

# List of types or union
agent = Agent(
    'openai:gpt-4o',
    output_type=[Box, str],  # can return Box or ask for clarification
)
```

## Output Functions

End run with function result instead of passing to model:

```python
from pydantic_ai import Agent, ModelRetry

def run_sql(query: str) -> list[dict]:
    """Execute SQL and return results."""
    if 'DROP' in query.upper():
        raise ModelRetry("DROP not allowed. Try SELECT.")
    return db.execute(query)

agent = Agent('openai:gpt-4o', output_type=run_sql)
```

## Output Modes

| Mode             | Description                                |
| ---------------- | ------------------------------------------ |
| `ToolOutput`     | Default. Uses tool calling (most reliable) |
| `NativeOutput`   | Uses model's native structured output      |
| `PromptedOutput` | Injects schema into prompt                 |

### Tool Output (Default)

```python
from pydantic_ai import ToolOutput

agent = Agent(
    'openai:gpt-4o',
    output_type=ToolOutput(MyModel, name='return_data', strict=True),
)
```

### Native Output

```python
from pydantic_ai import NativeOutput

agent = Agent(
    'openai:gpt-4o',
    output_type=NativeOutput([Fruit, Vehicle]),
)
```

### Text Output

Process plain text through function:

```python
from pydantic_ai import TextOutput

def split_words(text: str) -> list[str]:
    return text.split()

agent = Agent('openai:gpt-4o', output_type=TextOutput(split_words))
```

## Output Validators

```python
@agent.output_validator
async def validate(ctx: RunContext[Deps], output: MyModel) -> MyModel:
    if not output.is_valid:
        raise ModelRetry("Invalid output, try again")
    return output
```

### Streaming Partial Output

```python
@agent.output_validator
def validate(ctx: RunContext, output: str) -> str:
    if ctx.partial_output:
        return output  # Skip validation for partial
    if len(output) < 50:
        raise ModelRetry('Too short')
    return output
```

## Custom JSON Schema

```python
from pydantic_ai import StructuredDict

PersonDict = StructuredDict(
    {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'},
        },
        'required': ['name', 'age'],
    },
    name='Person',
)

agent = Agent('openai:gpt-4o', output_type=PersonDict)
```

---

## Built-in Tools

Native tools executed by model providers (not by Pydantic AI).

### Available Built-in Tools

| Tool                  | Purpose               | Providers                                 |
| --------------------- | --------------------- | ----------------------------------------- |
| `WebSearchTool`       | Search the web        | OpenAI Responses, Anthropic, Google, Groq |
| `CodeExecutionTool`   | Execute code securely | OpenAI, Google, Anthropic                 |
| `ImageGenerationTool` | Generate images       | OpenAI Responses, Google                  |
| `WebFetchTool`        | Fetch web pages       | Anthropic, Google                         |
| `MemoryTool`          | Persistent memory     | Anthropic                                 |
| `MCPServerTool`       | Remote MCP servers    | OpenAI Responses, Anthropic               |
| `FileSearchTool`      | Vector search (RAG)   | OpenAI Responses, Google                  |

### Web Search Example

```python
from pydantic_ai import Agent, WebSearchTool, WebSearchUserLocation

agent = Agent(
    'anthropic:claude-sonnet-4-0',
    builtin_tools=[
        WebSearchTool(
            search_context_size='high',
            user_location=WebSearchUserLocation(
                city='San Francisco',
                country='US',
            ),
            blocked_domains=['spam-site.net'],
            max_uses=5,  # Anthropic only
        )
    ],
)

result = agent.run_sync('What is the biggest AI news this week?')
```

### Code Execution Example

```python
from pydantic_ai import Agent, CodeExecutionTool

agent = Agent('anthropic:claude-sonnet-4-0', builtin_tools=[CodeExecutionTool()])
result = agent.run_sync('Calculate the factorial of 15.')
```

### Image Generation Example

```python
from pydantic_ai import Agent, BinaryImage, ImageGenerationTool

agent = Agent(
    'openai-responses:gpt-5',
    builtin_tools=[
        ImageGenerationTool(
            quality='high',
            size='1024x1024',
            output_format='png',
        )
    ],
    output_type=BinaryImage,
)

result = agent.run_sync('Generate an image of a sunset.')
```

### File Search (RAG) Example

```python
from pydantic_ai import Agent, FileSearchTool
from pydantic_ai.models.openai import OpenAIResponsesModel

model = OpenAIResponsesModel('gpt-5')

# Upload files to vector store first
file = await model.client.files.create(file=open('doc.txt', 'rb'), purpose='assistants')
vector_store = await model.client.vector_stores.create(name='my-docs')
await model.client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=file.id
)

agent = Agent(
    model,
    builtin_tools=[FileSearchTool(file_store_ids=[vector_store.id])]
)

result = await agent.run('What does the document say about X?')
```

### MCP Server Tool Example

```python
from pydantic_ai import Agent, MCPServerTool

agent = Agent(
    'anthropic:claude-sonnet-4-5',
    builtin_tools=[
        MCPServerTool(
            id='deepwiki',
            url='https://mcp.deepwiki.com/mcp',
            # authorization_token='...',  # If required
            # allowed_tools=['tool1', 'tool2'],
        )
    ]
)

result = agent.run_sync('Tell me about pydantic/pydantic-ai repo.')
```

### Key Notes

- Built-in tools executed by provider, not Pydantic AI
- Not all providers support all tools
- Google: Cannot use built-in + function tools together
- OpenAI: Web search/MCP require Responses API (`openai-responses:`)
- Access results via `result.response.builtin_tool_calls`

---

## Common Tools

Pre-built tools that Pydantic AI executes (not provider-side).

### DuckDuckGo Search

```bash
pip install "pydantic-ai-slim[duckduckgo]"
```

```python
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

agent = Agent(
    'openai:gpt-4o',
    tools=[duckduckgo_search_tool()],
    instructions='Search DuckDuckGo for the query and return results.',
)

result = agent.run_sync('Top AI news this week')
```

### Tavily Search

Paid service with free credits. Requires API key.

```bash
pip install "pydantic-ai-slim[tavily]"
```

```python
import os
from pydantic_ai import Agent
from pydantic_ai.common_tools.tavily import tavily_search_tool

api_key = os.getenv('TAVILY_API_KEY')

agent = Agent(
    'openai:gpt-4o',
    tools=[tavily_search_tool(api_key)],
    instructions='Search Tavily for the query and return results.',
)

result = agent.run_sync('Tell me top GenAI news with links.')
```

### Exa Neural Search

Neural search engine for high-quality results. Paid with free credits.

```bash
pip install "pydantic-ai-slim[exa]"
```

**Individual Tools:**

```python
import os
from pydantic_ai import Agent
from pydantic_ai.common_tools.exa import exa_search_tool

api_key = os.getenv('EXA_API_KEY')

agent = Agent(
    'openai:gpt-4o',
    tools=[exa_search_tool(api_key, num_results=5, max_characters=1000)],
    instructions='Search the web using Exa.',
)

result = agent.run_sync('Latest developments in quantum computing')
```

**Using ExaToolset (recommended):**

```python
import os
from pydantic_ai import Agent
from pydantic_ai.common_tools.exa import ExaToolset

api_key = os.getenv('EXA_API_KEY')

toolset = ExaToolset(
    api_key,
    num_results=5,
    max_characters=1000,  # Limit text for token control
    include_search=True,  # Web search (default: True)
    include_find_similar=True,  # Find similar pages (default: True)
    include_get_contents=False,  # Full content retrieval
    include_answer=True,  # AI answers with citations (default: True)
)

agent = Agent('openai:gpt-4o', toolsets=[toolset])
result = agent.run_sync('Find recent AI papers and summarize findings.')
```

**Exa Tools Available:**

| Tool                    | Description                           |
| ----------------------- | ------------------------------------- |
| `exa_search_tool`       | Web search (auto/keyword/neural/deep) |
| `exa_find_similar_tool` | Find pages similar to a URL           |
| `exa_get_contents_tool` | Get full text from URLs               |
| `exa_answer_tool`       | AI answers with citations             |

### Common vs Built-in Tools

| Aspect       | Common Tools      | Built-in Tools        |
| ------------ | ----------------- | --------------------- |
| Execution    | By Pydantic AI    | By model provider     |
| Works with   | All models        | Provider-specific     |
| Installation | Optional packages | Part of core          |
| Parameter    | `tools=[...]`     | `builtin_tools=[...]` |
