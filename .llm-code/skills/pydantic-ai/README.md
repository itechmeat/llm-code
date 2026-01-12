# Pydantic AI Skill

Agent Skill for building AI agents with [Pydantic AI](https://ai.pydantic.dev/) framework.

## Overview

Pydantic AI is a Python agent framework for building production-grade GenAI applications with the "FastAPI feeling". It provides type-safe agents, dependency injection, structured output, and integrations with 25+ model providers.

## Contents

- [SKILL.md](SKILL.md) — Main skill file with quick start and best practices
- [references/agents.md](references/agents.md) — Agent API, dependencies, run methods
- [references/tools.md](references/tools.md) — Function tools and structured output
- [references/models.md](references/models.md) — Model providers and configuration
- [references/evals.md](references/evals.md) — Pydantic Evals testing framework
- [references/integrations.md](references/integrations.md) — MCP, Logfire, A2A, durable execution

## Key Features

- **Model-agnostic**: OpenAI, Anthropic, Google, Groq, Mistral, and 20+ more providers
- **Type-safe**: Full IDE support with type checking
- **Dependency injection**: Pass context to tools and prompts
- **Structured output**: Pydantic model validation
- **MCP integration**: Connect to external tools via Model Context Protocol
- **Pydantic Evals**: Systematic agent testing and evaluation
- **Logfire observability**: Built-in tracing and debugging

## Quick Start

```bash
pip install pydantic-ai
```

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='Be helpful.')
result = agent.run_sync('Hello!')
print(result.output)
```

## Links

- [Documentation](https://ai.pydantic.dev/)
- [GitHub](https://github.com/pydantic/pydantic-ai)
