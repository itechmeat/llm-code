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

### Discord thread-bound sessions (v2026.3.1)

Discord can bind a thread to a session/subagent target so follow-up messages keep routing consistently.

Commands:

- `/focus <target>`
- `/unfocus`
- `/session idle <duration|off>`
- `/session max-age <duration|off>`

Config shape (from Discord channel docs):

```json5
{
  session: {
    threadBindings: { enabled: true, idleHours: 24, maxAgeHours: 0 },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false,
      },
    },
  },
}
```

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

## Provider/runtime updates (v2026.4.15)

- Anthropic defaults and `opus` aliases now point bundled image-understanding flows at Claude Opus 4.7.
- The bundled `google` plugin now supports TTS with voice selection plus WAV/PCM output paths.
- GitHub Copilot is available as a memory-search embedding provider, which is useful when memory search should align with Copilot-authenticated environments.
- Bundled Microsoft and ElevenLabs speech providers now auto-enable for TTS-oriented setups.

## Telegram channel playbook

- Configure bot token, DM policy, and group mention policy before production use.
- Keep numeric user IDs in allowlists; avoid username-only ACLs.
- Treat DM policy and group policy as independent controls and test both paths.
- If non-mention group behavior is required, align Telegram privacy mode/admin state accordingly.
- Use pairing approvals and channel status probes during onboarding validation.

### Telegram DM topics (v2026.3.1)

In addition to group forum topics, Telegram supports per-DM "direct" configuration with optional topics.

Config surface (from config schema/types):

- `channels.telegram.direct.<chatId>.topics.<threadId>.*`
- `channels.telegram.direct.<chatId>.requireTopic` (require a topic when topics are enabled)

Minimal example:

```json5
{
  channels: {
    telegram: {
      direct: {
        "123456789": {
          requireTopic: true,
          topics: {
            "1": { enabled: true, skills: ["calendar"], systemPrompt: "Personal admin" },
          },
        },
      },
    },
  },
}
```

### Telegram per-topic agent routing (v2026.3.7)

Forum group topics and DM topics support per-topic `agentId` overrides so each topic routes to a dedicated agent with an isolated session.

### ACP persistent channel bindings (v2026.3.7)

- Durable Discord channel and Telegram topic binding storage that survives restarts.
- ACP `spawn --thread here|auto` for Telegram topic binding.
- Actionable Telegram approval buttons with prefixed approval-id resolution.
- Successful bind confirmations are pinned in-topic.

### Slack DM typing feedback (v2026.3.7)

`channels.slack.typingReaction` enables reaction-based processing status in Socket Mode DMs when native assistant typing is unavailable.

### Slack interactive replies (v2026.3.13)

- Slack now supports opt-in interactive reply directives for richer response handling in supported flows.
- Treat this as a channel-specific behavior toggle to validate in staging before broad rollout, especially if you already depend on custom Slack reply formatting.

### Slack exec approvals (v2026.3.28)

- Native Slack approval routing with approver authorization so exec approval prompts stay in Slack instead of falling back to Web UI or terminal.

### WhatsApp reactions (v2026.3.28)

- Agents can react with emoji on incoming WhatsApp messages for more natural conversational interactions.

### LINE outbound media (v2026.3.28)

- LINE image, video, and audio outbound sends on the LINE-specific delivery path with explicit preview/tracking handling for videos.

### Matrix improvements (v2026.3.28)

- `channels.matrix.historyLimit` for optional room history context in group triggers, with per-agent watermarks and retry-safe snapshots.
- Per-DM `threadReplies` overrides with thread session isolation.
- `channels.matrix.proxy` for routing Matrix traffic through HTTP(S) proxy.

### Discord allowBots mention gating (v2026.3.7)

`allowBots: "mentions"` accepts bot-authored messages only when they mention the bot.

### Mattermost model picker (v2026.3.7)

Interactive `/oc_model` and `/oc_models` commands for Telegram-style provider/model browsing with callback-based selection.

## Apple Watch and APNs delivery notes (v2026.2.19)

- Apple Watch companion flows depend on reliable gateway-to-iOS notification relay.
- APNs registration/signing configuration is now an explicit operational dependency for iOS/watch delivery reliability.
- If watch/iOS commands appear delayed or missing, validate APNs push path before changing model/tool policy.

## Telegram media reliability (v2026.3.13)

- Telegram inbound media downloads retry with an IPv4 fallback when the primary fetch path fails.
- If media ingestion still fails, keep checking SSRF/media policy and network reachability rather than assuming the connector lacks retry behavior.

## Mistral provider (v2026.2.22)

OpenClaw supports Mistral for:

- Text/image model routing (`mistral/...`)
- Audio transcription via Voxtral (media understanding)
- Memory embeddings (`memorySearch.provider = "mistral"`)

Onboarding examples:

```bash
openclaw onboard --auth-choice mistral-api-key

# non-interactive
openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
```

Minimal config shape (example):

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "mistral/mistral-large-latest"
      }
    }
  }
}
```

Audio transcription model wiring example:

```json
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "models": [{ "provider": "mistral", "model": "voxtral-mini-latest" }]
      }
    }
  }
}
```

Operational notes:

- Auth uses `MISTRAL_API_KEY`.
- Default base URL: `https://api.mistral.ai/v1`.
- Embeddings endpoint: `/v1/embeddings` (commonly `mistral-embed`).
- Audio transcriptions endpoint: `/v1/audio/transcriptions`.

## Synology Chat channel (plugin) (v2026.2.22)

Synology Chat is plugin-based (not included in default core channel install).

Install the plugin from a local checkout:

```bash
openclaw plugins install ./extensions/synology-chat
```

High-level setup:

1. Create an incoming webhook in Synology Chat and copy its URL.
2. Create an outgoing webhook with a secret token.
3. Point the outgoing webhook to your gateway (default: `/webhook/synology`).
4. Configure `channels.synology-chat` and restart the gateway.

Minimal config example:

```json
{
  "channels": {
    "synology-chat": {
      "enabled": true,
      "token": "synology-outgoing-token",
      "incomingUrl": "https://nas.example.com/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=...",
      "webhookPath": "/webhook/synology",
      "dmPolicy": "allowlist",
      "allowedUserIds": ["123456"],
      "rateLimitPerMinute": 30,
      "allowInsecureSsl": false
    }
  }
}
```

Safety defaults:

- Prefer `dmPolicy: "allowlist"` in production.
- Keep `allowInsecureSsl: false` unless you explicitly trust your NAS TLS setup.

## Provider notes (v2026.2.23)

- `kilocode` provider is supported with first-class auth/onboarding and implicit provider detection.
- Moonshot/Kimi surfaces: `web_search` supports provider `"kimi"`, and media understanding adds a native Moonshot video provider.
