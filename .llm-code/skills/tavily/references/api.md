# Tavily REST API Reference

Base URL: `https://api.tavily.com`

## Authentication

All requests require Bearer token in header:

```bash
Authorization: Bearer tvly-YOUR_API_KEY
```

## POST /search

Web search optimized for LLMs.

### Request Body

| Parameter                  | Type        | Default      | Description                                                                                    |
| -------------------------- | ----------- | ------------ | ---------------------------------------------------------------------------------------------- |
| query                      | string      | **required** | Search query                                                                                   |
| search_depth               | string      | `"basic"`    | `"basic"` (1 credit), `"advanced"` (2 credits), `"fast"` (1 credit), `"ultra-fast"` (1 credit) |
| topic                      | string      | `"general"`  | `"general"`, `"news"`, `"finance"`                                                             |
| max_results                | int         | 5            | 1-20 results                                                                                   |
| include_answer             | bool/string | false        | `true`/`"basic"` (quick), `"advanced"` (detailed)                                              |
| include_raw_content        | bool/string | false        | `true`/`"markdown"`, `"text"` (plain text)                                                     |
| include_images             | bool        | false        | Include related images                                                                         |
| include_image_descriptions | bool        | false        | Add descriptions to images                                                                     |
| include_domains            | string[]    | []           | Filter to specific domains (max 300)                                                           |
| exclude_domains            | string[]    | []           | Exclude domains (max 150)                                                                      |
| time_range                 | string      | -            | `"day"`, `"week"`, `"month"`, `"year"` (or `"d"`, `"w"`, `"m"`, `"y"`)                         |
| start_date                 | string      | -            | `YYYY-MM-DD` format                                                                            |
| end_date                   | string      | -            | `YYYY-MM-DD` format                                                                            |
| country                    | string      | -            | Boost results from specific country                                                            |
| chunks_per_source          | int         | 3            | 1-3, only with `search_depth="advanced"`                                                       |
| auto_parameters            | bool        | false        | Auto-configure based on query intent                                                           |
| include_favicon            | bool        | false        | Include favicon URLs                                                                           |
| include_usage              | bool        | false        | Include credit usage info                                                                      |

### Response

```json
{
  "query": "Who is Leo Messi?",
  "answer": "AI-generated answer...",
  "results": [
    {
      "title": "Page Title",
      "url": "https://...",
      "content": "Relevant content...",
      "score": 0.95,
      "raw_content": "...",
      "published_date": "2024-01-15",
      "favicon": "https://.../favicon.ico"
    }
  ],
  "images": [{ "url": "...", "description": "..." }],
  "response_time": 1.67,
  "usage": { "credits": 1 },
  "request_id": "123e4567-..."
}
```

---

## POST /extract

Extract content from specific URLs.

### Request Body

| Parameter         | Type            | Default      | Description                                   |
| ----------------- | --------------- | ------------ | --------------------------------------------- |
| urls              | string/string[] | **required** | URL(s) to extract (max 20)                    |
| extract_depth     | string          | `"basic"`    | `"basic"` (1/5 URLs), `"advanced"` (2/5 URLs) |
| format            | string          | `"markdown"` | `"markdown"` or `"text"`                      |
| include_images    | bool            | false        | Include extracted images                      |
| query             | string          | -            | Rerank chunks by relevance to query           |
| chunks_per_source | int             | 3            | 1-5, only when `query` provided               |
| timeout           | float           | auto         | 1-60 seconds                                  |
| include_favicon   | bool            | false        | Include favicon URLs                          |
| include_usage     | bool            | false        | Include credit usage info                     |

### Response

```json
{
  "results": [
    {
      "url": "https://...",
      "raw_content": "Extracted markdown content...",
      "images": ["https://..."],
      "favicon": "https://.../favicon.ico"
    }
  ],
  "failed_results": [{ "url": "https://...", "error": "Timeout" }],
  "response_time": 0.02,
  "usage": { "credits": 1 },
  "request_id": "123e4567-..."
}
```

---

