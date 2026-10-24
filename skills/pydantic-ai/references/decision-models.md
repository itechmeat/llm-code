# Decision Models and Type-Safe Output

`TypeSafeModel` gives a model a fixed set of allowed answers. `DecisionModel` (`2.50.0`) generalizes it: instead of one flat choice list, the model answers **several questions at once** and the framework picks the route from those answers.

## TypeSafeModel - one question, fixed options

```python
from pydantic_ai import TypeSafeModel
from pydantic_ai.types import BoolCriteria, Choice

class Route(TypeSafeModel):
    category: Choice[str, ['billing', 'technical', 'other']]
    urgent: BoolCriteria
```

- `Choice` restricts a field to a fixed set of values.
- `BoolCriteria` (`2.49.0`) is the boolean-field equivalent of `Choice`: the model must answer yes or no explicitly, and the answer is typed rather than free text. A plain `True`/`False` Enum does the same thing.
- `2.49.0` added a **"none of these"** semantic to `TypeSafeModel`, so a model that cannot map the input to any option can say so instead of picking the closest one.
- `2.49.0` also allows **whole-number `Choice` options** - a numeric choice list, not only strings.

## DecisionModel - several questions, one route

```python
from pydantic_ai import DecisionModel

class Triage(DecisionModel):
    is_billing: BoolCriteria
    is_technical: BoolCriteria
    needs_human: BoolCriteria
```

The model answers all questions in one shot, and the framework derives the route from the answers:

- **Route fields** mark which fields decide the route.
- `decision_route_threshold` (`2.50.0`) sets how confident the route must be before it is used; below the threshold the agent falls back.
- `ModelSelectionContext.prompt` (`2.50.0`) gives the model the prompt that describes the decision it is making.
- `RunContext.in_durable_context` (`2.50.0`) marks a run as durable, which changes how decisions are recorded for replay.

## Where it fits

- **Routing** - pick a downstream model or pipeline from the decision instead of a string match on the output.
- **Structured triage** - a single LLM call answers "is this billing?", "is this technical?", "does this need a human?" instead of three separate calls.
- **Typed tool results** - the same typed-output machinery works for tool return values.

## Dynamic instruction prefixes

`2.59.0` added `on_change='append'` for dynamic instruction prefixes: when an agent's instructions change mid-run, the new text is appended rather than replacing the accumulated instruction history.

```python
agent = Agent(
    'openai:gpt-5',
    instructions=build_instructions,
    inst_dynamic_callable=...,
)
```

`FunctionToolset.instructions` can opt into the same `on_change='append'` behavior, so a toolset can contribute instructions that accumulate across calls rather than overwriting each other.

## Practical notes

- A decision model is only as good as its route fields - name them for the decision you actually want to make, not for the questions you happen to ask.
- Set `decision_route_threshold` deliberately: a low threshold routes on weak answers.
- "None of these" is a feature; make sure downstream code handles it instead of assuming a route was always chosen.
- `BoolCriteria` beats a free-text yes/no: it cannot be mis-parsed.
