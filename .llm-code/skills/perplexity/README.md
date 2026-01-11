# Perplexity Skill

Agent skill for integrating Perplexity API — web-grounded AI responses and real-time search.

## Overview

Perplexity provides two main APIs:

- **Chat Completions** — AI responses grounded in web data (Sonar models)
- **Search API** — Ranked web search results with advanced filtering

## Quick Start

```python
from perplexity import Perplexity

client = Perplexity()  # Uses PERPLEXITY_API_KEY env var

# Chat completion
completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Latest AI news"}]
)

# Search
search = client.search.create(query="AI trends 2024", max_results=5)
```

## Models

| Model                 | Use Case                  |
| --------------------- | ------------------------- |
| `sonar`               | Quick facts, simple Q&A   |
| `sonar-pro`           | Complex queries, research |
| `sonar-reasoning-pro` | Multi-step reasoning      |
| `sonar-deep-research` | Comprehensive reports     |

## Files

- `SKILL.md` — Main instructions and recipes
- `references/models.md` — Model details and pricing
- `references/search-api.md` — Search API patterns
- `references/chat-completions.md` — Chat API guide
- `references/structured-outputs.md` — JSON schema responses

## Links

- [Perplexity API Docs](https://docs.perplexity.ai/)
- [Python SDK](https://pypi.org/project/perplexityai/)
- [TypeScript SDK](https://www.npmjs.com/package/@perplexityai/perplexity)
