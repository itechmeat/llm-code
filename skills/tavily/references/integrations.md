# Tavily MCP & Integrations

## MCP Server

Model Context Protocol (MCP) enables AI assistants to integrate with Tavily for real-time web search and extraction.

### Remote MCP Server (Easiest)

```text
https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>
```

### Claude Desktop

Add integration in Claude Desktop (Settings > Integrations):

- Name: Tavily
- URL: `https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>`

### Cursor

```json
{
  "mcpServers": {
    "tavily-remote-mcp": {
      "command": "npx -y mcp-remote https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>",
      "env": {}
    }
  }
}
```

### Local Installation

```bash
# Prerequisites: Node.js v20+
npx -y @tavily/mcp
```

**Claude Desktop config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tavily-mcp": {
      "command": "npx",
      "args": ["-y", "@tavily/mcp"],
      "env": {
        "TAVILY_API_KEY": "tvly-YOUR_API_KEY"
      }
    }
  }
}
```

### OpenAI Integration

```python
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "mcp",
        "server_label": "tavily",
        "server_url": "https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>",
        "require_approval": "never",
    }],
    input="Search for recent AI developments"
)
```

### Available MCP Tools

| Tool           | Description               |
| -------------- | ------------------------- |
| tavily-search  | Web search with filters   |
| tavily-extract | Extract content from URLs |

---

## LangChain

**Package:** `langchain-tavily` (recommended over deprecated `langchain_community.tools.tavily_search`)

```bash
pip install -U langchain-tavily
```

### TavilySearch Tool

```python
from langchain_tavily import TavilySearch

tool = TavilySearch(
    max_results=5,
    topic="general",           # "general", "news", "finance"
    search_depth="basic",      # "basic", "advanced"
    include_answer=False,
    include_raw_content=False,
    include_images=False,
    time_range="day",          # "day", "week", "month", "year"
    include_domains=["wikipedia.org"],
    exclude_domains=["pinterest.com"]
)

# Direct invocation
result = tool.invoke({"query": "What happened at Wimbledon?"})
```

### Use with Agent

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

tavily_search = TavilySearch(max_results=5)

agent = create_agent(
    model=ChatOpenAI(model="gpt-4"),
    tools=[tavily_search],
    system_prompt="You are a research assistant. Use web search for up-to-date info."
)

response = agent.invoke({
    "messages": [{"role": "user", "content": "Latest AI developments?"}]
})
```

**Tip:** Inject today's date in system prompt for time-aware searches.

---

## LlamaIndex

```bash
pip install llama-index-tools-tavily-research llama-index tavily-python
```

### TavilyToolSpec

```python
from llama_index.tools.tavily_research.base import TavilyToolSpec
from llama_index.agent.openai import OpenAIAgent

tavily_tool = TavilyToolSpec(api_key='tvly-YOUR_API_KEY')
agent = OpenAIAgent.from_tools(tavily_tool.to_tool_list())

response = agent.chat('What happened at the latest Burning Man?')
```

**Tool:** `search` — returns list of URLs and relevant content for agent use.

---

## Google ADK

```bash
pip install google-adk mcp
```

### Agent Setup

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
import os

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

root_agent = Agent(
    model="gemini-2.5-pro",
    name="tavily_agent",
    instruction="Use Tavily to search the web, extract content, and explore websites.",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://mcp.tavily.com/mcp/",
                headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
            ),
        )
    ],
)
```

### Run Agent

```bash
adk create my_agent
adk run my_agent        # CLI interface
adk web --port 8000     # Web interface
```

**Available Tools:** tavily-search, tavily-extract, tavily-map, tavily-crawl

---

## n8n (No-Code)

No-code workflow automation with Tavily.

### Setup

1. In n8n, search for **Tavily** node
2. Add to workflow as:
   - **Node** — standalone Search or Extract
   - **Tool** — for AI agent workflows
3. Connect with Tavily API key

### Actions

| Action  | Parameters                                                               |
| ------- | ------------------------------------------------------------------------ |
| Search  | query, topic, include_raw_content, include/exclude domains, search_depth |
| Extract | URL(s), extraction type (basic/advanced)                                 |

### Use Cases

- Job search automation
- Competitive intelligence
- Market research & news monitoring
- Lead enrichment
- Content curation

**Tip:** Use `SplitInBatches` node for multiple results, `Merge` node to combine searches.

---

## Pydantic AI

```bash
pip install "pydantic-ai-slim[tavily]"
```

### Agent Setup

```python
import os
from pydantic_ai.agent import Agent
from pydantic_ai.common_tools.tavily import tavily_search_tool

api_key = os.getenv('TAVILY_API_KEY')

agent = Agent(
    'openai:o3-mini',
    tools=[tavily_search_tool(api_key)],
    system_prompt='Search Tavily for the given query and return the results.'
)

result = agent.run_sync('Top news in GenAI world, give me links.')
print(result.output)
```

---

## CrewAI

Multi-agent framework with Tavily web search.

```bash
pip install 'crewai[tools]'
```

### TavilySearchTool

```python
from crewai import Agent, Task, Crew
from crewai_tools import TavilySearchTool

tavily_tool = TavilySearchTool(
    search_depth="advanced",
    max_results=10,
    include_answer=True
)

researcher = Agent(
    role='News Researcher',
    goal='Find trending information about AI agents',
    backstory='Expert researcher specializing in AI technology.',
    tools=[tavily_tool],
    verbose=True
)

research_task = Task(
    description='Search for the top 3 Agentic AI trends in 2025.',
    expected_output='A JSON report summarizing the top 3 AI trends.',
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[research_task], verbose=True)
result = crew.kickoff()
```

**Search Parameters:** query, search_depth, topic, time_range, max_results, include/exclude_domains, include_answer, include_raw_content, include_images, timeout

### TavilyExtractorTool

```python
from crewai_tools import TavilyExtractorTool

tavily_extract = TavilyExtractorTool(
    extract_depth="advanced",
    include_images=True
)

extractor = Agent(
    role='Content Extractor',
    goal='Extract key information from web pages',
    tools=[tavily_extract]
)
```

**Extract Parameters:** urls, include_images, extract_depth, timeout
