# OpenClaw Installation

Use this reference only when OpenClaw is not installed yet or when migrating environments.

## Supported install paths

- Official installer script (recommended for fresh hosts).
- Global `npm`/`pnpm` install for managed environments.
- Source build path for contributors.

## Prerequisites

- Node 22+ runtime.
- Windows deployments should prefer WSL2 for gateway compatibility.
- `pnpm` users must approve build scripts when prompted.

## Post-install validation

1. Verify runtime health and status.
2. Open dashboard/control UI.
3. Confirm global binary path resolution.
4. Run diagnostics (`doctor`) if startup is inconsistent.

## Platform notes

- Node runtime is preferred for gateway workloads.
- Bun is not recommended for channel-critical gateway usage.
- Keep config/state paths explicit in automation.

## Migration / maintenance

- Re-run onboarding/configuration when environment changes.
- Use service install/repair commands for daemon lifecycle alignment.

## Discord voice dependency note (v2026.2.22)

- Discord voice now treats `@discordjs/opus` as an optional dependency.
- If native Opus builds fail, install/update should no longer hard-fail; runtime decoding falls back to `opusscript`.
- If you still see voice failures: validate Node toolchain/native build prerequisites on the host and confirm the voice path in your channel configuration.
