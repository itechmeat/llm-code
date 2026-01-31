# Changelog

All notable changes to this collection will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses date-based versioning rather than semantic versioning.

## [2026-01-31]

### Changed

- **beads** — Updated to v0.49.2 with GitLab bidirectional sync, key-value store (`bd kv`), and backend management commands (`bd backend`, `bd sync mode`)

## [2026-01-30]

### Added

- **bun** — Complete reference documentation for Bun 1.3.8 (26 reference files): HTTP server, WebSockets, SQLite, S3, Redis, FFI, shell scripting, workers, and more

### Changed

- **pydantic-ai** — Added Bedrock embedding provider for AWS Titan/Cohere models
- **tavily** — Updated to v0.7.21
- **openspec** — Updated to v1.1.0
- **vibekanban** — Updated to v0.0.166
- **agent-browser** — Updated to v0.8.5
- **refine-dev** — Updated to v8.0.0
- **open-meteo** — Corrected version to v1.4.0 (was incorrectly listed as 1.4.17)

## [2026-01-28]

### Changed

- **open-meteo** — Added Links section to README for official docs and APIs
- **openspec** — Documented spec naming convention and required task checkbox format
- **vibekanban** — Added VS Code Insiders support and worktree cleanup toggle guidance
- **pydantic-ai** — Documented `allowed_domains` for WebSearchTool and `continuous_usage_stats` model setting

## [2026-01-26]

### Added

- **project-creator** — New skill for project documentation scaffolding with templates and guides

### Changed

- **agent-browser** — Updated to v0.8.0 with Kernel provider support, cookie options, and `--ignore-https-errors`
- **beads** — Updated to v0.49.1 with new workflow flags, export options, and Dolt server checks
- **coderabbit** — Added reporting/metrics guidance and refreshed release metadata
- **openspec** — Updated to v1.0.1
- **skill-master** — Expanded skill structure guidance and added advanced features/templates
- **vibekanban** — Updated to v0.0.162 with workspace defaults, PR-based creation, slash commands, and merge guardrails

## [2026-01-25]

### Changed

- **Project structure** — Migrated to `npx add-skill` distribution model:
  - Moved skills from `.llm-code/skills/` to `skills/` in repo root (agentskills.io standard)
  - Moved agents from `.github/agents/` to `agents/` in repo root
  - Removed `.llm-code/` folder (symlink scripts: `link-assets.sh`, `link-config.sh`)
  - Updated all internal paths to relative format for portability
  - Installation now via single command: `npx add-skill itechmeat/llm-code`
  - Support for 25+ AI coding agents via add-skill CLI
- **beads** — Rebuilt for v0.49.0: new architecture (steveyegge/beads), hash-based IDs, molecules/gates, sync-branch mode, Linear/Jira import, daemon, federation; removed deprecated bv/stage-gate references
- **mantine-dev** — Updated to v8.3.13: shortened description, added version/release_date, README Links
- **openapi** — Updated to v3.2.0: shortened description, added version/release_date, README Links
- **openspec** — Updated to v0.23.0: added OPSX Commands table, Schema Management section, Project Configuration example, README Links
- **perplexity** — Updated to v0.26.0: added version/release_date, README Links (perplexity-py SDK)
- **postgresql** — Updated to v18.1: shortened description, added version/release_date, README Links
- **pydantic-ai** — Updated to v1.47.0: added Embeddings API (Embedder class), xAI native provider (XaiModel), Exa neural search tools (ExaToolset), VoyageAI/Google/Cohere embeddings, SambaNova provider, README Links
- **qdrant** — Updated to v1.16.3: shortened description, added version/release_date, README Links
- **react-testing-library** — Updated to v16.3.2: added React 19 error handlers (onCaughtError, onRecoverableError), updated peer dependency note, README Links
- **refine-dev** — Updated to v5.0.8: shortened description, added version/release_date, README Links
- **tavily** — Updated to v0.7.19: added version/release_date (tavily-python SDK)
- **telegram** — Updated to v3.24.0: added version/release_date, README Links (aiogram)
- **vibekanban** — Updated to v0.0.161: added Workspaces (Beta) reference (sessions, command bar, multi-repo, notes, terminal), Antigravity agent, context usage tracking
- **vite** — Updated to v7.3.1: added `future` deprecation warnings config, `hotUpdate` hook, `this.environment` in hooks, `build.emitLicense`, ModuleRunner API, `ssr.resolve.mainFields`
- **vitest** — Updated to v4.0.18: added OpenTelemetry support (experimental), CI/CD trace context propagation, browser mode OTEL, README Links

