# Search API Reference

Real-time ranked web search results with advanced filtering.

## Basic Search

```python
from perplexity import Perplexity

client = Perplexity()

search = client.search.create(
    query="latest AI developments 2024",
    max_results=5,
    max_tokens_per_page=2048
)

for result in search.results:
    print(f"{result.title}: {result.url}")
    print(f"Snippet: {result.snippet[:200]}...")
    print(f"Date: {result.date}")
```

## Response Structure

```json
{
  "results": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "snippet": "Content excerpt...",
      "date": "2024-01-15",
      "last_updated": "2024-01-20"
    }
  ],
  "id": "request-uuid"
}
```

## Parameters

| Parameter                | Type        | Default  | Description                            |
| ------------------------ | ----------- | -------- | -------------------------------------- |
| `query`                  | string/list | required | Search query (up to 5 for multi-query) |
| `max_results`            | int         | 10       | Results per query (1-20)               |
| `max_tokens_per_page`    | int         | 2048     | Content extraction per page            |
| `max_tokens`             | int         | 25000    | Total content budget (max 1M)          |
| `country`                | string      | -        | ISO 3166-1 alpha-2 code                |
| `search_domain_filter`   | list        | -        | Domain allow/denylist (max 20)         |
| `search_language_filter` | list        | -        | ISO 639-1 codes (max 10)               |

## Regional Search

```python
search = client.search.create(
    query="government renewable energy policies",
    country="US",  # ISO country code
    max_results=5
)
```

Common codes: `US`, `GB`, `DE`, `JP`, `FR`, `CA`, `AU`

## Multi-Query Search

Execute up to 5 queries in single request:

```python
search = client.search.create(
    query=[
        "artificial intelligence trends 2024",
        "machine learning breakthroughs recent",
        "AI applications in healthcare"
    ],
    max_results=5
)

# Results grouped by query
for i, query_results in enumerate(search.results):
    print(f"Query {i+1}:")
    for result in query_results:
        print(f"  {result.title}")
```

**Note:** Single query returns flat list; multi-query returns nested lists.

## Domain Filtering

### Allowlist Mode (include only)

```python
search = client.search.create(
    query="climate change research",
    search_domain_filter=[
        "science.org",
        "nature.com",
        "pnas.org"
    ]
)
```

### Denylist Mode (exclude)

```python
search = client.search.create(
    query="renewable energy innovations",
    search_domain_filter=[
        "-pinterest.com",
        "-reddit.com",
        "-quora.com"
    ]
)
```

**Rules:**

- Max 20 domains per filter
- Cannot mix allowlist and denylist in same request
- Prefix with `-` for denylist

## Language Filtering

```python
search = client.search.create(
    query="latest AI news",
    search_language_filter=["en", "fr", "de"],
    max_results=10
)
```

Max 10 language codes per request.

## Content Extraction Control

```python
# Comprehensive extraction (slower)
detailed = client.search.create(
    query="AI research methodology",
    max_results=5,
    max_tokens_per_page=2048,
    max_tokens=50000
)

# Quick extraction (faster)
brief = client.search.create(
    query="AI news headlines",
    max_results=10,
    max_tokens_per_page=512,
    max_tokens=5000
)
```

**Recommendations:**

- `max_tokens_per_page`: 256-512 for quick retrieval
- `max_tokens_per_page`: 2048+ for deep analysis
- Lower values = faster processing

## Async Search

```python
import asyncio
from perplexity import AsyncPerplexity

async def batch_search(queries, batch_size=3, delay_ms=1000):
    async with AsyncPerplexity() as client:
        results = []

        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            tasks = [
                client.search.create(query=q, max_results=5)
                for q in batch
            ]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            if i + batch_size < len(queries):
                await asyncio.sleep(delay_ms / 1000)

        return results
```

## Rate-Limited Concurrent Search

```python
import asyncio
from perplexity import AsyncPerplexity

class SearchManager:
    def __init__(self, max_concurrent=5):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def search_single(self, client, query):
        async with self.semaphore:
            return await client.search.create(query=query, max_results=5)

    async def search_many(self, queries):
        async with AsyncPerplexity() as client:
            tasks = [self.search_single(client, q) for q in queries]
            return await asyncio.gather(*tasks, return_exceptions=True)
```

## Caching Pattern

```python
import time
from typing import Dict, Tuple, Optional

class SearchCache:
    def __init__(self, ttl_seconds=3600):
        self.cache: Dict[str, Tuple[any, float]] = {}
        self.ttl = ttl_seconds

    def get(self, query: str) -> Optional[any]:
        if query in self.cache:
            result, timestamp = self.cache[query]
            if time.time() - timestamp < self.ttl:
                return result
            del self.cache[query]
        return None

    def set(self, query: str, result: any):
        self.cache[query] = (result, time.time())

# Usage
cache = SearchCache(ttl_seconds=1800)

def cached_search(client, query):
    cached = cache.get(query)
    if cached:
        return cached
    result = client.search.create(query=query)
    cache.set(query, result)
    return result
```

## Error Handling

```python
from perplexity import RateLimitError, APIStatusError

def resilient_search(client, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.search.create(query=query)
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
        except APIStatusError as e:
            print(f"API error: {e}")
            return None
```

## Best Practices

1. **Be specific:** "AI medical diagnosis accuracy 2024" > "AI medical"
2. **Use multi-query:** Break research into related sub-queries
3. **Request only needed results:** More results = longer response
4. **Cache static queries:** Don't repeat unchanged searches
5. **Implement backoff:** Handle rate limits gracefully
