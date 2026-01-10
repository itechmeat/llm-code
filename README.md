# LLM Code

A collection of universal assets for AI coding tools.

## What's Here

- **[Skills](.llm-code/skills/)** — structured instructions based on official documentation ([agentskills.io](https://agentskills.io) specification)
- **Agents** — specialized agent definitions _(coming later)_
- **Instructions** — rules for specific file types _(coming later)_
- **Commands** — custom commands _(coming later)_

## Available Skills

Each skill is built exclusively from official product documentation to ensure accuracy.

| Skill                                                       | Description                    |
| ----------------------------------------------------------- | ------------------------------ |
| [beads](.llm-code/skills/beads/README.md)                   | Beads Viewer issue tracking    |
| [coderabbit](.llm-code/skills/coderabbit/README.md)         | CodeRabbit code review         |
| [fastapi](.llm-code/skills/fastapi/README.md)               | FastAPI web framework          |
| [makefile](.llm-code/skills/makefile/README.md)             | GNU Make build automation      |
| [mantine-dev](.llm-code/skills/mantine-dev/README.md)       | Mantine UI components          |
| [open-meteo](.llm-code/skills/open-meteo/README.md)         | Open-Meteo weather API         |
| [openapi](.llm-code/skills/openapi/README.md)               | OpenAPI specification          |
| [postgresql](.llm-code/skills/postgresql/README.md)         | PostgreSQL database            |
| [qdrant](.llm-code/skills/qdrant/README.md)                 | Qdrant vector database         |
| [refine-dev](.llm-code/skills/refine-dev/README.md)         | Refine admin framework         |
| [refine-mantine](.llm-code/skills/refine-mantine/README.md) | Refine + Mantine integration   |
| [skill-master](.llm-code/skills/skill-master/README.md)     | Meta-skill for creating skills |
| [telegram](.llm-code/skills/telegram/README.md)             | Telegram Bot API               |

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
