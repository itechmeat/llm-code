# OpenClaw Gateway

## Role of the gateway

- The gateway is the always-on control plane and message routing hub.
- It multiplexes WebSocket control, HTTP APIs, UI surfaces, and channel connectivity.
- Default posture is local-first bind with authentication required.

## Startup and baseline checks

- Start with explicit port and optional verbose mode during bring-up.
- Confirm runtime health (`running` + RPC probe success) before channel testing.
- Probe channel readiness separately after gateway health passes.
- Monitor logs continuously during initial setup and rollout changes.

## Bind/auth rules you must enforce

- Port precedence: CLI flag, then env var, then config, then default.
- Bind precedence follows explicit override before config default.
- Non-loopback binds must be protected by token/password auth.
- Clients must supply auth even when reaching gateway through SSH tunnel.

## Remote access patterns

- Preferred: private overlay network (for example Tailscale/VPN).
- Fallback: SSH local tunnel to loopback gateway endpoint.
- Keep public exposure minimal and pair remote access with strict auth.

## Configuration levers

- Use dedicated config and state paths for profile isolation.
- Keep reload mode intentional (`hot`, `off`, `restart`, `hybrid`).
- For multi-gateway setups, isolate port, state dir, config path, and workspace.

## Operations checklist

- Health: gateway status + deep/json where needed.
- Readiness: channel probe + health endpoints.
- Lifecycle: install/restart/stop under launchd or systemd supervision.
- Recovery: on event-sequence gaps, refresh state before continuing actions.

## Failure signatures and fixes

- Bind refused without auth: add token/password before non-loopback bind.
- Address in use: resolve competing process or change port.
- Start blocked by mode mismatch: align gateway mode in config.
- Unauthorized connect: verify token/password parity between client and gateway.

## Do / Don’t

- Do run one gateway per host by default.
- Do supervise the process for auto-restart and persistence.
- Don’t rely on unauthenticated remote bindings.
- Don’t continue workflows after event gaps without explicit state refresh.

## Web surfaces and exposure model

- Control UI is served by gateway on the same endpoint surface and can be path-prefixed.
- Keep same-origin WS defaults unless explicit trusted origins are required.
- Tailscale serve/funnel modes are preferred for remote web exposure over direct public bind.
- Funnel mode should be paired with strong password auth and explicit exposure review.

## Control UI operations

- Control UI is a first-class operations surface for chat, channels, sessions, cron, skills, nodes, and config.
- Remote browser/device access follows pairing trust workflow; new devices require explicit approval.
- Prefer secure contexts (loopback or HTTPS via Tailscale Serve) to preserve device-identity protections.
- Use `config.apply` workflows with validation and conflict guards for safer live config edits.

## Tailscale modes and policy

- `serve`: recommended tailnet HTTPS proxy while gateway stays loopback-bound.
- `funnel`: public exposure mode and must use password-based auth.
- `tailnet` bind: direct tailnet endpoint without serve/funnel proxy behavior.
- If explicit credentials are required even on Serve, disable identity-header auth allowance.

## Configuration and reload behavior

- Config is schema-strict; invalid keys/types can block gateway startup.
- Use full replace (`config.apply`) for controlled rollouts and patch merge (`config.patch`) for targeted updates.
- Patch semantics: object keys merge, arrays replace, `null` deletes keys.
- Gateway server and infra-level settings typically require restart, while many runtime settings hot-apply.
- Include/env substitution errors should be treated as startup blockers and validated early.

## Remote access pattern

- Recommended remote pattern keeps gateway loopback-bound and accesses it over SSH tunnel or Tailscale Serve.
- Remote CLI mode should carry explicit URL + credentials configuration.
- When explicit `--url` is used in CLI calls, always pass auth credentials explicitly as well.
- Nodes remain WS clients; they do not host gateway service state.

## Security hardening essentials

- Assume prompt injection and hostile input are possible on every channel.
- Apply identity controls first (pairing/allowlists), then scope controls (mentions/tools/sandbox), then model policy.
- Keep gateway loopback-bound by default and require strong token/password for non-loopback access.
- Disable insecure control UI auth downgrades in production environments.
- Enforce strict file permissions for config/state and enable sensitive-data redaction in logs.

## New audit finding: `gateway.http.no_auth` (v2026.2.19)

- Trigger condition: `gateway.auth.mode="none"` with reachable Gateway HTTP APIs.
- Risk model: loopback exposure is warning-level; remote/public exposure is critical.
- Operational rule: never run no-auth mode on non-loopback endpoints.
- Remediation: re-enable auth (token/password), revert to loopback bind, and re-run audit checks.

## iOS wake/reconnect behavior (v2026.2.19)

- Gateway can trigger APNs wake before `nodes.invoke` for disconnected iOS nodes.
- Silent-push wake helps restore gateway sessions while app is backgrounded.
- If invoke reliability drops, validate APNs registration/signing first, then run push-test pipeline.
