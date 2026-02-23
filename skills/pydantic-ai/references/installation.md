# Installation

**Requires Python 3.10+ (Python 3.14 supported in v1.61+)**

```bash
# Full install (all model dependencies)
pip install pydantic-ai

# With examples
pip install "pydantic-ai[examples]"
```

## Slim Install

Use `pydantic-ai-slim` for minimal dependencies:

```bash
# Single model
pip install "pydantic-ai-slim[openai]"

# Multiple models
pip install "pydantic-ai-slim[openai,anthropic,logfire]"
```

## Optional Groups

| Group                   | Dependency                 |
| ----------------------- | -------------------------- |
| `openai`                | OpenAI models & embeddings |
| `anthropic`             | Anthropic Claude           |
| `google`                | Google Gemini & embeddings |
| `xai`                   | xAI Grok (native SDK)      |
| `groq`                  | Groq models                |
| `mistral`               | Mistral models             |
| `bedrock`               | AWS Bedrock                |
| `vertexai`              | Google Vertex AI           |
| `cohere`                | Cohere models & embeddings |
| `huggingface`           | Hugging Face Inference     |
| `voyageai`              | VoyageAI embeddings        |
| `sentence-transformers` | Local embeddings           |
| `logfire`               | Pydantic Logfire           |
| `evals`                 | Pydantic Evals             |
| `mcp`                   | MCP protocol               |
| `fastmcp`               | FastMCP                    |
| `a2a`                   | Agent-to-Agent             |
| `tavily`                | Tavily search              |
| `duckduckgo`            | DuckDuckGo search          |
| `exa`                   | Exa neural search          |
| `cli`                   | CLI tools                  |
| `dbos`                  | DBOS durable execution     |
| `prefect`               | Prefect durable execution  |
