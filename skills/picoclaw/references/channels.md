# Channels

Channels are configured under `channels` in `~/.picoclaw/config.json` and are started by `picoclaw gateway`.

General pattern:

1. Set `channels.<name>.enabled=true`
2. Fill required credentials/IDs
3. Optionally restrict who can trigger the bot via `allow_from`
4. Run `picoclaw gateway`

## Common fields

- `enabled`: turns the channel on/off.
- `allow_from`: allowlist of peer IDs. Accepts strings or numbers.

Recent channel updates add voice-audio transcription echo behavior, so supported channels can reply with the recognized transcription of a voice message instead of treating voice as opaque input.

## WhatsApp

Config keys (from upstream `config.example.json`):

- `channels.whatsapp.enabled`
- `channels.whatsapp.bridge_url` (WebSocket URL for a bridge process)
- `channels.whatsapp.use_native` (use built-in native implementation)
- `channels.whatsapp.session_store_path` (where to store the native session state)
- `channels.whatsapp.allow_from`
- `channels.whatsapp.reasoning_channel_id`

Operational notes:

- If you set `use_native=true`, PicoClaw must be built with the `whatsapp_native` build tag.
  - Upstream Makefile provides a helper target: `make build-whatsapp-native`.
- If you run a standard binary (no native tag), keep `use_native=false` and point `bridge_url` to your WhatsApp bridge.

## Telegram

Config keys:

- `channels.telegram.token`
- `channels.telegram.proxy` (optional)
- `channels.telegram.allow_from`

Setup notes:

- Create a bot via `@BotFather` → `/newbot` → copy the HTTP API token.
- If you need an allowlist, you can obtain your Telegram numeric user ID (e.g. via a user-info bot) and put it into `allow_from`.

## Discord

Config keys:

- `channels.discord.token`
- `channels.discord.mention_only` (only respond when mentioned)
- `channels.discord.allow_from`

Setup notes:

- Create an app in the Discord Developer Portal.
- Enable intents (at least Message Content Intent; some setups also require Server Members Intent).
- Invite the bot to your server with send/read permissions.

Discord channel behavior was updated to reply more cleanly when voice transcription echo is enabled.

## Slack

Config keys:

- `channels.slack.bot_token`
- `channels.slack.app_token`

Setup notes:

- PicoClaw uses Slack Socket Mode (no public webhook endpoint required).
- Create a Slack app → enable Socket Mode → generate an app-level token (`xapp-...`).
- Install the app to your workspace and provide a bot token (`xoxb-...`).

Recent builds also improved Slack reply behavior when audio transcription echo is involved.

## Teams Webhook (output-only, v0.2.6)

Config surface comes from the upstream `teams_webhook` channel type:

- `channels.<name>.type = "teams_webhook"`
- `channels.<name>.settings.webhooks.default.webhook_url`
- optional additional named webhook targets under `webhooks.<target>`
- optional target title per webhook

Operational notes:

- This is an output-only channel. It does not receive inbound chat events.
- Webhook URLs must use HTTPS, and a `default` target is required.
- Outbound `ChatID` selects the webhook target; unknown or empty targets fall back to `default`.
- PicoClaw renders rich notifications as Adaptive Cards and converts markdown tables into native Teams table elements when possible.

## Feishu reply context (v0.2.6)

- Recent builds improved reply context for Feishu card and file replies.
- If follow-up replies used to lose thread context, re-test after upgrading before adding custom channel-side workarounds.

## OneBot

Config keys:

- `channels.onebot.ws_url`
- `channels.onebot.access_token`
- `channels.onebot.group_trigger_prefix`

## WeCom (two modes)

### WeCom Bot (`channels.wecom`)

Intended for easier setup and group chats.
Typical keys:

- `token`, `encoding_aes_key`
- `webhook_url`
- `webhook_host`, `webhook_port`, `webhook_path`

Setup notes:

- Add a group robot and copy its send webhook URL.
- If you want inbound messages, configure the callback URL + token + AES key in WeCom.

### WeCom App (`channels.wecom_app`)

More features (incl. proactive messaging), but private chat only.
Typical keys:

- `corp_id`, `corp_secret`, `agent_id`
- `token`, `encoding_aes_key`
- `webhook_host`, `webhook_port` (default 18792), `webhook_path` (default `/webhook/wecom-app`)

Setup notes:

- Create an internal app in the WeCom admin console and note `CorpID`, `AgentId`, and `Secret`.
- Configure “receive messages” callback to `http://<host>:<port>/webhook/wecom-app`.

Operational notes (from project docs):

- Callback URL validation requires the port to be reachable.
- If you see decrypt/padding errors for Chinese text, update PicoClaw (WeCom uses a 32-byte PKCS7 block size).

## LINE

Config keys:

- `channel_secret`, `channel_access_token`
- `webhook_host`, `webhook_port` (default 18791), `webhook_path`
