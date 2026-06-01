# Chat Completions Reference

Web-grounded AI responses with conversation context.

## Basic Usage

```python
from perplexity import Perplexity

client = Perplexity()

completion = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "Tell me about AI developments"}]
)

print(completion.choices[0].message.content)
```

## Extended Type Encoding (v0.28.0)

The Python client ships with a custom JSON encoder for broader type support.
If you pass non-primitive objects in request payloads, let the client encode
them instead of manually serializing to JSON.

## Message Roles

| Role        | Purpose                       |
| ----------- | ----------------------------- |
| `system`    | Set behavior and persona      |
| `user`      | User input/questions          |
| `assistant` | Model responses (for context) |

## Multi-Turn Conversation

```python
messages = [
    {"role": "system", "content": "You are a research assistant."},
    {"role": "user", "content": "What causes climate change?"},
    {"role": "assistant", "content": "Climate change is caused by..."},
    {"role": "user", "content": "What are the solutions?"}
]

completion = client.chat.completions.create(
    messages=messages,
    model="sonar"
)
```

## Streaming Responses

```python
stream = client.chat.completions.create(
    messages=[{"role": "user", "content": "Write a summary of AI breakthroughs"}],
    model="sonar",
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Responses API streaming note (v0.34.1+)

The Python SDK now yields named SSE events for `responses.create` and discriminates the `ResponseStreamEvent` union. If your app branches on event types, prefer the named event/type fields over brittle string parsing of raw chunks.

**TypeScript:**

```typescript
const stream = await client.chat.completions.create({
  messages: [{ role: "user", content: "Explain quantum computing" }],
  model: "sonar",
  stream: true,
});

for await (const chunk of stream) {
  if (chunk.choices[0]?.delta?.content) {
    process.stdout.write(chunk.choices[0].delta.content);
  }
}
```

## Web Search Options

```python
completion = client.chat.completions.create(
    messages=[{"role": "user", "content": "Latest renewable energy news"}],
    model="sonar",
    web_search_options={
        "search_recency_filter": "week",
        "search_domain_filter": ["energy.gov", "iea.org"],
        "max_search_results": 10
    }
)
```

### Recency Filters

- `hour`, `day`, `week`, `month`, `year`

### Return Options

```python
completion = client.chat.completions.create(
    messages=[...],
    model="sonar",
    return_images=True,
    return_related_questions=True
)
```

## Response Parameters

| Parameter           | Default | Range   | Description           |
| ------------------- | ------- | ------- | --------------------- |
| `temperature`       | 0.7     | 0-2     | Creativity level      |
| `max_tokens`        | varies  | -       | Response length limit |
| `top_p`             | 0.9     | 0-1     | Nucleus sampling      |
| `presence_penalty`  | 0       | -2 to 2 | Topic diversity       |
| `frequency_penalty` | 0       | -2 to 2 | Word repetition       |

```python
completion = client.chat.completions.create(
    messages=[{"role": "user", "content": "Explain ML"}],
    model="sonar",
    max_tokens=500,
    temperature=0.7,
    top_p=0.9
)
```

## Async Chat (sonar-deep-research only)

### Create Async Request

```python
async_request = client.async_.chat.completions.create(
    messages=[{"role": "user", "content": "Comprehensive renewable energy analysis"}],
    model="sonar-deep-research",
    max_tokens=2000
)

print(f"Request ID: {async_request.request_id}")
print(f"Status: {async_request.status}")
```

### Check Status

```python
request_id = "req_123abc456def789"
status = client.async_.chat.completions.get(request_id)

if status.status == "completed":
    print(status.result.choices[0].message.content)
elif status.status == "failed":
    print(f"Error: {status.error}")
```

### List Requests

```python
requests = client.async_.chat.completions.list(
    limit=10,
    status="completed"
)

for req in requests.data:
    print(f"ID: {req.id}, Status: {req.status}")
```

## Responses API background tasks (v0.35.0+)

The SDK adds background-task support and `responses.retrieve`. Use this for long-running responses when you need a request id and polling/retrieval flow instead of holding a streaming connection open.

Operational notes:

- Persist the response id immediately so retries can retrieve the same job.
- Keep timeouts and cancellation policy explicit; background execution should not become an unbounded queue.
- `xhigh` reasoning effort is available where the API/model supports reasoning controls.
- `0.36.0` adds the Responses API sandbox built-in tool. Treat sandbox use as a tool-execution surface: gate it by product policy, log invocations, and do not expose it implicitly to untrusted user prompts.

## Concurrent Operations

```python
import asyncio
from perplexity import AsyncPerplexity

async def process_questions(questions):
    async with AsyncPerplexity() as client:
        tasks = [
            client.chat.completions.create(
                messages=[{"role": "user", "content": q}],
                model="sonar"
            )
            for q in questions
        ]
        return await asyncio.gather(*tasks)
```

## Error Handling

```python
import perplexity

try:
    completion = client.chat.completions.create(...)
except perplexity.BadRequestError as e:
    print(f"Invalid parameters: {e}")
except perplexity.RateLimitError:
    print("Rate limited, retry later")
except perplexity.APIStatusError as e:
    print(f"API error: {e.status_code}")
```

## Rate Limit Retry Pattern

```python
import time
import random

def chat_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                messages=messages,
                model="sonar"
            )
        except perplexity.RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

## Configuration Presets

### Factual Q&A

```python
factual = {
    "temperature": 0.1,
    "top_p": 0.9,
    "search_recency_filter": "month"
}
```

### Creative Writing

```python
creative = {
    "temperature": 0.8,
    "top_p": 0.95,
    "presence_penalty": 0.1,
    "frequency_penalty": 0.1
}
```

## System Prompt Example

```python
system_prompt = """You are an expert research assistant.
Always provide well-sourced information and cite your sources.
Format responses with clear headings and bullet points."""

completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Explain quantum computing applications"}
    ],
    model="sonar-pro"
)
```

## Best Practices

1. **Choose right model:** sonar for simple, sonar-pro for complex
2. **Use streaming:** Better UX for long responses
3. **Implement retry:** Handle rate limits gracefully
4. **Set temperature:** Low (0.1) for facts, high (0.8) for creativity
5. **Use system prompts:** Consistent behavior across requests
