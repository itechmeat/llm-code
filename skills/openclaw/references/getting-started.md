# OpenClaw Getting Started

This reference assumes OpenClaw is already installed.

If not installed, use `references/installation.md` first.

## Platform and runtime guidance

- Prefer Node runtime for gateway workloads.
- Avoid Bun for gateway/channel-critical deployments due to known connector instability.
- On Windows, prefer WSL2 for gateway operation.
- Treat mobile/macOS apps as node/companion surfaces, not gateway replacements.

## Service deployment patterns

- Recommended bootstrap: `openclaw onboard --install-daemon`.
- Alternative lifecycle path: `openclaw gateway install` and service-specific commands.
- Use `openclaw doctor` for repair/migration and configuration drift checks.

## Minimal first-run path

1. Run onboarding with daemon install.
2. Verify gateway status.
3. Open dashboard/control UI and run first chat.

## Fast verification checklist

- `openclaw gateway status` returns healthy runtime.
- `openclaw dashboard` opens local control surface successfully.
- Optional: send a test message only after channel provisioning is complete.

## Onboarding decision points

- Choose CLI wizard for full control of gateway/workspace/channels/skills.
- Choose macOS app for guided local first run on Mac hardware.
- For custom providers, capture endpoint type, base URL, API key, model ID, alias, and endpoint ID explicitly.

## Onboarding output expectations

- Provisioned runtime with gateway and workspace defaults.
- Channel and skill baseline from wizard choices.
- Reusable provider endpoint entries for multi-endpoint environments.

## CLI wizard execution map

1. Configure model/provider and default model.
2. Select workspace path and bootstrap files.
3. Configure gateway port/bind/auth/remote exposure.
4. Select channels and pairing prompts.
5. Install daemon/service unit.
6. Run health checks.
7. Install recommended skills.

## Wizard pitfalls to avoid

- Re-running wizard is non-destructive unless reset is explicitly chosen.
- Invalid/legacy config should be repaired with `openclaw doctor` before rerun.
- Remote mode configures local client targeting only; it does not provision remote host.
- `--json` does not imply non-interactive mode; use `--non-interactive` explicitly.

## macOS app onboarding specifics

- First-run flow includes local network/security prompts and explicit local-vs-remote gateway choice.
- Remote gateway mode requires credentials prepared on the remote host.
- App onboarding requests OS permissions for automation/media/device integrations.
- Dedicated onboarding chat session is created to bootstrap user guidance separately from normal chats.

## Personal assistant bootstrap

- Recommended pattern uses a dedicated assistant number and strict sender allowlist.
- Start conservative: keep proactive heartbeat disabled until trust and safety prompts are tuned.
- Validate control UI access and token-based auth before external messaging tests.

## Workspace and session defaults

- Workspace acts as persistent memory context and can be managed as a git repository.
- Bootstrap creates core identity/tools/persona files for first-run guidance.
- Session reset/compact flows should be part of standard operator controls.

## Day-1 safety baseline

- Enforce channel allowlist constraints before exposing assistant to contacts.
- Require mention-based activation in groups for noise reduction.
- Use per-sender session scope for cleaner isolation and incident triage.

## Quickstart acceptance criteria

- Gateway is running, authentication is configured, and control UI is reachable.
- Quick validation uses node version, gateway status, and dashboard open checks.
- Message send checks are optional and only valid after channel provisioning.
