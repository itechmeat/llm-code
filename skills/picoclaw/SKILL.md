---
name: picoclaw
description: "PicoClaw Go AI assistant. Covers CLI ops, config.json, channels, auth, skills, gateway. Use when running the PicoClaw CLI, configuring models/tools/gateway in config.json, or operating channels and authentication. Keywords: picoclaw, onboard, gateway, model_list."
metadata:
  version: "v0.2.4"
  release_date: "2026-03-25"
---

# PicoClaw

PicoClaw is an ultra-lightweight AI assistant written in Go. This skill is a practical operator playbook for running the CLI, configuring `~/.picoclaw/config.json`, and operating `gateway` + channels.

## Links

- [Documentation](https://github.com/sipeed/picoclaw/tree/main/docs)
- [Releases](https://github.com/sipeed/picoclaw/releases)
- [GitHub](https://github.com/sipeed/picoclaw)

## Quick navigation

- Getting started + common commands: `references/quickstart.md`
- Config (`model_list`, tools, gateway, channels, bindings): `references/config.md`
- Tools (web search, exec guardrails, registries): `references/tools.md`
- Auth flows (OpenAI OAuth, Google Antigravity OAuth, token): `references/auth.md`
- Gateway operations (health/ready, cron, heartbeat, voice): `references/gateway.md`
- Channels (Telegram/Discord/WeCom/Feishu/OneBot/etc): `references/channels.md`
- Skills management (install/list/remove, channel commands): `references/skills.md`
- Hook system (observers, interceptors, approvers): `references/hooks.md`
- Cron scheduling via CLI: `references/cron.md`
- Migration notes: `references/migration.md`
- Troubleshooting: `references/troubleshooting.md`

## When to use

Use when you need to:

- Bootstrap PicoClaw on a host (onboard → config → run)
- Switch providers/models via `model_list`
- Run the agent in CLI mode or operate `gateway`
- Enable chat channels (Telegram/Discord/Slack/WeCom/...)
- Configure tools (web search, exec deny patterns, skills registries)
- Install/remove skills into the workspace
- Use skill channel commands (`/list skills`, `/use <skill>`)
- Configure hook system (observers, interceptors, approvers)
- Configure agent bindings (route messages to different agents)
- Schedule recurring jobs (cron)

## Recipes

### 1) Initialize + verify

- Create initial config and workspace templates:
  - `picoclaw onboard`
- Verify what’s configured:
  - `picoclaw status`

### 2) Chat from CLI

- One-shot:
  - `picoclaw agent -m "Hello"`
- Interactive:
  - `picoclaw agent`

### 3) Run gateway (channels + cron + health)

- Start gateway:
  - `picoclaw gateway`
- Debug logs:
  - `picoclaw gateway --debug`

### 4) Manage auth

- OpenAI OAuth (optionally device-code for headless):
  - `picoclaw auth login --provider openai`
  - `picoclaw auth login --provider openai --device-code`
- Google Antigravity OAuth:
  - `picoclaw auth login --provider google-antigravity`
- Check status / list models:
  - `picoclaw auth status`
  - `picoclaw auth models`

### 5) Install skills

- List installed skills:
  - `picoclaw skills list`
- Install from GitHub repo slug:
  - `picoclaw skills install sipeed/picoclaw-skills/weather`
- Install from registry:
  - `picoclaw skills install --registry clawhub github`

### 6) Add a scheduled job

- Create a cron job:
  - `picoclaw cron add --name "Daily report" --cron "0 9 * * *" --message "Summarize my inbox"`
- List jobs:
  - `picoclaw cron list`

## Critical safety notes

- Do not commit real API keys or OAuth tokens into a repo; keep them in `~/.picoclaw/` only.
- Be cautious enabling the exec tool; keep deny patterns enabled unless you fully trust the environment.
- Exposing gateway to `0.0.0.0` makes health endpoints reachable from the network; do that only intentionally.

## Release Highlights (v0.2.4)

- **Hook system**: in-process and out-of-process hooks (JSON-RPC over stdio) with observer, LLM interceptor, tool interceptor, and tool approver stages. Configurable via `hooks` in config.
- **Agent bindings**: route incoming messages to different agents by channel/account/context via `bindings` config section.
- **Skill channel commands**: `/list skills`, `/use <skill> <message>`, `/use <skill>` (arm for next message), `/use clear`.
- **Configurable log level**: `gateway.log_level` (debug/info/warn/error/fatal) in config or `PICOCLAW_LOG_LEVEL` env var.
- **Voice transcription model**: `voice.model_name` lets you use any multimodal model for audio transcription; Groq Whisper remains as fallback.
- **Security config separation**: `.security.yml` file for storing API keys/tokens separate from `config.json`.
- **Workspace file hot-reload**: `AGENT.md`, `SOUL.md`, `USER.md`, `MEMORY.md` are auto-detected via mtime tracking — no restart needed.
- SubTurn error handling and logging improved. Security config precedence fixed during migration.

## Links

- Upstream repo (for releases/issues): https://github.com/sipeed/picoclaw
