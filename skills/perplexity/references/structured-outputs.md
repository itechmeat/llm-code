# Structured Outputs Reference

Enforce JSON response formats using JSON Schema.

## Basic Usage

```python
from perplexity import Perplexity
from pydantic import BaseModel

class ContactInfo(BaseModel):
    email: str
    phone: str

client = Perplexity()

completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Find Tesla IR contact info"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "schema": ContactInfo.model_json_schema()
        }
    }
)

contact = ContactInfo.model_validate_json(completion.choices[0].message.content)
print(f"Email: {contact.email}")
```

## Response Format Structure

```json
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "schema": {
        /* your JSON schema */
      }
    }
  }
}
```

## Financial Analysis Example

```python
from typing import List, Optional
from pydantic import BaseModel

class FinancialMetrics(BaseModel):
    company: str
    quarter: str
    revenue: float
    net_income: float
    eps: float
    revenue_growth_yoy: Optional[float] = None
    key_highlights: Optional[List[str]] = None

completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": "Analyze Apple's latest quarterly earnings. Extract key metrics."
    }],
    response_format={
        "type": "json_schema",
        "json_schema": {"schema": FinancialMetrics.model_json_schema()}
    }
)

metrics = FinancialMetrics.model_validate_json(
    completion.choices[0].message.content
)
print(f"Revenue: ${metrics.revenue}B")
```

## Perplexity vs Other Providers

**Simplified syntax** — no `name` or `strict` fields required:

```json
// Other providers
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "my_schema",
      "strict": true,
      "schema": { ... }
    }
  }
}

// Perplexity
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "schema": { ... }
    }
  }
}
```

## Reasoning Models

With `sonar-reasoning-pro`, response includes `<think>` section:

```
<think>
I need to provide information about France...
Let me format this information as required.
</think>
{"country":"France","capital":"Paris","population":67750000}
```

**Parse manually** to extract JSON after `</think>`.

## Cold Start Warning

**First request with new schema takes 10-30 seconds** to prepare.

- May cause timeout errors on first call
- Subsequent requests with same schema are fast
- Consider pre-warming schemas in production

## Improve Compliance

Add hints in prompts:

```python
messages = [{
    "role": "user",
    "content": """Find the contact information for Apple investor relations.
    Return as JSON with email and phone fields."""
}]
```

## Unsupported Schemas

```python
# ❌ UNSUPPORTED: Recursive schema
class RecursiveJson(BaseModel):
    value: str
    child: list["RecursiveJson"]

# ❌ UNSUPPORTED: Unconstrained dict
from typing import Any

class UnconstrainedDict(BaseModel):
    data: dict[str, Any]
```

## Links in JSON Responses

**Do NOT request links in JSON structured outputs.**

- May result in hallucinations or broken URLs
- Use `citations` or `search_results` from API response instead

```python
# ❌ BAD: Links in schema
class ResultWithLink(BaseModel):
    title: str
    url: str  # May be hallucinated

# ✅ GOOD: Get links from citations
completion = client.chat.completions.create(...)
citations = completion.citations  # Valid URLs
```

## Best Practices

1. **Use Pydantic** — Generate schemas with `model_json_schema()`
2. **Keep schemas simple** — Avoid deep nesting
3. **No recursion** — Flatten recursive structures
4. **Type everything** — Use specific types, not `Any`
5. **Pre-warm schemas** — First request is slow
6. **Get links from citations** — Don't request URLs in JSON
7. **Add prompt hints** — Improve schema compliance
