# UI Event Streams Reference

Pydantic AI supports multiple UI event stream protocols for building interactive AI applications.

---

## Overview

UI event stream integrations enable streaming agent events to frontend applications.

| Protocol  | Adapter           | Use Case                                 |
| --------- | ----------------- | ---------------------------------------- |
| AG-UI     | `AGUIAdapter`     | CopilotKit, frontend tools, shared state |
| Vercel AI | `VercelAIAdapter` | Vercel AI SDK, React/Next.js apps        |

Both inherit from `UIAdapter` abstract class.

---

## AG-UI (Agent-User Interaction)

Open standard by CopilotKit for frontend-agent communication.

### Installation

```bash
pip install 'pydantic-ai-slim[ag-ui]'
pip install uvicorn  # ASGI server
```

### Three Usage Methods

#### 1. Handle Run Input Directly

```python
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from pydantic_ai import Agent
from pydantic_ai.ui import SSE_CONTENT_TYPE
from pydantic_ai.ui.ag_ui import AGUIAdapter

agent = Agent('openai:gpt-4o', instructions='Be fun!')
app = FastAPI()

@app.post('/')
async def run_agent(request: Request):
    run_input = AGUIAdapter.build_run_input(await request.body())
    adapter = AGUIAdapter(agent=agent, run_input=run_input)
    event_stream = adapter.run_stream()  # Returns AG-UI events
    sse_stream = adapter.encode_stream(event_stream)
    return StreamingResponse(sse_stream, media_type=SSE_CONTENT_TYPE)
```

#### 2. Handle Starlette/FastAPI Request (Recommended)

```python
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from pydantic_ai import Agent
from pydantic_ai.ui.ag_ui import AGUIAdapter

agent = Agent('openai:gpt-4o', instructions='Be fun!')
app = FastAPI()

@app.post('/')
async def run_agent(request: Request) -> Response:
    return await AGUIAdapter.dispatch_request(request, agent=agent)
```

#### 3. Stand-alone ASGI App

```python
from pydantic_ai import Agent
from pydantic_ai.ui.ag_ui.app import AGUIApp

agent = Agent('openai:gpt-4o', instructions='Be fun!')
app = AGUIApp(agent)
# Run: uvicorn my_module:app
```

### State Management

Share state between UI and server using `StateDeps`:

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.ui import StateDeps
from pydantic_ai.ui.ag_ui.app import AGUIApp

class DocumentState(BaseModel):
    """Shared document state."""
    document: str = ''

agent = Agent(
    'openai:gpt-4o',
    instructions='Be fun!',
    deps_type=StateDeps[DocumentState],
)
app = AGUIApp(agent, deps=StateDeps(DocumentState()))
```

Custom deps must implement `StateHandler` protocol (dataclass with `state` field).

### Frontend Tools

AG-UI frontend tools are automatically provided to the agent.

### Custom Events

Return AG-UI events from tools using `ToolReturn`:

```python
from ag_ui.core import CustomEvent, EventType, StateSnapshotEvent
from pydantic_ai import Agent, RunContext, ToolReturn
from pydantic_ai.ui import StateDeps

@agent.tool
async def update_state(ctx: RunContext[StateDeps[DocumentState]]) -> ToolReturn:
    return ToolReturn(
        return_value='State updated',
        metadata=[
            StateSnapshotEvent(
                type=EventType.STATE_SNAPSHOT,
                snapshot=ctx.deps.state,
            ),
        ],
    )

@agent.tool_plain
async def custom_events() -> ToolReturn:
    return ToolReturn(
        return_value='Events sent',
        metadata=[
            CustomEvent(type=EventType.CUSTOM, name='count', value=1),
            CustomEvent(type=EventType.CUSTOM, name='count', value=2),
        ]
    )
```

---

## Vercel AI Data Stream Protocol

Native support for Vercel AI SDK frontend applications.

### Update note (v1.62.0)

Tool approval integration is supported in Vercel adapter workflows.

### Update note (v1.60.0)

AG-UI parent message linking was fixed for back-to-back built-in tool calls.

### Basic Usage (FastAPI)

```python
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from pydantic_ai import Agent
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

agent = Agent('openai:gpt-4o')
app = FastAPI()

@app.post('/chat')
async def chat(request: Request) -> Response:
    return await VercelAIAdapter.dispatch_request(request, agent=agent)
```

### Advanced Usage

For non-Starlette frameworks or fine-grained control:

```python
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from pydantic_ai import Agent
from pydantic_ai.ui import SSE_CONTENT_TYPE
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

agent = Agent('openai:gpt-4o')
app = FastAPI()

@app.post('/chat')
async def chat(request: Request):
    accept = request.headers.get('accept', SSE_CONTENT_TYPE)

    # 1. Build run input from request
    run_input = VercelAIAdapter.build_run_input(await request.body())

    # 2. Create adapter and run
    adapter = VercelAIAdapter(agent=agent, run_input=run_input, accept=accept)
    event_stream = adapter.run_stream()

    # 3. Encode and return
    sse_stream = adapter.encode_stream(event_stream)
    return StreamingResponse(sse_stream, media_type=accept)
```

### Method Chain

| Method                  | Purpose                                |
| ----------------------- | -------------------------------------- |
| `build_run_input(body)` | Parse request body → `RequestData`     |
| `from_request(request)` | Build adapter from Starlette request   |
| `run_stream()`          | Run agent → Vercel AI events           |
| `run_stream_native()`   | Run agent → Pydantic AI events         |
| `transform_stream()`    | Convert Pydantic AI → Vercel AI events |
| `encode_stream()`       | Encode events as SSE strings           |
| `streaming_response()`  | Generate Starlette streaming response  |
| `dispatch_request()`    | All-in-one: request → response         |

### On Complete Callback

```python
async def on_complete(result: AgentRunResult):
    # Yield additional events after agent completes
    yield SomeVercelAIEvent(...)

return await VercelAIAdapter.dispatch_request(
    request,
    agent=agent,
    on_complete=on_complete,
)
```

---

## Common Patterns

### With Dependencies

```python
@app.post('/chat')
async def chat(request: Request) -> Response:
    deps = MyDeps(user_id=get_user_id(request))
    return await AGUIAdapter.dispatch_request(request, agent=agent, deps=deps)
```

### Error Handling

```python
from pydantic import ValidationError

@app.post('/chat')
async def chat(request: Request):
    try:
        run_input = VercelAIAdapter.build_run_input(await request.body())
    except ValidationError as e:
        return Response(
            content=json.dumps(e.json()),
            media_type='application/json',
            status_code=422,
        )
    # ... continue
```

### Mount ASGI App

```python
from fastapi import FastAPI
from pydantic_ai.ui.ag_ui.app import AGUIApp

main_app = FastAPI()
ag_ui_app = AGUIApp(agent)
main_app.mount('/agent', ag_ui_app)
```

---

## Key Classes

| Class              | Module                     | Purpose                          |
| ------------------ | -------------------------- | -------------------------------- |
| `AGUIAdapter`      | `pydantic_ai.ui.ag_ui`     | AG-UI protocol adapter           |
| `AGUIApp`          | `pydantic_ai.ui.ag_ui.app` | Stand-alone ASGI app             |
| `VercelAIAdapter`  | `pydantic_ai.ui.vercel_ai` | Vercel AI protocol adapter       |
| `StateDeps`        | `pydantic_ai.ui`           | Generic state container          |
| `ToolReturn`       | `pydantic_ai`              | Tool return with metadata/events |
| `SSE_CONTENT_TYPE` | `pydantic_ai.ui`           | `text/event-stream` constant     |
