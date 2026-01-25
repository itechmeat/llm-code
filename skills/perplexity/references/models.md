# Perplexity Models Reference

## Available Models

### Sonar (sonar)

- **Purpose:** Lightweight, cost-effective web search
- **Best for:** Quick facts, news updates, simple Q&A, high-volume applications
- **Pricing:** $1/1M input tokens, $1/1M output tokens

### Sonar Pro (sonar-pro)

- **Purpose:** Advanced search with deeper content understanding
- **Best for:** Complex queries, competitive analysis, detailed research
- **Pricing:** $3/1M input tokens, $15/1M output tokens

### Sonar Reasoning Pro (sonar-reasoning-pro)

- **Purpose:** Enhanced multi-step reasoning with web search
- **Best for:** Complex problem-solving, research analysis, strategic planning
- **Pricing:** $2/1M input tokens, $8/1M output tokens

### Sonar Deep Research (sonar-deep-research)

- **Purpose:** Exhaustive research and detailed report generation
- **Best for:** Academic research, market analysis, comprehensive reports
- **Pricing:** $2/1M input, $8/1M output, $2/1M citation tokens, $5/1K search queries, $3/1M reasoning tokens
- **Note:** Async-only model via `client.async_.chat.completions.create()`

## Model Selection Decision Tree

```
Quick factual query? → sonar
Complex analysis needed? → sonar-pro
Multi-step reasoning? → sonar-reasoning-pro
Comprehensive research report? → sonar-deep-research
```

## Request Pricing by Search Context Size

| Model               | Low   | Medium | High   |
| ------------------- | ----- | ------ | ------ |
| sonar               | $5/1K | $8/1K  | $12/1K |
| sonar-pro           | $6/1K | $10/1K | $14/1K |
| sonar-reasoning-pro | $6/1K | $10/1K | $14/1K |

- **Low:** (default) Fastest, cheapest
- **Medium:** Balanced cost/quality
- **High:** Maximum search depth

## Pro Search (sonar-pro only)

Enables automated multi-step tool usage for complex queries.

```python
completion = client.chat.completions.create(
    messages=[...],
    model="sonar-pro",
    stream=True,  # Required for Pro Search
    web_search_options={"search_type": "pro"}
)
```

**Search Types:**

- `fast` — Standard behavior (default)
- `pro` — Multi-step tool usage ($14-$22/1K requests)
- `auto` — Automatic classification

## Cost Examples

### Sonar (500 input + 200 output tokens, Low context)

- Input: $0.0005
- Output: $0.0002
- Request fee: $0.005
- **Total: $0.0057**

### Sonar Deep Research (typical query)

- Input: ~$0.00
- Output: ~$0.03-$0.06
- Citation tokens: ~$0.04-$0.12
- Reasoning tokens: ~$0.22-$1.02
- Search queries: ~$0.09-$0.15
- **Total: $0.40-$1.32**

## Configuration Presets

### Factual Q&A (Low creativity)

```python
config = {
    "temperature": 0.1,
    "top_p": 0.9,
    "search_recency_filter": "month"
}
```

### Creative Writing (Higher creativity)

```python
config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "presence_penalty": 0.1,
    "frequency_penalty": 0.1
}
```

## Search API Pricing

**$5 per 1,000 requests** — No token-based costs.
