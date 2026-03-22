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

## Available Skills (46)

Each skill follows the [agentskills.io](https://agentskills.io) specification.

| Skill                                                    | Description                                   |
| -------------------------------------------------------- | --------------------------------------------- |
| [base-ui](skills/base-ui/)                               | Base UI unstyled React components             |
| [beads](skills/beads/)                                   | Beads distributed git-backed issue tracker    |
| [bun](skills/bun/)                                       | Bun JavaScript/TypeScript runtime and toolkit |
| [changelog](skills/changelog/)                           | Keep a Changelog format                       |
| [coderabbit](skills/coderabbit/)                         | CodeRabbit AI code review                     |
| [commits](skills/commits/)                               | Conventional Commits format                   |
| [deps-dev](skills/deps-dev/)                             | deps.dev API v3 package version lookup        |
| [fastapi](skills/fastapi/)                               | FastAPI web framework                         |
| [github-stars-organizer](skills/github-stars-organizer/) | GitHub stars and lists organizer              |
| [inworld](skills/inworld/)                               | Inworld TTS API                               |
| [k8s-cluster-api](skills/k8s-cluster-api/)               | Kubernetes Cluster API v1.12                  |
| [makefile](skills/makefile/)                             | GNU Make build automation                     |
| [mantine-dev](skills/mantine-dev/)                       | Mantine UI components                         |
| [open-meteo](skills/open-meteo/)                         | Open-Meteo weather API                        |
| [openclaw](skills/openclaw/)                             | OpenClaw local AI assistant stack             |
| [openapi](skills/openapi/)                               | OpenAPI specification                         |
| [openspec](skills/openspec/)                             | OpenSpec workflow specification               |
| [perplexity](skills/perplexity/)                         | Perplexity AI search API                      |
| [picoclaw](skills/picoclaw/)                             | PicoClaw Go AI assistant runbook              |
| [pipecat](skills/pipecat/)                               | Pipecat realtime voice/multimodal bots        |
| [postgresql](skills/postgresql/)                         | PostgreSQL database                           |
| [pgvector](skills/pgvector/)                             | pgvector Postgres extension                   |
| [project-creator](skills/project-creator/)               | Project documentation scaffolding             |
| [pydantic-ai](skills/pydantic-ai/)                       | Pydantic AI agent framework                   |
| [qdrant](skills/qdrant/)                                 | Qdrant vector database                        |
| [react-testing-library](skills/react-testing-library/)   | React component testing                       |
| [refine-dev](skills/refine-dev/)                         | Refine admin framework                        |
| [seaweedfs](skills/seaweedfs/)                           | SeaweedFS distributed storage                 |
| [skill-master](skills/skill-master/)                     | Agent Skills authoring and evaluation         |
| [social-writer](skills/social-writer/)                   | Social media content creation                 |
| [tavily](skills/tavily/)                                 | Tavily AI search API                          |
| [telegram](skills/telegram/)                             | Telegram Bot API (aiogram)                    |
| [turso](skills/turso/)                                   | Turso SQLite database                         |
| [vibekanban](skills/vibekanban/)                         | Vibe Kanban AI agent orchestration            |
| [vite](skills/vite/)                                     | Vite build tool                               |
| [vitest](skills/vitest/)                                 | Vitest testing framework                      |
| [zvec](skills/zvec/)                                     | SQLite for vectors                            |

## Creating New Skills

See [skills/skill-master/](skills/skill-master/) for the skill authoring guide.

## License

MIT
