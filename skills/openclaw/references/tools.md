# OpenClaw Tools

## What matters operationally

- OpenClaw tools are policy-controlled capabilities exposed to agents and sessions.
- Effective permissions are computed by profile + provider overrides + allow/deny.
- Node and gateway tools are high-impact surfaces and need explicit gating.

## Tool governance model

- Start from `tools.profile` (`minimal`, `coding`, `messaging`, `full`).
- Narrow per provider with `tools.byProvider`.
- Apply explicit `tools.allow` / `tools.deny` (deny takes precedence).
- Use group aliases (for example `group:fs`, `group:web`, `group:nodes`) to keep policy readable.

## Onboarding default tools profile (BREAKING, v2026.3.2)

For new local installs, onboarding now defaults `tools.profile` to `messaging`. If you expect coding/system tools, set `tools.profile` explicitly (and keep it as least-privilege).

## High-impact tools and constraints

- `exec` runs shell commands; prefer bounded `timeout` and background session control.
- `process` manages running sessions (`poll`, `log`, `kill`, `remove`) and is required for non-blocking flows.
- `apply_patch` is experimental and typically workspace-scoped.
- `nodes` controls approval lifecycle and remote actions (run, camera, screen, location).
- `sessions_*` spawns and communicates with sub-agents, subject to visibility restrictions.

## Optional plugin tool: `diffs` (v2026.3.1)

OpenClaw can enable an optional read-only diff renderer that produces a gateway-hosted viewer URL and/or a PNG.

Enable:

```json5
{
  plugins: {
    entries: {
      diffs: { enabled: true },
    },
  },
}
```

Operational notes:

- Intended for view-only rendering (before/after or unified patch).
- Viewer pages are served by the gateway under `/plugins/diffs/...`.
- PNG rendering requires a Chromium-compatible browser; configure `browser.executablePath` if auto-detect fails.

v2026.3.2 adds PDF output support and quality controls for diff artifacts.

## Safety practices

- Enable loop detection to prevent repetitive no-progress tool loops.
- Require explicit consent before camera/screen recording operations.
- Treat elevated execution as exceptional and policy-gated.
- Validate node status/capabilities before invoking remote actions.
- Prefer least-privilege profile first, then add explicit allow entries.

## Plugin and binding safety (v2026.3.13)

- Channel/binding collisions in plugins now fail fast instead of silently competing at runtime.
- Treat collision errors as configuration bugs to resolve explicitly; do not work around them by retrying the same plugin load order.

## Plugin install security (v2026.3.28)

- `before_install` hook with structured request provenance, built-in scan status, and install-target metadata for external security scanners.
- `--dangerously-force-unsafe-install` as break-glass override for built-in dangerous-code false positives.
- Gateway-backed skill dependency installs blocked on dangerous-code `critical` findings unless override is set.

## Loop guards and tool identity (v2026.4.15)

- The unknown-tool stream guard is now enabled by default. Keep `tools.loopDetection.unknownToolThreshold` explicit only when you need to raise or lower the tolerance.
- Client-defined tool names can no longer normalize-collide with built-ins or with another client tool in the same request.
- Trusted local `MEDIA:` passthrough is anchored to the exact raw name of the built-in tool registered for the current run; do not assume a lookalike client tool will inherit built-in media trust.

## Skills snapshot invalidation (v2026.4.15)

- Config writes touching `skills.*` now bump the cached skills-snapshot version.
- Existing sessions still keep the snapshot that was frozen at session creation, so if a disabled skill/tool continues to be called, restart the affected session instead of repeatedly toggling config.

## MCP remote servers (v2026.3.28)

- `mcp.servers` now supports remote HTTP/SSE URLs with auth headers.
- Bundled MCP tools use provider-safe names (`serverName__toolName`).
- `streamable-http` transport selection and per-server connection timeouts available.
- Real tool results preserved from aborted/error turns unless truncation explicitly drops them.

## Browser SSRF policy (v2026.2.23)

- Config key rename: `browser.ssrfPolicy.allowPrivateNetwork` -> `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`.
- Default behavior changed when unset; treat this as a post-update verification item.
- After updating, run `openclaw doctor --fix` to migrate legacy config and re-check safety posture.

## Practical operator recipes

- Disable a risky tool globally via deny list.
- Use messaging profile for chat workflows; coding profile only where command execution is needed.
- Restrict selected providers to minimal tools when model behavior is less predictable.
- For browser automation: verify `status` before `snapshot/act` to reduce flaky sequences.
- For web search: provider `"kimi"` is supported (Moonshot); expect a two-step tool flow where results are echoed before final synthesis.
- For long-running shell tasks: use `exec(background=true)` + `process.poll` instead of blocking calls.

## Troubleshooting checklist

- If a tool is unavailable, check profile, provider override, and deny list order.
- If background tasks appear stalled, inspect process session scope and poll cadence.
- If web results seem stale, account for built-in cache interval.
- If elevated mode has no effect, verify sandbox mode and elevated policy flags.