## POST /crawl

Crawl websites with AI-guided instructions.

### Request Body

| Parameter         | Type     | Default      | Description                                       |
| ----------------- | -------- | ------------ | ------------------------------------------------- |
| url               | string   | **required** | Starting URL                                      |
| instructions      | string   | -            | Natural language guidance (2x credit cost)        |
| max_depth         | int      | 1            | 1-5 levels deep                                   |
| max_breadth       | int      | 20           | Links per page                                    |
| limit             | int      | 50           | Total pages to process                            |
| select_paths      | string[] | -            | Regex patterns to include (e.g., `"/docs/.*"`)    |
| exclude_paths     | string[] | -            | Regex patterns to exclude (e.g., `"/private/.*"`) |
| select_domains    | string[] | -            | Regex for allowed domains                         |
| exclude_domains   | string[] | -            | Regex for excluded domains                        |
| allow_external    | bool     | true         | Follow external links                             |
| extract_depth     | string   | `"basic"`    | `"basic"` or `"advanced"`                         |
| format            | string   | `"markdown"` | `"markdown"` or `"text"`                          |
| include_images    | bool     | false        | Extract images                                    |
| chunks_per_source | int      | 3            | 1-5, only with `instructions`                     |
| timeout           | float    | 150          | 10-150 seconds                                    |
| include_favicon   | bool     | false        | Include favicon URLs                              |
| include_usage     | bool     | false        | Include credit usage info                         |

### Response

```json
{
  "base_url": "docs.tavily.com",
  "results": [
    {
      "url": "https://docs.tavily.com/welcome",
      "raw_content": "Extracted content...",
      "images": [],
      "favicon": "https://.../favicon.ico"
    }
  ],
  "response_time": 1.23,
  "usage": { "credits": 1 },
  "request_id": "123e4567-..."
}
```

---

## POST /map

Get website structure (URLs only, no content).

### Request Body

| Parameter       | Type     | Default      | Description                                |
| --------------- | -------- | ------------ | ------------------------------------------ |
| url             | string   | **required** | Starting URL                               |
| instructions    | string   | -            | Natural language guidance (2x credit cost) |
| max_depth       | int      | 1            | 1-5 levels deep                            |
| max_breadth     | int      | 20           | Links per page                             |
| limit           | int      | 50           | Total links to process                     |
| select_paths    | string[] | -            | Regex patterns to include                  |
| exclude_paths   | string[] | -            | Regex patterns to exclude                  |
| select_domains  | string[] | -            | Regex for allowed domains                  |
| exclude_domains | string[] | -            | Regex for excluded domains                 |
| allow_external  | bool     | true         | Include external links                     |
| timeout         | float    | 150          | 10-150 seconds                             |
| include_usage   | bool     | false        | Include credit usage info                  |

### Response

```json
{
  "base_url": "docs.tavily.com",
  "results": ["https://docs.tavily.com/welcome", "https://docs.tavily.com/documentation/about"],
  "response_time": 1.23,
  "usage": { "credits": 1 },
  "request_id": "123e4567-..."
}
```

---

## POST /research (Beta)

Autonomous deep research on complex topics.

### Request Body

| Parameter       | Type   | Default      | Description                                                  |
| --------------- | ------ | ------------ | ------------------------------------------------------------ |
| input           | string | **required** | Research question                                            |
| model           | string | `"auto"`     | `"mini"` (4-110 credits), `"pro"` (15-250 credits), `"auto"` |
| stream          | bool   | false        | Stream results via SSE                                       |
| output_schema   | object | -            | JSON Schema for structured output                            |
| citation_format | string | `"numbered"` | `"numbered"`, `"mla"`, `"apa"`, `"chicago"`                  |

### Response

```json
{
  "request_id": "123e4567-...",
  "created_at": "2025-01-15T10:30:00Z",
  "status": "pending",
  "input": "What are the latest developments in AI?",
  "model": "mini",
  "response_time": 1.23
}
```

---

## GET /research/{request_id}

Poll for research task status and results.

