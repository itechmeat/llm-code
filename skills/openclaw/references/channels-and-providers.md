# OpenClaw Channels and Providers

## Channels overview

- OpenClaw supports many chat surfaces in parallel and routes by chat/channel context.
- Core channels include WhatsApp, Telegram, Slack, Discord, Signal, IRC, and WebChat.
- Several integrations are plugin-delivered (for example Teams, Matrix, LINE, Mattermost).
- iMessage legacy path is deprecated; BlueBubbles is the preferred approach.

## Pairing and trust model

- Some channels require explicit pairing flows (for example QR/token onboarding).
- DM pairing and allowlist controls are key safety boundaries.
- Group behavior differs by platform and must be validated per channel.

## Operations notes

- Text support is broad; media/reactions capabilities vary by connector.
- Multi-channel operation is expected; keep channel-specific routing explicit.
- Maintain channel troubleshooting playbooks per connector family.

## Practical channel strategy

- Start with Telegram for fastest bootstrap and operator validation.
- Add WhatsApp only after pairing and persistence paths are verified.
- For iMessage workflows, standardize on BlueBubbles and document known feature gaps.

## Provider options and model naming

- Providers span hosted APIs and local runtimes (for example OpenAI/Anthropic plus Ollama/vLLM).
- The effective model selector uses `provider/model` naming.
- OpenClaw supports both direct providers and gateway-style aggregation providers.

## Configuration baseline

- Authenticate provider credentials during onboarding flow.
- Set default model via `agents.defaults.model.primary`.
- Keep environment-specific provider choices explicit to avoid accidental model drift.

## Provider operations guidance

- Begin with one stable primary provider before introducing alternates.
- Add local providers only after resource and latency constraints are validated.
- Treat provider credentials as secrets and rotate through your secret-management process.

## Telegram channel playbook

- Configure bot token, DM policy, and group mention policy before production use.
- Keep numeric user IDs in allowlists; avoid username-only ACLs.
- Treat DM policy and group policy as independent controls and test both paths.
- If non-mention group behavior is required, align Telegram privacy mode/admin state accordingly.
- Use pairing approvals and channel status probes during onboarding validation.
