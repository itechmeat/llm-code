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

## Safety practices

- Enable loop detection to prevent repetitive no-progress tool loops.
- Require explicit consent before camera/screen recording operations.
- Treat elevated execution as exceptional and policy-gated.
- Validate node status/capabilities before invoking remote actions.
- Prefer least-privilege profile first, then add explicit allow entries.

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
