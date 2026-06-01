# Troubleshooting

## “Config not found” / “Workspace not found”

- Run `picoclaw onboard` to create `~/.picoclaw/config.json` and workspace templates.
- Check with `picoclaw status`.

## “No channels enabled”

- Enable at least one channel: set `channels.<name>.enabled=true` and configure credentials.
- Start: `picoclaw gateway`.

## Model not found

Error shape:

- `model "xxx" not found in model_list or providers`

Fix:

- Ensure `agents.defaults.model_name` matches an existing `model_list[].model_name`.

## Auth issues

- `picoclaw auth status` shows whether tokens are expired.
- Re-login the provider if needed.

## Gateway not reachable from host

- If running in Docker, binding to `127.0.0.1` may make endpoints unreachable externally.
- Set `gateway.host=0.0.0.0` intentionally if you need remote access.

## Exec tool blocks commands

PicoClaw has default deny patterns for dangerous commands (delete, pipes to shell, sudo, etc.).
If something is blocked unexpectedly, adjust `tools.exec.custom_deny_patterns` or (carefully) disable defaults.

See also: `tools.md`.

## Provider/tool schema issues after v0.2.9

- If Gemini-backed MCP tools fail schema validation, update first and re-run `picoclaw mcp test`; the release line includes Gemini MCP schema sanitization fixes.
- DeepSeek vision unsupported errors are clearer. Treat them as capability mismatch signals and switch model/tool routing instead of retrying the same vision request.
- For DeepSeek/Mimo reasoning-history replay issues, verify the current release before adding custom transcript rewriting.

## WeCom callback validation fails

- Ensure the webhook port is reachable from WeCom.
- Confirm `corp_id`, `token`, `encoding_aes_key`.
- Check gateway logs (`--debug`).
