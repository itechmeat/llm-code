# Pydantic Graph Reference

> pydantic-graph — async graph and state machine library for Python where nodes and edges are defined using type hints.

## Installation

```bash
pip install pydantic-graph
# Or included with pydantic-ai
pip install pydantic-ai
```

Note: `pydantic-graph` is required dependency of `pydantic-ai`, optional for `pydantic-ai-slim`.

## When to Use Graphs

Graphs are powerful but NOT for every job:

- Consider simpler multi-agent approaches first
- If not confident graph-based is needed — it's probably unnecessary
- Graphs are for advanced users with heavy generics/type hints usage

## Core Components

### GraphRunContext

Context for graph run, holds state and dependencies:

```python
from pydantic_graph import GraphRunContext

# Generic in StateT
async def run(self, ctx: GraphRunContext[MyState]) -> NextNode:
    ctx.state.counter += 1  # Access/mutate state
    return NextNode()
```

### End

Return value indicating graph run should end:

```python
from pydantic_graph import End

# Generic in RunEndT (return type)
return End(result_value)
```

### BaseNode

Subclass to define nodes. Nodes are dataclasses with:

1. Fields for parameters
2. Business logic in `run` method
3. Return annotations for outgoing edges

```python
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, GraphRunContext

@dataclass
class MyNode(BaseNode[StateT, DepsT, RunEndT]):
    """
    Generic parameters:
    - StateT: state type (default None)
    - DepsT: dependencies type (default None)
    - RunEndT: return type if returns End (default Never)
    """
    foo: int  # Node parameter

    async def run(
        self,
        ctx: GraphRunContext[StateT, DepsT],
    ) -> NextNode | End[RunEndT]:  # Return type = outgoing edges
        if self.foo % 5 == 0:
            return End(self.foo)
        return NextNode()
```

### Graph

Execution graph made of node classes:

```python
from pydantic_graph import Graph

# Generic in StateT, DepsT, RunEndT
my_graph = Graph(nodes=[NodeA, NodeB, NodeC])

# Run synchronously
result = my_graph.run_sync(StartNode(value=4))

# Run asynchronously
result = await my_graph.run(StartNode(), state=state, deps=deps)
```

## Complete Example

```python
from __future__ import annotations
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

@dataclass
class DivisibleBy5(BaseNode[None, None, int]):
    foo: int

    async def run(self, ctx: GraphRunContext) -> Increment | End[int]:
        if self.foo % 5 == 0:
            return End(self.foo)
        return Increment(self.foo)

@dataclass
class Increment(BaseNode):
    foo: int

    async def run(self, ctx: GraphRunContext) -> DivisibleBy5:
        return DivisibleBy5(self.foo + 1)

fives_graph = Graph(nodes=[DivisibleBy5, Increment])
result = fives_graph.run_sync(DivisibleBy5(4))
print(result.output)  # 5
```

## Stateful Graphs

State = object passed along and mutated by nodes:

```python
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

@dataclass
class MachineState:
    user_balance: float = 0.0
    product: str | None = None

@dataclass
class InsertCoin(BaseNode[MachineState]):
    async def run(self, ctx: GraphRunContext[MachineState]) -> CoinsInserted:
        amount = float(input('Insert coins: '))
        return CoinsInserted(amount)

@dataclass
class CoinsInserted(BaseNode[MachineState]):
    amount: float

    async def run(self, ctx: GraphRunContext[MachineState]) -> SelectProduct | Purchase:
        ctx.state.user_balance += self.amount  # Mutate state
        if ctx.state.product is not None:
            return Purchase(ctx.state.product)
        return SelectProduct()

# ... more nodes ...

async def main():
    state = MachineState()
    await vending_machine_graph.run(InsertCoin(), state=state)
```

## Iterating Over Graph

### Using `Graph.iter` with async for

```python
async with my_graph.iter(StartNode(), state=state) as run:
    async for node in run:
        print('Node:', node)
        # Node: StartNode()
        # Node: NextNode()
        # Node: End(data=result)
print('Final:', run.result.output)
```

### Manual iteration with `next()`

```python
async with my_graph.iter(StartNode(), state=state) as run:
    node = run.next_node
    while not isinstance(node, End):
        print('Node:', node)
        if some_condition:
            break  # Early exit possible
        node = await run.next(node)
```

## State Persistence

Allows interruption and resumption of graph runs.

### Built-in Implementations

| Class                    | Description                               |
| ------------------------ | ----------------------------------------- |
| `SimpleStatePersistence` | In-memory, latest snapshot only (default) |
| `FullStatePersistence`   | In-memory, full history                   |
| `FileStatePersistence`   | JSON file-based                           |

### Using FileStatePersistence

