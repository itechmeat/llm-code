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

### `gateway`

- `host`, `port` control the health server bind address.
- If you bind to `127.0.0.1`, endpoints are local-only.

### `heartbeat`, `devices`

- `heartbeat.enabled` and `heartbeat.interval` start periodic tasks.
- `devices.enabled` and `devices.monitor_usb` manage device event monitoring.

## Minimal config change checklist

- [ ] Set at least one `model_list[].api_key` (or configure OAuth via `picoclaw auth login ...`).
- [ ] Set `agents.defaults.model_name` to a `model_list[].model_name` you configured.
- [ ] If running gateway externally, decide whether `gateway.host` should be `127.0.0.1` or `0.0.0.0`.
