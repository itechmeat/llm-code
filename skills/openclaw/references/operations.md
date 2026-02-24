# OpenClaw Operations

## CLI operating model

- CLI supports profile/dev isolation and broad command families for gateway, channels, models, sessions, and security.
- Use profile scoping for multi-environment separation instead of mixing state directories manually.
- Keep status/health checks as first responders before deep troubleshooting.

## Core operator command sets

- Runtime checks: `status`, `health`, `gateway status`, `channels status --probe`.
- Config lifecycle: `configure`, `config get/set/unset`, onboarding/setup commands.
- Log inspection: `logs --follow`, structured JSON logs for automation pipelines.
- Gateway lifecycle: install/start/stop/restart/service status.
- Channel lifecycle: list/add/login/logout/remove and channel log inspection.

## Updating (v2026.2.22)

Prefer controlled, observable updates:

1. Preview the update plan (`--dry-run`).
2. Run the update (manual or wizard).
3. Validate with `doctor` + `health`.

Key commands:

```bash
openclaw update
openclaw update --dry-run
openclaw update status
openclaw update wizard
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
openclaw update --no-restart
openclaw update --json
```

Channel semantics and install method alignment:

- `stable` / `beta`: installs from npm using the matching dist-tag.
- `dev`: ensures a git checkout (default `~/openclaw`, override with `OPENCLAW_GIT_DIR`), then updates it.

Operational notes:

- Treat downgrades as risky (older versions can break config); require explicit confirmation.
- If the gateway is supervised (launchd/systemd), prefer `openclaw gateway restart` after updates.

## Automatic updates (Gateway core auto-updater)

The Gateway has an optional built-in auto-updater. It is **off by default**.

Minimal example:

```json
{
  "update": {
    "channel": "stable",
    "auto": {
      "enabled": true,
      "stableDelayHours": 6,
      "stableJitterHours": 12,
      "betaCheckIntervalHours": 1
    }
  }
}
```

Behavior summary:

- `stable`: waits `stableDelayHours`, then applies a deterministic per-install jitter up to `stableJitterHours`.
- `beta`: checks on `betaCheckIntervalHours` cadence (typically hourly).
- `dev`: does not auto-apply; use manual `openclaw update`.

After any update (manual or automated), use:

```bash
openclaw doctor
openclaw gateway restart
openclaw health
```

## Safe operations pattern

1. Validate gateway health and RPC reachability.
2. Probe channels and providers before functional tests.
3. Tail logs during rollout or incident triage.
4. Run `doctor` and security audit when warnings persist.
5. Apply config changes with explicit profile targeting.

## Security and reliability controls

- Prefer security audit workflows to detect risky defaults.
- Use deep checks only when necessary (they may trigger live provider calls).
- Keep remote gateway calls authenticated and timeout-bounded.
- Avoid Bun runtime for gateway in channel-critical environments.

## CLI output hygiene (security)

- As of v2026.2.22, `openclaw config get` redacts sensitive values before printing.
- Treat any config output as potentially sensitive anyway (paths, scopes, and non-redacted values can still reveal operational details).

## Help entry workflow

- Use docs-driven triage order: install sanity, gateway troubleshooting, logging, then doctor repairs.
- Keep this escalation order in runbooks to reduce random debugging paths.
- When incidents are unclear, collect logs + status snapshots before escalating.

## Documentation navigation strategy

- Use `start/hubs` as index to discover deep pages not visible in sidebar navigation.
- Route day-1 issues to Getting Started/Quickstart/Help hubs first.
- Route operational incidents to Gateway + Operations hub branch.

## Troubleshooting command ladder

1. `openclaw status`
2. `openclaw gateway status`
3. `openclaw logs --follow`
4. `openclaw doctor`
5. `openclaw channels status --probe`

## Paired-device hygiene commands (v2026.2.19)

- Remove a specific paired entry: `openclaw devices remove <device-id>`.
- Remove via gateway/device-pair flow: `device.pair.remove`.
- Bulk cleanup with confirmation: `openclaw devices clear --yes`.
- Include pending requests during cleanup when needed: `openclaw devices clear --yes --pending`.
- Run cleanup before re-pairing when stale pair records cause routing/auth anomalies.

## Incident triage patterns

- No replies: inspect pairing, mention gating, and allowlist policy first.
- Connectivity loops: validate auth mode, secure context, and gateway reachability.
- Startup failure: check gateway mode, auth for bind mode, and port conflicts.
- Channel flow failure: validate API scopes, policy gates, and pairing approvals.
- Node/browser tool failures: isolate permissions, approvals, foreground constraints, and runtime dependencies.
