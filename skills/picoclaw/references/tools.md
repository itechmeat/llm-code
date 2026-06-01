# Tools configuration

Tools are configured under `tools` in `~/.picoclaw/config.json`.

Sections:

- `tools.web`: search/fetch
- `tools.exec`: shell execution guardrails
- `tools.cron`: scheduler limits
- `tools.skills`: skill registries (e.g. ClawHub)

## MCP management (v0.2.8)

Recent PicoClaw builds add CLI-level MCP management commands for inspecting and operating configured servers:

- `picoclaw mcp list`
- `picoclaw mcp show`
- `picoclaw mcp add`
- `picoclaw mcp edit`
- `picoclaw mcp remove`
- `picoclaw mcp test`

Operational notes:

- Treat `mcp test` as the first-line check before blaming agent/tool routing.
- MCP init failures are surfaced to command handlers more clearly in the newer release line, so a failed test/init is now a meaningful signal rather than silent flakiness.
- Local stdio command paths are normalized and home-directory paths are expanded, which reduces config drift across machines.

## MCP/tool feedback updates (v0.2.9)

- The config web UI has an MCP section, so operators can inspect or edit MCP-related settings without leaving the web flow.
- MCP streamable HTTP support and Gemini MCP schema sanitization were fixed; re-run `picoclaw mcp test` after upgrade before blaming server-side MCP schemas.
- `tool_feedback` defaults now include `pretty_print` and `disable_escape_html`. Review any UI/channel code that assumed raw escaped HTML or compact JSON output.
- Edit-file diff preview support improves generated-edit review. Prefer previewing changes before enabling tools that can modify files.

## Web tools

Supported switches (from project docs):

- Brave: `enabled`, `api_key`, `max_results`
- DuckDuckGo: `enabled`, `max_results`
- Perplexity: `enabled`, `api_key`, `max_results`
- `tools.web.proxy`: proxy for web tools

## Exec tool (dangerous command blocking)

Config keys:

- `tools.exec.enable_deny_patterns` (default true)
- `tools.exec.custom_deny_patterns` (regex list)
- `allow_remote` support is now surfaced in web settings, so remote-exec policy can be managed consistently across CLI and web flows.

Docs describe default blocked patterns including:

- destructive deletes (`rm -rf`, `del /f/q`, ...)
- `format`, `mkfs`, `dd if=...`, writes to `/dev/sd*`
- `shutdown`/`reboot`
- command substitution (`$()`, backticks)
- pipes to shell (`| sh`, `| bash`)
- privilege escalation (`sudo`, `chmod`, `chown`)
- remote ops (`curl | sh`, `ssh`)
- package managers and container commands

## Security posture update (v0.2.2)

- PicoClaw hardened unauthenticated tool-exec paths.
- Treat remote execution as an explicit policy decision; do not rely on older implicit behavior.

## Exec and subagent updates (v0.2.3)

- Exec controls are now used to gate cron command execution as well as direct command flows.
- Whitelist path checks are normalized for symlinked allowed roots, which reduces false negatives in workspace layouts that rely on symlinks.
- `SpawnStatusTool` is available for reporting subagent status back into the agent/tool surface.

## Cron tool

- `tools.cron.exec_timeout_minutes` controls how long scheduled executions may run.
- Scheduled command execution now depends on exec policy, so review `tools.exec` when cron jobs need shell access.

## Skills tool (registries)

Configure registries under:

- `tools.skills.registries.<name>.*`

Example registry in docs:

- `clawhub`: `enabled`, `base_url`, `search_path`, `skills_path`, `download_path`

## Environment variable overrides

Docs define an override format for tools:

- `PICOCLAW_TOOLS_<SECTION>_<KEY>`

Example:

- `PICOCLAW_TOOLS_WEB_DUCKDUCKGO_ENABLED=true`

Note: array-type environment variables are not supported for tools; set those in the config file.

## Serial hardware tool (v0.2.8)

PicoClaw now ships a cross-platform serial tool and wires it into runtime/dashboard flows.

- Treat serial access as an explicit operator capability; do not enable it casually on hosts where attached hardware should stay out of scope.
- Re-check exec/remote policy and agent permissions when exposing serial operations through gateway/web management surfaces.
