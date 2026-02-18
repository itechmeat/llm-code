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

## Incident triage patterns

- No replies: inspect pairing, mention gating, and allowlist policy first.
- Connectivity loops: validate auth mode, secure context, and gateway reachability.
- Startup failure: check gateway mode, auth for bind mode, and port conflicts.
- Channel flow failure: validate API scopes, policy gates, and pairing approvals.
- Node/browser tool failures: isolate permissions, approvals, foreground constraints, and runtime dependencies.
