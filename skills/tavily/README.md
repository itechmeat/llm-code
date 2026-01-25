# Tavily Skill

Agent Skill for integrating Tavily AI-powered search API in LLM applications.

## Overview

Tavily is a search engine optimized for AI agents and LLM applications. Unlike traditional search APIs, Tavily delivers clean, relevant content ready for LLM consumption.

## Key Features

- **Search**: Web search with AI-generated answers and content extraction
- **Extract**: Pull structured content from specific URLs
- **Crawl**: Deep website crawling with AI-guided filtering
- **Map**: Discover website structure and URLs
- **Research** (Beta): Autonomous deep research on complex topics

## When to Use This Skill

- Building RAG pipelines that need real-time web data
- Creating AI agents with web search capabilities
- Extracting content from websites for analysis
- Implementing fact-checking or research automation

## Files

| File                                                         | Description                                               |
| ------------------------------------------------------------ | --------------------------------------------------------- |
| [SKILL.md](SKILL.md)                                         | Main skill with quick start, patterns, and best practices |
| [references/api.md](references/api.md)                       | REST API endpoints and parameters                         |
| [references/python.md](references/python.md)                 | Python SDK reference (TavilyClient, AsyncTavilyClient)    |
| [references/javascript.md](references/javascript.md)         | JavaScript SDK reference                                  |
| [references/best-practices.md](references/best-practices.md) | Best practices for Search, Extract, Crawl, Research       |
| [references/integrations.md](references/integrations.md)     | MCP, LangChain, LlamaIndex, CrewAI, Pydantic AI, n8n      |

## Quick Example

```python
from tavily import TavilyClient

client = TavilyClient(api_key="tvly-YOUR_API_KEY")

# Search with AI answer
response = client.search(
    query="What are the latest developments in AI?",
    include_answer="advanced"
)

print(response["answer"])
```

## Links

- [Tavily Documentation](https://docs.tavily.com)
- [API Console](https://app.tavily.com)
- [Python SDK](https://pypi.org/project/tavily-python/)
- [JavaScript SDK](https://www.npmjs.com/package/@tavily/core)
