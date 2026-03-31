# Config: `~/.picoclaw/config.json`

`picoclaw onboard` creates the config file and a workspace directory (defaults to `~/.picoclaw/workspace`).

## Key sections

### `agents.defaults`

Common fields:

- `workspace`: agent workspace root.
- `restrict_to_workspace`: when true, tools are expected to operate inside the workspace.
- `model_name`: the _alias_ you want to use (must match a `model_list[].model_name`).
- `max_tokens`, `temperature`, `max_tool_iterations`: generation limits.

Environment overrides exist for many fields (Go struct tags), e.g.:

- `PICOCLAW_AGENTS_DEFAULTS_WORKSPACE`
- `PICOCLAW_AGENTS_DEFAULTS_MODEL_NAME`

### `agents.list` and `bindings` (agent routing)

You can define multiple agents and route incoming messages to them by channel/account/context:

```json
{
  "agents": {
    "defaults": { "workspace": "~/.picoclaw/workspace", "model_name": "gpt-4o-mini" },
    "list": [
      { "id": "main", "default": true, "name": "Main Assistant" },
      { "id": "support", "name": "Support Assistant" }
    ]
  },
  "bindings": [
    {
      "agent_id": "support",
      "match": { "channel": "telegram", "account_id": "*", "peer": { "kind": "direct", "id": "user123" } }
    }
  ]
}
```

Match priority: `peer` → `parent_peer` → `guild_id` → `team_id` → `account_id` (non-wildcard) → channel wildcard → default agent. Missing `agent_id` silently falls back to the default agent.

### `gateway.log_level`

Controls gateway log verbosity. Default: `warn`. Supported: `debug`, `info`, `warn`, `error`, `fatal`. Override with `PICOCLAW_LOG_LEVEL` env var.

### `model_list` (preferred)

Each entry describes _one way_ to call a model:

- `model_name`: user-facing alias (what you set in `agents.defaults.model_name`).
- `model`: protocol-prefixed identifier, e.g. `openai/gpt-5.2`, `anthropic/claude-sonnet-4.6`.
- `api_key`, `api_base`, `proxy`: HTTP settings.
- `auth_method`: `oauth` or `token` for some providers.

Notes:

- The `model` field format is typically `[protocol/]model-id`.
  - Example: `cerebras/llama-3.3-70b`.
  - If no prefix is specified, PicoClaw treats it as `openai/`.
- Multiple entries can share the same `model_name` for round-robin load balancing.
- If you keep legacy `providers`, PicoClaw may auto-convert internally for backward compatibility.

### `channels`

Enable channels by setting `channels.<name>.enabled=true` and supplying tokens/IDs.

Important:

- `allow_from` accepts numbers or strings (it is parsed as a flexible string list).

### `tools`

Tools are configured under `tools.*` (web search, exec, cron, skills registries).
See: `tools.md`.

Recent builds also expose exec `allow_remote` support through web-facing settings. If you manage PicoClaw from the web UI/launcher, make sure remote-exec policy matches your CLI config instead of assuming the UI is read-only.

As of v0.2.3, cron command execution is also gated by exec settings. If a scheduled command stops running after upgrade, inspect `tools.exec` policy before debugging cron syntax.

### `gateway`

- `host`, `port` control the health server bind address.
- If you bind to `127.0.0.1`, endpoints are local-only.

### `heartbeat`, `devices`

- `heartbeat.enabled` and `heartbeat.interval` start periodic tasks.
- `devices.enabled` and `devices.monitor_usb` manage device event monitoring.

### `.security.yml` (sensitive data separation)

Store API keys and tokens in `~/.picoclaw/.security.yml` separate from `config.json`:

```yaml
model_list:
  gpt-5.4:
    api_keys:
      - "sk-proj-your-openai-key"
channels:
  telegram:
    token: "your-telegram-bot-token"
```

Values from `.security.yml` auto-map to config fields. If a field exists in both, `.security.yml` takes precedence. Set `chmod 600` on the file.

### `voice` (audio transcription)

`voice.model_name` lets you use any multimodal model for audio transcription instead of Groq Whisper:

```json
{
  "voice": {
    "model_name": "voice-gemini",
    "echo_transcription": false
  }
}
```

If `voice.model_name` is unset, PicoClaw falls back to Groq when a Groq API key is available.

### Workspace file hot-reload

`AGENT.md`, `SOUL.md`, `USER.md`, and `memory/MEMORY.md` are auto-detected via mtime tracking. No gateway restart needed after editing these files.

## Minimal config change checklist

- [ ] Set at least one `model_list[].api_key` (or configure OAuth via `picoclaw auth login ...`).
- [ ] Set `agents.defaults.model_name` to a `model_list[].model_name` you configured.
- [ ] If running gateway externally, decide whether `gateway.host` should be `127.0.0.1` or `0.0.0.0`.
