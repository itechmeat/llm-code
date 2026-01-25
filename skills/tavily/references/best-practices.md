# Tavily Best Practices

## Search Best Practices

### Query Optimization

- **Keep queries under 400 characters** — concise, agent-style queries work best
- **Break complex queries into sub-queries** — separate focused requests for multi-topic research

```python
# ✅ Good: focused queries
client.search("Competitors of company ABC")
client.search("Financial performance of company ABC")
client.search("Recent developments of company ABC")

# ❌ Bad: one massive multi-topic query
```

### Search Depth Selection

| Depth      | Latency | Relevance | Content Type | Best For                       |
| ---------- | ------- | --------- | ------------ | ------------------------------ |
| ultra-fast | Lowest  | Lower     | Content      | Real-time apps, speed critical |
| fast       | Low     | Good      | Chunks       | Quick targeted snippets        |
| basic      | Medium  | High      | Content      | General-purpose searches       |
| advanced   | Higher  | Highest   | Chunks       | Specific, detailed info        |

**Content Types:**

- **Content** — NLP-based page summary (general context)
- **Chunks** — Short snippets reranked by query relevance

### Time Filtering

```python
# Relative time range
client.search("latest ML trends", time_range="month")

# Specific date range
client.search("AI news", start_date="2025-01-01", end_date="2025-02-01")
```

### Domain Filtering

```python
# Restrict to specific domains
client.search("CEO background at Google", include_domains=["linkedin.com/in"])

# Exclude irrelevant domains
client.search("US economy", exclude_domains=["espn.com", "vogue.com"])

# Boost country results
client.search("tech startup funding", country="united states")

# Wildcard patterns
client.search("AI news", include_domains=["*.com"], exclude_domains=["example.com"])
```

**Tip:** Keep domain lists short and relevant.

### auto_parameters

Tavily auto-configures based on query intent. Explicit values override automatic ones.

```python
client.search(
    query="impact of AI in education policy",
    auto_parameters=True,
    search_depth="basic"  # Override to control cost (auto may set "advanced")
)
```

**Warning:** `auto_parameters` may set `search_depth="advanced"` (2 credits). Set manually to control cost.

---

## Extract Best Practices

### Using Query for Targeted Extraction

```python
# Extract only relevant portions
response = client.extract(
    urls=["https://example.com/article"],
    query="machine learning applications in healthcare",
    chunks_per_source=3  # Max 500 chars each, 1-5 chunks
)
```

**When to use query:**

- Extract only relevant portions of long documents
- Need focused content instead of full page
- Targeted information retrieval

**Note:** `chunks_per_source` only works when `query` is provided.

### Extract Depth Selection

| Depth           | Use Case                                  |
| --------------- | ----------------------------------------- |
| basic (default) | Simple text, faster processing            |
| advanced        | Complex pages, tables, JS-rendered, media |

```python
# For complex pages
response = client.extract(
    urls=["https://example.com/complex-page"],
    extract_depth="advanced"
)
```

### Search vs Extract

| Approach                           | When to Use                                        |
| ---------------------------------- | -------------------------------------------------- |
| `search(include_raw_content=True)` | Quick prototyping, single API call                 |
| `extract(urls=[...])`              | Specific URLs, curated extraction, query filtering |

### Optimal Workflow Pipeline

```python
async def content_pipeline(topic):
    # 1. Search to discover URLs
    response = await client.search(
        query=topic,
        search_depth="advanced",
        max_results=20
    )

    # 2. Filter by relevance score (>0.5)
    urls = [r['url'] for r in response['results'] if r.get('score', 0) > 0.5]

    # 3. Deduplicate
    urls = list(set(urls))[:20]

    # 4. Extract with targeted query
    extracted = await client.extract(
        urls=urls,
        query="specific focus question",
        chunks_per_source=3,
        extract_depth="advanced"
    )

    return extracted
```

### Advanced Filtering Strategies

| Strategy     | Description                                 |
| ------------ | ------------------------------------------- |
| Score-based  | Filter search results by relevance score    |
| Domain-based | Filter by trusted domains before extracting |
| Re-ranking   | Use dedicated re-ranking models             |
| LLM-based    | Let LLM assess relevance before extraction  |

---

## Crawl Best Practices

### Using Instructions

Guide crawl with natural language for semantic filtering:

```python
response = client.crawl(
    url="example.com",
    max_depth=2,
    instructions="Find all documentation pages about Python",
    chunks_per_source=3  # Only with instructions
)
```

