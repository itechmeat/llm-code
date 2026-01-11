# Perplexity Prompting Guide

Best practices for prompting web-search models.

## System vs User Prompt

### System Prompt

- Controls style, tone, language of response
- **NOT used** by real-time search component
- Good for formatting instructions

```python
messages=[
    {
        "role": "system",
        "content": """You are a helpful AI assistant.
Rules:
1. Provide only the final answer without explaining steps.
2. Format as a list if multiple items."""
    },
    {"role": "user", "content": "Best sushi restaurants in Tokyo"}
]
```

### User Prompt

- Used to kick off real-time web search
- Should contain the actual query
- Be specific and contextual

## Key Differences from Traditional LLMs

Web search models behave differently from standard LLMs:

| Aspect              | Traditional LLM        | Perplexity Web Search         |
| ------------------- | ---------------------- | ----------------------------- |
| Few-shot prompting  | Works well             | **Avoid** — confuses search   |
| Generic questions   | Often acceptable       | **Too broad** — poor results  |
| Multi-part requests | Handled reasonably     | **Break apart** — one topic   |
| URL requests        | Can hallucinate anyway | **Never ask** — use citations |

## Best Practices

### Be Specific

```python
# ✅ GOOD - specific context
"Explain recent advances in climate prediction models for urban planning"

# ❌ BAD - too generic
"Tell me about climate models"
```

### Avoid Few-Shot Prompting

```python
# ✅ GOOD
"Summarize current research on mRNA vaccine technology"

# ❌ BAD - examples confuse search
"Here's an example summary: [example]. Now summarize mRNA vaccines."
```

### Use Search-Friendly Terms

```python
# ✅ GOOD - terms experts would use
"Compare energy efficiency ratings of heat pumps vs traditional HVAC for residential use"

# ❌ BAD - vague
"Tell me which home heating is better"
```

### One Topic Per Query

```python
# ✅ GOOD
"Explain quantum computing principles that might impact cryptography in the next decade"

# ❌ BAD - multiple unrelated topics
"Explain quantum computing, regenerative agriculture, and stock market predictions"
```

## Handling URLs and Sources

### NEVER ask for URLs in prompts

The model cannot see actual URLs from search and will **hallucinate** them.

```python
# ❌ WRONG - URLs will be hallucinated
messages=[{
    "role": "user",
    "content": "Find Canadian news. For each, include headline, summary, and source link."
}]

# ✅ CORRECT - get URLs from response metadata
messages=[{
    "role": "user",
    "content": "Find Canadian news. For each, include headline and why it matters."
}]

# Then access URLs from search_results field in response
for citation in completion.citations:
    print(f"Source: {citation.url}")
```

### Use Citations Field

URLs are in `search_results` / `citations`:

```python
completion = client.chat.completions.create(...)

# Access accurate sources
for citation in completion.citations:
    print(f"{citation.title}: {citation.url}")
```

## Preventing Hallucination

### Set Clear Boundaries

```python
messages=[{
    "role": "user",
    "content": """Search for renewable energy developments.
If you cannot find relevant information, state that clearly
rather than providing speculative information."""
}]
```

### Request Source Transparency

```python
messages=[{
    "role": "user",
    "content": """Find Tesla's latest earnings report.
Only provide information from your search results.
Clearly state if certain details are not available."""
}]
```

### Avoid Inaccessible Sources

These often lead to hallucination:

- LinkedIn posts (private/auth required)
- Paywalled content
- Private documents
- Very recent unindexed content

## Use API Parameters, Not Prompts

### DON'T control search via prompts

```python
# ❌ INEFFECTIVE
messages=[{
    "role": "user",
    "content": "Search only Wikipedia for climate change. Only use sources from past month."
}]
```

### DO use built-in parameters

```python
# ✅ EFFECTIVE
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Climate change policies"}],
    search_domain_filter=["wikipedia.org"],
    search_recency_filter="month"
)
```

## Query Type Tips

| Query Type       | Best Practices                                         |
| ---------------- | ------------------------------------------------------ |
| Factual Research | Use domain filters, high search context                |
| Creative Content | Style guidelines in system prompt, disable_search=True |
| Technical        | Include language/framework, use docs domains           |
| Analysis         | Request step-by-step reasoning                         |

## Examples

### Technical Documentation

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "FastAPI dependency injection patterns"}],
    search_domain_filter=["fastapi.tiangolo.com", "docs.python.org"],
    web_search_options={"search_context_size": "medium"}
)
```

### Current Events

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": "Latest AI policy developments in European Union this week"
    }],
    search_recency_filter="week"
)
```

### Creative (No Search)

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[
        {"role": "system", "content": "You are a creative writing assistant."},
        {"role": "user", "content": "Write a short sci-fi story about time travel"}
    ],
    disable_search=True,
    temperature=0.8
)
```

## Parameter Recommendations

- **Do NOT tune** `temperature` — defaults are optimized
- **Do use** `search_domain_filter` for trusted sources
- **Do use** `search_context_size` appropriately:
  - `low` — simple facts
  - `medium` — general use (default)
  - `high` — comprehensive research