### Path Parameters

| Parameter  | Type   | Description             |
| ---------- | ------ | ----------------------- |
| request_id | string | Unique research task ID |

### Response (200 - completed)

```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174111",
  "created_at": "2025-01-15T10:30:00Z",
  "status": "completed",
  "content": "Research Report: Latest Developments in AI\n\n## Executive Summary\n\n...",
  "sources": [
    {
      "title": "Latest AI Developments",
      "url": "https://example.com/ai-news",
      "favicon": "https://example.com/favicon.ico"
    }
  ],
  "response_time": 1.23
}
```

### Status Codes

| Code | Description                  |
| ---- | ---------------------------- |
| 200  | Research completed or failed |
| 202  | Research still in progress   |
| 401  | Unauthorized                 |
| 404  | Research task not found      |
| 500  | Server error                 |

---

## Research Streaming

Enable real-time progress with `stream: true` in POST /research request.

### Event Types

| Event Type    | Description                                         |
| ------------- | --------------------------------------------------- |
| tool_call     | Agent performing action (WebSearch, Planning, etc.) |
| tool_response | Tool completed with sources                         |
| content       | Streamed report chunks                              |
| sources       | Final list of all sources                           |
| done          | Stream complete                                     |

### Tool Types

| Tool             | Description              | Model    |
| ---------------- | ------------------------ | -------- |
| Planning         | Initialize research plan | Both     |
| WebSearch        | Execute web searches     | Both     |
| ResearchSubtopic | Deep subtopic research   | Pro only |
| Generating       | Generate final report    | Both     |

### Python Streaming

```python
stream = client.research(
    input="Research the latest developments in AI",
    model="pro",
    stream=True
)

for chunk in stream:
    print(chunk.decode('utf-8'))
```

### JavaScript Streaming

```javascript
const stream = await client.research("Latest AI developments", {
  model: "pro",
  stream: true,
});

for await (const chunk of stream) {
  console.log(chunk.toString("utf-8"));
}
```

### SSE Event Structure

```json
{
  "id": "123e4567-...",
  "object": "chat.completion.chunk",
  "model": "mini",
  "created": 1705329000,
  "choices": [{
    "delta": {
      "role": "assistant",
      "content": "# Research Report\n\n...",
      "tool_calls": {...},
      "sources": [...]
    }
  }]
}
```

### Research Flow

1. Planning tool_call → tool_response
2. WebSearch tool_call (with queries) → tool_response (with sources)
3. _(Pro)_ ResearchSubtopic cycles
4. Generating tool_call → tool_response
5. Content events (report chunks)
6. Sources event (all sources)
7. Done event

---

## GET /usage

Get API key and account usage details.

### Response

```json
{
  "key": {
    "usage": 150,
    "limit": 1000
  },
  "account": {
    "current_plan": "Bootstrap",
    "plan_usage": 500,
    "plan_limit": 15000,
    "paygo_usage": 25,
    "paygo_limit": 100
  }
}
```

### Response Fields

| Field                | Description                   |
| -------------------- | ----------------------------- |
| key.usage            | Credits used by this API key  |
| key.limit            | Credit limit for this key     |
| account.current_plan | Active subscription plan      |
| account.plan_usage   | Total credits used this month |
| account.plan_limit   | Monthly credit limit          |
| account.paygo_usage  | Pay-as-you-go credits used    |
| account.paygo_limit  | Pay-as-you-go credit limit    |

---

## Credit Costs Summary

| API           | Basic         | Advanced     | Notes                       |
| ------------- | ------------- | ------------ | --------------------------- |
| Search        | 1             | 2            | Per request                 |
| Extract       | 1 / 5 URLs    | 2 / 5 URLs   | Only charged for successful |
| Map           | 1 / 10 pages  | 2 / 10 pages | With `instructions` = 2x    |
| Crawl         | Map + Extract | -            | Combined cost               |
| Research mini | 4-110         | -            | Dynamic                     |
| Research pro  | 15-250        | -            | Dynamic                     |