**Note:** `chunks_per_source` only works when `instructions` are provided.

### Depth vs Performance

| Parameter   | Description            | Impact                  |
| ----------- | ---------------------- | ----------------------- |
| max_depth   | Levels deep from start | **Exponential** latency |
| max_breadth | Links per page         | Horizontal spread       |
| limit       | Total max pages        | Hard cap                |

**Critical:** Each depth level increases time exponentially. Start with `max_depth=1`.

```python
# ✅ Conservative (recommended start)
client.crawl(url="example.com", max_depth=1, max_breadth=20, limit=20)

# ⚠️ Comprehensive (use carefully)
client.crawl(url="example.com", max_depth=3, max_breadth=100, limit=500)
```

### Path Filtering (Regex)

```python
# Target specific sections
client.crawl(
    url="example.com",
    select_paths=["/blog/.*", "/docs/.*"],
    exclude_paths=["/private/.*", "/admin/.*"]
)

# Stay within subdomain
client.crawl(
    url="docs.example.com",
    select_domains=["^docs.example.com$"]
)
```

### Map Before Crawl Workflow

1. Use Map to discover site structure
2. Analyze paths and patterns
3. Configure Crawl with discovered paths
4. Execute focused crawl

### Common Pitfalls

| Pitfall                 | Impact             | Solution               |
| ----------------------- | ------------------ | ---------------------- |
| Excessive depth (>3)    | Exponential time   | Start with 1-2         |
| No instructions         | Irrelevant content | Use semantic filtering |
| Missing limit           | Runaway costs      | Always set limit       |
| Ignoring failed_results | Incomplete data    | Monitor failures       |

---

## Research Best Practices

### Prompting Tips

- **Be specific** — include known details (market, competitors, geography)
- **Avoid contradictions** — no conflicting constraints or goals
- **Share what's known** — include prior assumptions so research doesn't repeat
- **Keep prompts clean** — clear task + context + output format

**Example prompts:**

```text
"Research the company ____ and its 2026 outlook. Provide overview
of products, services, and market position."
```

```text
"We're evaluating Notion as a partner. We know they serve SMB/mid-market,
expanded AI in 2025, compete with Confluence and ClickUp. Research their
2026 outlook, growth risks, and partnership opportunities. Include citations."
```

### Model Selection

| Model | Best For                             | Credits  |
| ----- | ------------------------------------ | -------- |
| mini  | Narrow, well-scoped questions        | 4-110    |
| pro   | Complex, multi-domain, deep analysis | 15-250   |
| auto  | Unsure of complexity                 | Variable |

```python
# Mini for focused questions
client.research(
    input="What are the top 5 competitors to X in SMB market?",
    model="mini"
)

# Pro for comprehensive analysis
client.research(
    input="Analyze competitive landscape for X including positioning, pricing, segments, product moves, and risks over 2-3 years.",
    model="pro"
)
```

### Structured Output vs Report

| Mode                              | Best For                                  |
| --------------------------------- | ----------------------------------------- |
| Structured Output (output_schema) | Data pipelines, enrichment, powering UIs  |
| Report (default)                  | Reading, sharing, chat interfaces, briefs |

**Schema tips:**

- Write clear field descriptions (1-3 sentences)
- Use proper types (arrays, objects, enums) — not comma-separated strings
- Avoid duplicate/overlapping fields

### Streaming vs Polling

| Mode                         | Best For                           |
| ---------------------------- | ---------------------------------- |
| Streaming (`stream=True`)    | User interfaces, real-time updates |
| Polling (GET /research/{id}) | Background processes               |

---

## API Key Management

### If Key Leaks

1. **Revoke immediately** in [Tavily Dashboard](https://app.tavily.com)
2. **Generate new key**
3. **Update applications** (env vars, secrets manager)
4. **Contact support** if unusual usage: support@tavily.com

### Key Rotation

Rotate keys every **90 days** as security best practice.

**Zero-downtime rotation:**

1. Generate new key (keep old active)
2. Deploy app with new key
3. Verify functionality
4. Revoke old key

### Security Rules

```python
# ✅ Use environment variables
import os
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ❌ Never hardcode in source
client = TavilyClient(api_key="tvly-XXXXX")  # WRONG
```

**Never:**

- Hardcode keys in source code
- Commit keys to repositories
- Expose in client-side code
- Share in screenshots
