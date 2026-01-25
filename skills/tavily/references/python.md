# Tavily Python SDK Reference

## Installation

```bash
pip install tavily-python
```

## Client Setup

### Synchronous Client

```python
from tavily import TavilyClient

# From environment variable TAVILY_API_KEY
client = TavilyClient()

# Explicit key
client = TavilyClient(api_key="tvly-YOUR_API_KEY")

# With proxy
client = TavilyClient(
    api_key="tvly-YOUR_API_KEY",
    proxies={
        "http://": "http://proxy.example.com:8080",
        "https://": "http://proxy.example.com:8080"
    }
)
```

### Async Client

```python
from tavily import AsyncTavilyClient

client = AsyncTavilyClient()
response = await client.search("query")
```

---

## search()

```python
response = client.search(
    query="string",                    # Required

    # Search behavior
    search_depth="basic",              # "basic"|"advanced"|"fast"|"ultra-fast"
    topic="general",                   # "general"|"news"|"finance"
    auto_parameters=False,             # Auto-configure based on query

    # Time filtering
    time_range="day",                  # "day"|"week"|"month"|"year"
    start_date="2024-01-01",           # YYYY-MM-DD format
    end_date="2024-12-31",             # YYYY-MM-DD format

    # Results configuration
    max_results=5,                     # 0-20
    chunks_per_source=3,               # 1-3, requires search_depth="advanced"

    # Content options
    include_answer=False,              # True|"basic"|"advanced"
    include_raw_content=False,         # True|"markdown"|"text"
    include_images=False,
    include_image_descriptions=False,
    include_favicon=False,

    # Domain filtering
    include_domains=["example.com"],   # Max 300
    exclude_domains=["spam.com"],      # Max 150

    # Regional
    country="US",                      # Boost results from country

    # Usage tracking
    include_usage=False
)
```

### Response Structure

```python
{
    "query": str,
    "answer": str | None,
    "results": [
        {
            "title": str,
            "url": str,
            "content": str,
            "score": float,
            "raw_content": str | None,
            "published_date": str | None,
            "favicon": str | None
        }
    ],
    "images": [{"url": str, "description": str}],
    "response_time": float,
    "usage": {"credits": int} | None,
    "request_id": str
}
```

---

## extract()

```python
response = client.extract(
    urls="https://example.com",        # String or list of URLs (max 20)

    # Extraction options
    extract_depth="basic",             # "basic"|"advanced"
    format="markdown",                 # "markdown"|"text"
    include_images=False,
    include_favicon=False,

    # Relevance filtering
    query="specific question",         # Rerank chunks by relevance
    chunks_per_source=3,               # 1-5, requires query

    # Timing
    timeout=30,                        # 1-60 seconds

    include_usage=False
)
```

### Response Structure

```python
{
    "results": [
        {
            "url": str,
            "raw_content": str,
            "images": [str] | None,
            "favicon": str | None
        }
    ],
    "failed_results": [
        {"url": str, "error": str}
    ],
    "response_time": float,
    "usage": {"credits": int} | None,
    "request_id": str
}
```

---

## crawl()

```python
response = client.crawl(
    url="https://example.com",         # Required: starting URL

    # Scope control
    max_depth=1,                       # 1-5 levels
    max_breadth=20,                    # Links per page
    limit=50,                          # Total pages

    # AI guidance (doubles credit cost)
    instructions="Focus on API docs",

    # Path filtering (regex patterns)
    select_paths=["/docs/.*"],         # Only crawl matching paths
    exclude_paths=["/private/.*"],     # Skip matching paths

    # Domain filtering (regex patterns)
    select_domains=["example\\.com"],
    exclude_domains=["ads\\..*"],
    allow_external=True,               # Follow external links

    # Extraction options
    extract_depth="basic",             # "basic"|"advanced"
    format="markdown",                 # "markdown"|"text"
    include_images=False,
    include_favicon=False,
    chunks_per_source=3,               # 1-5, with instructions

    # Timing
    timeout=150,                       # 10-150 seconds

    include_usage=False
)
```

