# Pydantic Evals Reference

Evaluation framework for testing AI systems.

## Installation

```bash
pip install pydantic-evals

# With Logfire integration
pip install 'pydantic-evals[logfire]'
```

## Data Model

```
Dataset (1) ──── (Many) Case
│                │
└── (Many) Experiment ──┴── (Many) Case results
    │
    └── (1) Task
    │
    └── (Many) Evaluator
```

| Concept        | Description                                       |
| -------------- | ------------------------------------------------- |
| **Dataset**    | Collection of test cases                          |
| **Case**       | Single test scenario with inputs/expected outputs |
| **Evaluator**  | Scores task outputs                               |
| **Experiment** | Run dataset against a task                        |

## Basic Usage

### Define Cases

```python
from pydantic_evals import Case, Dataset

case = Case(
    name='capital_france',
    inputs='What is the capital of France?',
    expected_output='Paris',
    metadata={'difficulty': 'easy'},
)

dataset = Dataset(cases=[case])
```

### Define Task

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

async def my_task(question: str) -> str:
    result = await agent.run(question)
    return result.output
```

### Run Evaluation

```python
report = dataset.evaluate_sync(my_task)
report.print(include_input=True, include_output=True)
```

## Built-in Evaluators

| Evaluator    | Purpose              |
| ------------ | -------------------- |
| `IsInstance` | Check output type    |
| `ExactMatch` | Exact string match   |
| `Contains`   | Substring check      |
| `Regex`      | Regex pattern match  |
| `LLMJudge`   | LLM-based evaluation |

`Contains` supports `pydantic.BaseModel` outputs (v1.59.0).

```python
from pydantic_evals.evaluators import IsInstance, ExactMatch

dataset = Dataset(
    cases=[case],
    evaluators=[
        IsInstance(type_name='str'),
        ExactMatch(),
    ],
)
```

## Custom Evaluators

```python
from dataclasses import dataclass
from pydantic_evals.evaluators import Evaluator, EvaluatorContext

@dataclass
class MyEvaluator(Evaluator[str, str]):
    async def evaluate(self, ctx: EvaluatorContext[str, str]) -> float:
        output = ctx.output
        expected = ctx.expected_output

        if output == expected:
            return 1.0
        elif expected.lower() in output.lower():
            return 0.8
        return 0.0
```

## LLM Judge

Use LLM to evaluate subjective qualities:

```python
from pydantic_evals.evaluators import LLMJudge

judge = LLMJudge(
    model='openai:gpt-4o',
    criteria='Is the response accurate, helpful, and well-formatted?',
)

dataset = Dataset(cases=[case], evaluators=[judge])
```

## Case-Specific Evaluators

```python
case = Case(
    name='math_case',
    inputs='What is 2+2?',
    expected_output='4',
    evaluators=[ExactMatch()],  # Only for this case
)
```

## Dataset from YAML

```yaml
# dataset.yaml
cases:
  - name: capital_france
    inputs: "What is the capital of France?"
    expected_output: "Paris"
  - name: capital_japan
    inputs: "What is the capital of Japan?"
    expected_output: "Tokyo"
```

```python
from pydantic_evals import Dataset

dataset = Dataset.from_yaml('dataset.yaml')
```

## Report Output

```python
report = dataset.evaluate_sync(my_task)

# Print to console
report.print()

# Access results
for case_result in report.case_results:
    print(f"{case_result.name}: {case_result.scores}")

# Export
report.to_json('results.json')
```

## Logfire Integration

```python
import logfire

logfire.configure()

# Results auto-appear in Logfire dashboard
report = dataset.evaluate_sync(my_task)
```

## Span-Based Evaluation

Evaluate internal agent behavior (tool calls, execution flow):

```python
from pydantic_evals.evaluators import SpanEvaluator

class ToolCallEvaluator(SpanEvaluator):
    async def evaluate_spans(self, spans: list[Span]) -> float:
        tool_calls = [s for s in spans if s.name.startswith('tool:')]
        return 1.0 if len(tool_calls) <= 3 else 0.5
```

## Concurrency

```python
# Control parallel execution
report = dataset.evaluate_sync(
    my_task,
    max_concurrency=5,
)
```

## Retry Strategies

```python
from pydantic_evals import RetryConfig

report = dataset.evaluate_sync(
    my_task,
    retry_config=RetryConfig(
        max_retries=3,
        backoff_multiplier=2.0,
    ),
)
```

## Best Practices

1. **Start simple** — Begin with exact match, add complex evaluators as needed
2. **Use metadata** — Tag cases with difficulty, category for analysis
3. **Combine evaluators** — Use deterministic + LLM-based together
4. **Version datasets** — Track dataset changes over time
5. **Integrate Logfire** — Visualize results and compare runs
