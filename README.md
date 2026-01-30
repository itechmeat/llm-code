# LLM Code

A collection of agent skills for AI coding tools.

## Installation

```bash
npx add-skill itechmeat/llm-code
```

This installs all skills to your current project for the detected AI coding agent.

### Options

```bash
# List available skills
npx add-skill itechmeat/llm-code --list

# Install specific skills
npx add-skill itechmeat/llm-code --skill vite --skill fastapi

# Install for specific agents
npx add-skill itechmeat/llm-code -a claude-code -a github-copilot

# Non-interactive (CI/CD friendly)
npx add-skill itechmeat/llm-code -y
```

## Available Skills (37)

Each skill follows the [agentskills.io](https://agentskills.io) specification.

| Skill                                                            | Description                                    |
| ---------------------------------------------------------------- | ---------------------------------------------- |
| [agent-browser](skills/agent-browser/)                           | Headless browser automation for AI agents      |
| [base-ui](skills/base-ui/)                                       | Base UI unstyled React components              |
| [beads](skills/beads/)                                           | Beads distributed git-backed issue tracker     |
| [bun](skills/bun/)                                               | Bun JavaScript/TypeScript runtime and toolkit  |
| [changelog](skills/changelog/)                                   | Keep a Changelog format                        |
| [cloudflare-d1](skills/cloudflare-d1/)                           | Cloudflare D1 SQLite database                  |
| [cloudflare-durable-objects](skills/cloudflare-durable-objects/) | Cloudflare Durable Objects stateful serverless |
| [cloudflare-images](skills/cloudflare-images/)                   | Cloudflare Images service                      |
| [cloudflare-kv](skills/cloudflare-kv/)                           | Cloudflare Workers KV storage                  |
| [cloudflare-pages](skills/cloudflare-pages/)                     | Cloudflare Pages deployment                    |
| [cloudflare-queues](skills/cloudflare-queues/)                   | Cloudflare Queues message queue                |
| [cloudflare-r2](skills/cloudflare-r2/)                           | Cloudflare R2 object storage                   |
| [cloudflare-workers](skills/cloudflare-workers/)                 | Cloudflare Workers serverless                  |
| [cloudflare-workflows](skills/cloudflare-workflows/)             | Cloudflare Workflows durable execution         |
| [coderabbit](skills/coderabbit/)                                 | CodeRabbit AI code review                      |
| [commits](skills/commits/)                                       | Conventional Commits format                    |
| [fastapi](skills/fastapi/)                                       | FastAPI web framework                          |
| [inworld](skills/inworld/)                                       | Inworld TTS API                                |
| [makefile](skills/makefile/)                                     | GNU Make build automation                      |
| [mantine-dev](skills/mantine-dev/)                               | Mantine UI components                          |
| [open-meteo](skills/open-meteo/)                                 | Open-Meteo weather API                         |
| [openapi](skills/openapi/)                                       | OpenAPI specification                          |
| [openspec](skills/openspec/)                                     | OpenSpec workflow specification                |
| [perplexity](skills/perplexity/)                                 | Perplexity AI search API                       |
| [postgresql](skills/postgresql/)                                 | PostgreSQL database                            |
| [project-creator](skills/project-creator/)                       | Project documentation scaffolding              |
| [pydantic-ai](skills/pydantic-ai/)                               | Pydantic AI agent framework                    |
| [qdrant](skills/qdrant/)                                         | Qdrant vector database                         |
| [react-testing-library](skills/react-testing-library/)           | React component testing                        |
| [refine-dev](skills/refine-dev/)                                 | Refine admin framework                         |
| [skill-master](skills/skill-master/)                             | Meta-skill for creating skills                 |
| [social-writer](skills/social-writer/)                           | Social media content creation                  |
| [tavily](skills/tavily/)                                         | Tavily AI search API                           |
| [telegram](skills/telegram/)                                     | Telegram Bot API (aiogram)                     |
| [turso](skills/turso/)                                           | Turso SQLite database                          |
| [vibekanban](skills/vibekanban/)                                 | Vibe Kanban AI agent orchestration             |
| [vite](skills/vite/)                                             | Vite build tool                                |
| [vitest](skills/vitest/)                                         | Vitest testing framework                       |

## Creating New Skills

See [skills/skill-master/](skills/skill-master/) for the skill authoring guide.

## License

MIT
