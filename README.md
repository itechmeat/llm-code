# LLM Code

A collection of universal assets for AI coding tools.

## What's Here

- **[Skills](.llm-code/skills/)** — structured instructions based on official documentation ([agentskills.io](https://agentskills.io) specification)
- **Agents** — specialized agent definitions _(coming later)_
- **Instructions** — rules for specific file types _(coming later)_
- **Commands** — custom commands _(coming later)_

## Available Skills

Each skill is built exclusively from official product documentation to ensure accuracy.

| Skill                                                                               | Description                                    |
| ----------------------------------------------------------------------------------- | ---------------------------------------------- |
| [base-ui](.llm-code/skills/base-ui/README.md)                                       | Base UI unstyled React components              |
| [beads](.llm-code/skills/beads/README.md)                                           | Beads Viewer issue tracking                    |
| [changelog](.llm-code/skills/changelog/README.md)                                   | Keep a Changelog format                        |
| [cloudflare-workers](.llm-code/skills/cloudflare-workers/README.md)                 | Cloudflare Workers serverless                  |
| [cloudflare-images](.llm-code/skills/cloudflare-images/README.md)                   | Cloudflare Images service                      |
| [cloudflare-pages](.llm-code/skills/cloudflare-pages/README.md)                     | Cloudflare Pages deployment                    |
| [cloudflare-d1](.llm-code/skills/cloudflare-d1/README.md)                           | Cloudflare D1 SQLite database                  |
| [cloudflare-r2](.llm-code/skills/cloudflare-r2/README.md)                           | Cloudflare R2 object storage                   |
| [cloudflare-kv](.llm-code/skills/cloudflare-kv/README.md)                           | Cloudflare Workers KV storage                  |
| [cloudflare-queues](.llm-code/skills/cloudflare-queues/README.md)                   | Cloudflare Queues message queue                |
| [cloudflare-workflows](.llm-code/skills/cloudflare-workflows/README.md)             | Cloudflare Workflows durable execution         |
| [cloudflare-durable-objects](.llm-code/skills/cloudflare-durable-objects/README.md) | Cloudflare Durable Objects stateful serverless |
| [coderabbit](.llm-code/skills/coderabbit/README.md)                                 | CodeRabbit code review                         |
| [commits](.llm-code/skills/commits/README.md)                                       | Conventional Commits format                    |
| [fastapi](.llm-code/skills/fastapi/README.md)                                       | FastAPI web framework                          |
| [makefile](.llm-code/skills/makefile/README.md)                                     | GNU Make build automation                      |
| [mantine-dev](.llm-code/skills/mantine-dev/README.md)                               | Mantine UI components                          |
| [open-meteo](.llm-code/skills/open-meteo/README.md)                                 | Open-Meteo weather API                         |
| [openapi](.llm-code/skills/openapi/README.md)                                       | OpenAPI specification                          |
| [openspec](.llm-code/skills/openspec/README.md)                                     | OpenSpec workflow specification                |
| [perplexity](.llm-code/skills/perplexity/README.md)                                 | Perplexity AI conversational search            |
| [postgresql](.llm-code/skills/postgresql/README.md)                                 | PostgreSQL database                            |
| [pydantic-ai](.llm-code/skills/pydantic-ai/README.md)                               | Pydantic AI agent framework                    |
| [qdrant](.llm-code/skills/qdrant/README.md)                                         | Qdrant vector database                         |
| [react-testing-library](.llm-code/skills/react-testing-library/README.md)           | React component testing                        |
| [refine-dev](.llm-code/skills/refine-dev/README.md)                                 | Refine admin framework                         |
| [skill-master](.llm-code/skills/skill-master/README.md)                             | Meta-skill for creating skills                 |
| [social-writer](.llm-code/skills/social-writer/README.md)                           | Social media content creation                  |
| [tavily](.llm-code/skills/tavily/README.md)                                         | Tavily AI search API                           |
| [telegram](.llm-code/skills/telegram/README.md)                                     | Telegram Bot API                               |
| [vibekanban](.llm-code/skills/vibekanban/README.md)                                 | AI coding agent orchestration                  |
| [vite](.llm-code/skills/vite/README.md)                                             | Vite project and API guidance                  |
| [vitest](.llm-code/skills/vitest/README.md)                                         | Vitest testing framework                       |

> _This collection reflects the author's personal needs. New skills will be added for development, product management, research, analytics, and other workflows._

## Compatibility

Works with any AI coding tool:
GitHub Copilot, Claude Code, OpenCode, Cursor, Gemini, Qwen, Continue, Aider, and other MCP-compatible tools.

## Basic Usage

1. Copy `.llm-code/` to your project
2. Run with your tool (example for Claude Code):

```bash
.llm-code/link-assets.sh -t claude
```

See [.llm-code/README.md](.llm-code/README.md) for detailed setup and all supported tools.

## Documentation

- [.llm-code/README.md](.llm-code/README.md) — setup guide and tool mappings
- [.llm-code/skills/skill-master/SKILL.md](.llm-code/skills/skill-master/SKILL.md) — skills specification