```python
from pathlib import Path
from pydantic_graph import End
from pydantic_graph.persistence.file import FileStatePersistence

async def main():
    persistence = FileStatePersistence(Path('graph_state.json'))

    # Initialize graph
    await my_graph.initialize(StartNode(), state=state, persistence=persistence)

    # Run from persistence (can be in separate process)
    async with my_graph.iter_from_persistence(persistence) as run:
        node_or_end = await run.next()
        if isinstance(node_or_end, End):
            print('Complete:', node_or_end.data)
```

### Human in the Loop Pattern

```python
# Run 1: Generate question
persistence = FileStatePersistence(Path('qa.json'))
if snapshot := await persistence.load_next():
    state = snapshot.state
    node = EvaluateAnswer(user_answer)
else:
    state = QuestionState()
    node = AskQuestion()

async with qa_graph.iter(node, state=state, persistence=persistence) as run:
    while True:
        node = await run.next()
        if isinstance(node, End):
            print('Correct!')
            break
        elif isinstance(node, WaitForAnswer):
            print(node.question)  # Wait for user input
            break
```

## Dependency Injection

```python
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
from pydantic_graph import BaseNode, GraphRunContext

@dataclass
class GraphDeps:
    executor: ProcessPoolExecutor

@dataclass
class MyNode(BaseNode[None, GraphDeps, int]):
    async def run(self, ctx: GraphRunContext[None, GraphDeps]) -> NextNode:
        # Use dependency
        result = await loop.run_in_executor(ctx.deps.executor, self.compute)
        return NextNode(result)

# Run with deps
with ProcessPoolExecutor() as executor:
    deps = GraphDeps(executor)
    result = await my_graph.run(StartNode(), deps=deps)
```

## Mermaid Diagrams

### Generate Diagram Code

```python
code = my_graph.mermaid_code(start_node=StartNode)
```

### Generate Image

```python
# Get image bytes
image = my_graph.mermaid_image(start_node=StartNode)

# Save to file
my_graph.mermaid_save(start_node=StartNode, path='diagram.png')
```

### Jupyter Display

```python
from IPython.display import Image, display
display(Image(my_graph.mermaid_image(start_node=StartNode)))
```

### Diagram Customization

```python
from typing import Annotated
from pydantic_graph import Edge, BaseNode

@dataclass
class Ask(BaseNode[State]):
    """Generate question using AI."""  # Note from docstring
    docstring_notes = True  # Enable docstring as note

    async def run(self, ctx: GraphRunContext[State]) -> Annotated[Answer, Edge(label='Ask the question')]:
        return Answer(question)

# Direction: 'TB' (top-bottom), 'LR' (left-right), 'RL', 'BT'
code = my_graph.mermaid_code(
    start_node=StartNode,
    direction='LR',
    highlighted_nodes=[CurrentNode]  # Highlight specific nodes
)
```

## GenAI Integration Example

```python
from pydantic_ai import Agent, format_as_xml
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

email_writer = Agent('openai:gpt-4o', output_type=Email)
feedback_agent = Agent('openai:gpt-4o', output_type=FeedbackResult)

@dataclass
class State:
    user: User
    messages: list[ModelMessage] = field(default_factory=list)

@dataclass
class WriteEmail(BaseNode[State]):
    feedback: str | None = None

    async def run(self, ctx: GraphRunContext[State]) -> ReviewEmail:
        result = await email_writer.run(
            f'Write email for: {format_as_xml(ctx.state.user)}',
            message_history=ctx.state.messages,
        )
        ctx.state.messages += result.new_messages()
        return ReviewEmail(result.output)

@dataclass
class ReviewEmail(BaseNode[State, None, Email]):
    email: Email

    async def run(self, ctx: GraphRunContext[State]) -> WriteEmail | End[Email]:
        result = await feedback_agent.run(format_as_xml(self.email))
        if result.output.needs_revision:
            return WriteEmail(feedback=result.output.feedback)
        return End(self.email)

email_graph = Graph(nodes=[WriteEmail, ReviewEmail])
result = await email_graph.run(WriteEmail(), state=State(user=user))
```

## Key Patterns

### Node Return Types Define Edges

```python
# Single edge
async def run(self, ctx) -> NextNode:
    return NextNode()

# Multiple possible edges (union)
async def run(self, ctx) -> NodeA | NodeB | End[int]:
    if condition_a:
        return NodeA()
    elif condition_b:
        return NodeB()
    return End(42)
```

### State vs Dependencies

| Aspect      | State                      | Dependencies                |
| ----------- | -------------------------- | --------------------------- |
| Mutability  | Mutable during run         | Read-only                   |
| Persistence | Saved in snapshots         | Not persisted               |
| Purpose     | Data flowing through graph | External resources          |
| Example     | `user_balance`, `messages` | `executor`, `db_connection` |

## Prohibitions

- ❌ Using graphs when simpler multi-agent approach works
- ❌ Forgetting generic parameters for End-returning nodes
- ❌ Returning node types not in return annotation
- ❌ Using state without passing to `graph.run()`
