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

## Container probe endpoints (v2026.3.1)

For Docker/Kubernetes liveness/readiness checks, the gateway exposes unauthenticated probe endpoints:

- Liveness: `/healthz` (alias: `/health`)
- Readiness: `/readyz` (alias: `/ready`)

Use these for process/container probes only; for authenticated deeper checks, use `openclaw health` and channel probe commands.

## Bind/auth rules you must enforce

- Port precedence: CLI flag, then env var, then config, then default.
- Bind precedence follows explicit override before config default.
- Non-loopback binds must be protected by token/password auth.
- Clients must supply auth even when reaching gateway through SSH tunnel.
- **(v2026.3.7)** When both `gateway.auth.token` and `gateway.auth.password` are configured (including SecretRefs), set `gateway.auth.mode` to `token` or `password` explicitly. Omitting it causes startup/pairing/TUI failures.
- SecretRef is supported for `gateway.auth.token` with auth-mode guardrails.

## Remote access patterns

- Preferred: private overlay network (for example Tailscale/VPN).
- Fallback: SSH local tunnel to loopback gateway endpoint.
- Keep public exposure minimal and pair remote access with strict auth.
- For remote onboarding on macOS, expect a shared gateway token flow when paired-device auth is not sufficient; retrieve the token from the gateway host instead of guessing or reusing stale local credentials.

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
- Control UI token auth is intentionally session-scoped in the browser; refresh in the same tab should survive, but operators should expect to re-authenticate after a fresh browser session.

## Model auth status (v2026.4.15)

- Control UI now exposes a model-auth status card showing OAuth token health and provider rate-limit pressure.
- The backing `models.authStatus` gateway method strips credentials and caches results briefly (60s) for operator visibility without exposing secrets.
- Use this card during incident triage before re-running onboarding flows or manually rotating tokens.

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
- For direct HTTPS deployments, you can enable HSTS via `gateway.http.securityHeaders.strictTransportSecurity`.
- Enforce strict file permissions for config/state and enable sensitive-data redaction in logs.
- Browser-originated WebSocket connections must pass origin validation even behind `trusted-proxy`; never rely on forwarded headers as a substitute for allowed-origin policy.

## Auth and media hardening notes (v2026.4.15)

- HTTP bearer auth is now resolved per request on the server and upgrade paths, so secret rotation via reload/hot config applies immediately instead of waiting for a gateway restart.
- `/mcp` bearer checks now use constant-time comparison and reject non-loopback browser-origin requests before the auth gate runs.
- Webchat audio/media embedding enforces `localRoots` containment and rejects remote-host `file://` URLs.

## New security and reachability notes (v2026.3.11-v2026.3.13)

- Scope-limited probe RPC should be treated as degraded reachability, not full health, when downstream permissions or visibility are incomplete.
- Gateway/client request handling now bounds unanswered client requests more aggressively; if UI/API calls appear to hang, inspect gateway logs for timed-out pending requests instead of assuming the request is still live.
- If local `gateway.auth.*` uses SecretRefs, treat missing secret resolution as a hard failure and fix the secret source before retrying startup.

## Recovery release notes (v2026.3.13-1)

- The `v2026.3.13-1` tag is a release-path recovery tag; do not treat the `-1` suffix as a new npm/runtime version line.
- If the control UI is reached through an insecure compatibility path, shared-auth behavior has been restored; still prefer loopback or HTTPS/Tailscale contexts for normal operations.
- Connect failures are classified more explicitly now, so incident triage should distinguish auth/connectivity failures from generic UI breakage.
- Docker deployments can set `OPENCLAW_TZ` to keep gateway/container timezone behavior explicit.

## New audit finding: `gateway.http.no_auth` (v2026.2.19)

- Trigger condition: `gateway.auth.mode="none"` with reachable Gateway HTTP APIs.
- Risk model: loopback exposure is warning-level; remote/public exposure is critical.
- Operational rule: never run no-auth mode on non-loopback endpoints.
- Remediation: re-enable auth (token/password), revert to loopback bind, and re-run audit checks.

## iOS wake/reconnect behavior (v2026.2.19)

- Gateway can trigger APNs wake before `nodes.invoke` for disconnected iOS nodes.
- Silent-push wake helps restore gateway sessions while app is backgrounded.
- If invoke reliability drops, validate APNs registration/signing first, then run push-test pipeline.