### Response Structure

```python
{
    "base_url": str,
    "results": [
        {
            "url": str,
            "raw_content": str,
            "images": [str] | None,
            "favicon": str | None
        }
    ],
    "response_time": float,
    "usage": {"credits": int} | None,
    "request_id": str
}
```

---

## map()

```python
response = client.map(
    url="https://example.com",         # Required: starting URL

    # Scope control
    max_depth=1,                       # 1-5 levels
    max_breadth=20,                    # Links per page
    limit=50,                          # Total URLs

    # AI guidance (doubles credit cost)
    instructions="Find all API endpoints",

    # Path filtering (regex patterns)
    select_paths=["/api/.*"],
    exclude_paths=["/internal/.*"],

    # Domain filtering (regex patterns)
    select_domains=["api\\.example\\.com"],
    exclude_domains=["beta\\..*"],
    allow_external=True,

    # Timing
    timeout=150,                       # 10-150 seconds

    include_usage=False
)
```

### Response Structure

```python
{
    "base_url": str,
    "results": [str],                  # List of URLs (no content)
    "response_time": float,
    "usage": {"credits": int} | None,
    "request_id": str
}
```

---

## TavilyHybridClient (RAG Integration)

For MongoDB-based hybrid RAG with Tavily web search.

```python
from tavily import TavilyHybridClient

client = TavilyHybridClient(
    api_key="tvly-YOUR_API_KEY",
    db_provider="mongodb",
    collection=mongo_collection,       # pymongo Collection object
    index="vector_index",              # Atlas Search index name
    embeddings_field="embeddings",     # Field with vectors
    content_field="content"            # Field with text
)

# Search combining local DB + web
results = client.search(
    query="What is machine learning?",
    max_results=5,
    max_local=3,                       # From MongoDB
    max_foreign=2                      # From Tavily web search
)
```

### Custom Embedding Function

```python
import cohere

co = cohere.Client("cohere-api-key")

def my_embeddings(texts: list[str]) -> list[list[float]]:
    response = co.embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type="search_document"
    )
    return response.embeddings

client = TavilyHybridClient(
    ...,
    embedding_function=my_embeddings
)
```

### Custom Ranking Function

```python
def my_ranker(query: str, documents: list[str], top_n: int) -> list[dict]:
    response = co.rerank(
        query=query,
        documents=documents,
        model="rerank-english-v2.0",
        top_n=top_n
    )
    return [{"index": r.index, "score": r.relevance_score} for r in response.results]

client = TavilyHybridClient(
    ...,
    ranking_function=my_ranker
)
```

### Save Web Results to DB

```python
results = client.search(
    query="latest AI news",
    save_foreign=True                  # Cache web results in MongoDB
)
```

---

## Error Handling

```python
from tavily import TavilyClient
from tavily.errors import (
    InvalidAPIKeyError,
    UsageLimitExceededError,
    MissingAPIKeyError
)

try:
    response = client.search("query")
except InvalidAPIKeyError:
    print("Invalid API key")
except UsageLimitExceededError:
    print("Credit limit reached")
except MissingAPIKeyError:
    print("No API key provided")
except Exception as e:
    print(f"Request failed: {e}")
```

---

## Best Practices

```python
# ✅ Use async for high throughput
async def batch_search(queries: list[str]):
    client = AsyncTavilyClient()
    tasks = [client.search(q) for q in queries]
    return await asyncio.gather(*tasks)

# ✅ Filter domains for quality
response = client.search(
    query="python tutorials",
    include_domains=["python.org", "realpython.com"],
    exclude_domains=["medium.com"]
)

# ✅ Use auto_parameters for unknown query types
response = client.search(
    query=user_input,
    auto_parameters=True
)

# ✅ Get structured answers for RAG
response = client.search(
    query="What is quantum computing?",
    include_answer="advanced",
    include_raw_content="markdown"
)
```
