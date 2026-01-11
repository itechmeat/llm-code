# Perplexity Pro Search

Advanced multi-step reasoning with built-in tools.

## Overview

Pro Search enables complex research queries with:

- Multi-step reasoning visible in responses
- Built-in tools: `web_search`, `fetch_url_content`
- Automatic tool orchestration (no configuration needed)

## Basic Usage

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Research solar panel ROI for California homes"}],
    search_type="pro",  # "pro", "fast", or "auto"
    stream=True  # REQUIRED for Pro Search
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
```

## Search Types

| Type | Description               | Use Case                     |
| ---- | ------------------------- | ---------------------------- |
| pro  | Full multi-step reasoning | Complex research, reports    |
| fast | Quick search, fewer steps | Simple queries, speed needed |
| auto | AI decides                | Mixed workloads              |

## CRITICAL: Streaming Required

Pro Search **REQUIRES** `stream=True`. Non-streaming requests will fail.

```python
# ✅ CORRECT
completion = client.chat.completions.create(
    model="sonar-pro",
    search_type="pro",
    stream=True,
    messages=[...]
)

# ❌ WRONG - will fail
completion = client.chat.completions.create(
    model="sonar-pro",
    search_type="pro",
    stream=False,  # Pro Search doesn't support this
    messages=[...]
)
```

## Built-in Tools

Pro Search automatically uses two tools:

### web_search

Conducts web searches for current information.

```json
{
  "thought": "I need current EV market data",
  "type": "web_search",
  "web_search": {
    "search_keywords": ["EV Statistics 2024", "electric vehicle sales"],
    "search_results": [
      {
        "title": "Trends in electric cars",
        "url": "https://www.iea.org/...",
        "date": "2024-03-15",
        "snippet": "Electric car sales neared 14 million...",
        "source": "web"
      }
    ]
  }
}
```

### fetch_url_content

Retrieves full content from specific URLs.

```json
{
  "thought": "This paper has detailed methodology I need",
  "type": "fetch_url_content",
  "fetch_url_content": {
    "contents": [
      {
        "title": "Research Paper Title",
        "url": "https://arxiv.org/pdf/...",
        "snippet": "The dominant sequence transduction models..."
      }
    ]
  }
}
```

## Multi-Tool Workflows

Pro Search automatically chains tools:

1. **User asks**: "Research solar panel options for California homes"
2. **web_search** → finds incentives and costs
3. **fetch_url_content** → reads policy documents
4. **web_search** → verifies electricity rates

## Reasoning Steps

Access tool executions in `reasoning_steps`:

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    search_type="pro",
    stream=True,
    messages=[{"role": "user", "content": "AI startup funding 2024"}]
)

full_response = ""
reasoning_steps = []

for chunk in completion:
    if chunk.choices[0].delta.content:
        full_response += chunk.choices[0].delta.content

    # Collect reasoning steps from streaming response
    if hasattr(chunk, 'reasoning_steps'):
        reasoning_steps.extend(chunk.reasoning_steps)

print("Final answer:", full_response)
print("Research steps:", reasoning_steps)
```

## Pricing

| Search Type | Per 1K Requests |
| ----------- | --------------- |
| Pro Search  | $14–$22         |
| Fast Search | $6–$14          |

Prices vary by search context size (Low/Medium/High).

## Pro Search vs Standard Sonar Pro

| Feature          | Standard Sonar Pro | Pro Search   |
| ---------------- | ------------------ | ------------ |
| Model            | sonar-pro          | sonar-pro    |
| Streaming        | Optional           | **Required** |
| Multi-step       | No                 | Yes          |
| Tool visibility  | No                 | Yes          |
| Complex research | Limited            | Excellent    |
| Cost             | Lower              | Higher       |

## Best Practices

### Use Pro Search When

- Complex, multi-step research needed
- Want visibility into search process
- Building research/analysis tools
- Need comprehensive answers

### Use Standard Search When

- Simple factual queries
- Speed is priority
- Cost-sensitive applications
- Don't need reasoning visibility

### Combine with Filters

```python
completion = client.chat.completions.create(
    model="sonar-pro",
    search_type="pro",
    stream=True,
    messages=[{"role": "user", "content": "Latest AI research papers"}],
    search_domain_filter=["arxiv.org", "nature.com"],
    search_recency_filter="month"
)
```

## Error Handling

```python
from perplexity import BadRequestError

try:
    completion = client.chat.completions.create(
        model="sonar-pro",
        search_type="pro",
        stream=False,  # This will fail
        messages=[...]
    )
except BadRequestError as e:
    if "stream" in str(e).lower():
        print("Pro Search requires stream=True")
```

## sonar-deep-research

For exhaustive research, use `sonar-deep-research`:

```python
# Deep research is async-only
async def deep_research():
    async with AsyncPerplexity() as client:
        completion = await client.chat.completions.create(
            model="sonar-deep-research",
            messages=[{"role": "user", "content": "Comprehensive analysis of..."}],
            stream=True
        )
        async for chunk in completion:
            print(chunk.choices[0].delta.content or "", end="")
```

### Deep Research Limitations

- **Async only** — use `AsyncPerplexity`
- **No image input** — doesn't support image attachments
- **Longer response time** — can take minutes
- **Highest cost** — use sparingly