## [2026-01-24]

### Added

- **agent-browser** — Headless browser automation CLI for AI agents (v0.7.6)
- **inworld** — Inworld TTS API for voice cloning and audio markups (v1.5)
- **turso** — Turso SQLite database with encryption and sync (v0.4.0)

### Changed

- **skill-master** — Added Version Tracking section, Description Rules (80-150 chars target), README Links format, frontmatter field order rule
- **changelog** — Added README Synchronization section for keeping project README in sync
- **base-ui** — Added version 1.1.0, release date, shortened description, README with Links
- **beads** — Added version 0.46.0, release date, shortened description
- **coderabbit** — Shortened description, README Links section
- **commits** — Added version 1.0.0, release date 2019-02-21, shortened description, README Links section
- **fastapi** — Added version 0.128.0, release date 2025-12-27, shortened description, README Links section
- **vite** — Added version 7.2.6, release date, shortened description, README Links section

## [2026-01-20]

### Added

- **base-ui** — Base UI (React) unstyled components skill with references
- **openspec** — OpenSpec (OPSX) workflow skill with references
- **vite** — Vite project and API skill with references

### Changed

- **changelog** — Enforced English-only entries, required `CHANGELOG.md`, and clarified empty-section handling
- **coderabbit** — Added a local capture script and guidance for prompt-only reports

## [2026-01-12]

### Added

- **cloudflare-workers** — Cloudflare Workers serverless platform
- **cloudflare-images** — Cloudflare Images service
- **cloudflare-pages** — Cloudflare Pages deployment
- **cloudflare-d1** — Cloudflare D1 SQLite database
- **cloudflare-r2** — Cloudflare R2 object storage
- **cloudflare-kv** — Cloudflare Workers KV storage
- **cloudflare-queues** — Cloudflare Queues message queue
- **cloudflare-workflows** — Cloudflare Workflows durable execution
- **cloudflare-durable-objects** — Cloudflare Durable Objects stateful serverless
- **pydantic-ai** — Pydantic AI agent framework
- **tavily** — Tavily AI search API

## [2026-01-11]

### Added

- **perplexity** — Perplexity AI API for conversational search and Sonar models
- **react-testing-library** — React Testing Library for user-centric component testing
- **social-writer** — Social media content creation for X, LinkedIn, Threads, Instagram, Facebook
- **vibekanban** — Vibe Kanban orchestration platform for AI coding agents
- **vitest** — Vitest testing framework powered by Vite

### Removed

- **refine-mantine** — Merged into refine-dev skill

## [2026-01-10]

### Added

- Initial collection with skills:
  - **beads** — Beads Viewer issue tracking
  - **changelog** — Keep a Changelog 1.1.0 format specification
  - **coderabbit** — CodeRabbit AI code review with CLI, configuration, agent integration
  - **commits** — Conventional Commits 1.0.0 specification
  - **fastapi** — FastAPI web framework
  - **makefile** — GNU Make build automation
  - **mantine-dev** — Mantine UI components
  - **open-meteo** — Open-Meteo weather API
  - **openapi** — OpenAPI specification
  - **postgresql** — PostgreSQL database
  - **qdrant** — Qdrant vector database
  - **refine-dev** — Refine admin framework
  - **refine-mantine** — Refine + Mantine integration
  - **skill-master** — Meta-skill for creating skills
  - **telegram** — Telegram Bot API
