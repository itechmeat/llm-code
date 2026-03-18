# OpenClaw Operations

## CLI operating model

- CLI supports profile/dev isolation and broad command families for gateway, channels, models, sessions, and security.
- Use profile scoping for multi-environment separation instead of mixing state directories manually.
- Keep status/health checks as first responders before deep troubleshooting.

## Core operator command sets

- Runtime checks: `status`, `health`, `gateway status`, `channels status --probe`.
- Config lifecycle: `configure`, `config file`, `config get/set/unset`, onboarding/setup commands.
- Log inspection: `logs --follow`, structured JSON logs for automation pipelines.
- Gateway lifecycle: install/start/stop/restart/service status.
- Channel lifecycle: list/add/login/logout/remove and channel log inspection.

Recommended local iteration loop after manual config edits:

1. `openclaw config file`
2. `openclaw config validate`
3. `openclaw doctor`
4. `openclaw gateway restart` when touching gateway infra settings or when hot-reload behavior is unclear.

### Config file path (v2026.3.1)

Print the active config file location:

```bash
openclaw config file
```

Resolution rule (per docs): uses `OPENCLAW_CONFIG_PATH` if set; otherwise uses the default config location.

### Config validation (v2026.3.2)

Validate a config file **before** starting the gateway:

```bash
openclaw config validate
openclaw config validate --json
```

Use this as a first step when the gateway fails fast on invalid config keys or paths.

As of v2026.3.11, top-level `config.set`, `config.patch`, and `config.apply` errors surface multiple validation issues in the summary. Read the first few issues carefully before making another write attempt.

### Cron/heartbeat lightweight context (v2026.3.1)

When you want automation turns to run with a smaller bootstrap payload:

- Cron agent turns: `--light-context`
- Heartbeat: `agents.*.heartbeat.lightContext`

Use this when bootstrap files are large and you want to reduce token/context overhead for scheduled runs.

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
- After upgrading to v2026.3.11+, run `openclaw doctor --fix` to migrate legacy cron storage and legacy cron notify/webhook metadata before trusting scheduled delivery.
- For `v2026.3.13-1`, remember that the `-1` suffix is only a GitHub release/tag recovery marker; runtime versioning still tracks `2026.3.13`.

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

1. Validate config path and schema before rollout.
2. Validate gateway health and RPC reachability.
3. Probe channels and providers before functional tests.
4. Tail logs during rollout or incident triage.
5. Run `doctor` and security audit when warnings persist.
6. Apply config changes with explicit profile targeting.

## Security and reliability controls

- Prefer security audit workflows to detect risky defaults.
- Use deep checks only when necessary (they may trigger live provider calls).
- Keep remote gateway calls authenticated and timeout-bounded.
- Avoid Bun runtime for gateway in channel-critical environments.
- Child commands launched from OpenClaw now carry `OPENCLAW_CLI`; use that marker in wrapper scripts when you need different behavior for CLI-spawned subprocesses.

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

## Patch-level triage additions (v2026.3.13-1)

- If compaction quality regresses after update, inspect post-compaction sanity using full-session token counts before tuning prompt/summary policies.
- If session continuity breaks after reset flows, verify whether `lastAccountId` / `lastThreadId` were preserved instead of assuming channel routing drift.
- If gateway/UI requests look stuck, check for bounded unanswered client requests in logs rather than waiting indefinitely.

## Cron migration note (BREAKING, v2026.3.11)

- Isolated cron delivery no longer falls back to ad hoc agent sends or main-session summaries.
- Legacy notify/webhook metadata should be migrated with `openclaw doctor --fix` after upgrade.
- If scheduled jobs appear "silent" after updating, inspect cron storage and doctor output before changing routing or agent policy.
