# Telegram Bot Features Overview

Quick reference of what bots can do. For details, see specialized references.

## Commands

- Start with `/`, up to 32 chars, lowercase recommended
- Standard: `/start`, `/help`, `/settings`
- Configure via @BotFather or `setMyCommands` API
- Scope by chat type, user role, language

See also: [bots-overview.md](bots-overview.md)

## Keyboards

| Type                | Purpose                           |
| ------------------- | --------------------------------- |
| **Reply Keyboard**  | Custom keyboard below input field |
| **Inline Keyboard** | Buttons attached to messages      |

Button types: callback, URL, switch-inline, login_url, web_app, pay.

Bots can now set button colors and emoji to emphasize primary actions.

See also: [keyboard-design.md](keyboard-design.md)

## Inline Mode

Users query bot from any chat: `@YourBot query`

Enable in @BotFather → `/setinline`

See also: [inline-mode.md](inline-mode.md)

## Payments

| Mode           | Currency              | Use Case              |
| -------------- | --------------------- | --------------------- |
| Physical goods | Fiat (USD, EUR, etc.) | Shipping required     |
| Digital goods  | Telegram Stars (XTR)  | Subscriptions, in-app |

See also: [payments.md](payments.md)

## Managed & Business Bots (Bot API 9.6-10.0)

- Telegram now supports managed-bot flows where one bot can help create and operate another bot.
- New button/request flows allow asking the user for a managed bot directly from keyboards and Mini Apps.
- Managed bot creation and token-change events are now first-class update/message payloads, so webhook routing and allowlist logic should treat them as operationally sensitive events.
- Bot API 10.0 adds managed-bot access settings methods and lets business bots manage user accounts without requiring Telegram Premium.
- If bot-to-bot communication is enabled, treat conversations with other bots as explicit allowlisted flows rather than assuming all peer bots are unreachable.

## Guest Mode (Bot API 10.0)

- Bots can now receive certain guest-mode messages and reply in chats where they are not members.
- New guest-mode payloads (`guest_message`, `guest_query_id`, caller user/chat metadata) should be routed separately from normal membership-based chat flows.
- Do not assume chat membership when authorizing guest-mode replies, logging sender context, or deciding whether a bot may answer.

## Polls (Bot API 9.6-10.0)

- Quizzes can now have multiple correct answers.
- Polls can allow revoting, shuffle options, hide results until close, and carry a description.
- Option metadata now has persistent identifiers and audit-style fields for who added an option and when.
- Bot API 10.0 adds media in poll questions/options/explanations, `members_only`, `country_codes`, and allows single-option poll flows.
- If your bot stores poll state externally, prefer persistent option IDs over positional assumptions, and validate media-bearing options with the patched aiogram `3.28.1+` serializers.

## Media Updates (Bot API 10.0)

- Live photos are now first-class media with dedicated send/edit/media-group support.
- Polls can carry media in the question, answer options, and quiz explanations.
- If your bot mirrors Telegram media types in a strict schema, add live-photo and poll-media variants before enforcing validation.

## Chat Management (Bot API 10.0)

- Bots can now delete reactions from messages and work with `can_react_to_messages` permissions.
- `getChatAdministrators` can optionally return bots, which matters if your admin sync logic previously filtered them out by assumption.

## Mini Apps

JavaScript web apps inside Telegram with native features:

- Theme integration
- Haptic feedback
- Cloud storage
- QR scanner
- Fullscreen mode
- `requestChat` from `WebApp`
- Prepared keyboard buttons for requesting users, chats, and managed bots

See also: [mini-apps.md](mini-apps.md)

## HTML5 Games

1. Create via @BotFather `/newgame`
2. Send via `sendGame`
3. Track scores with `setGameScore`

## Rate Limits

| Tier      | Rate         | Cost         |
| --------- | ------------ | ------------ |
| Standard  | 30 msg/sec   | Free         |
| Increased | 1000 msg/sec | 0.1 Star/msg |

## Monetization Options

- Digital product sales (Telegram Stars)
- Paid media (photos/videos)
- Star subscriptions
- Star reactions (channels)
- Affiliate programs
- Telegram Ads revenue share (50%)

## Platform Updates (2025-2026)

These are client/platform features (not direct Bot API controls), but they affect user expectations:

- AI summaries for channel posts and Instant View pages.
- Collectible gifts: crafting system and gift marketplace.
- Gift purchase offers using Stars or TON.
- Passkeys for secure Telegram logins.

## Links

- Commands: https://core.telegram.org/bots/features#commands
- Keyboards: https://core.telegram.org/bots/features#keyboards
- Inline Mode: https://core.telegram.org/bots/inline
- Payments: https://core.telegram.org/bots/payments
- Mini Apps: https://core.telegram.org/bots/webapps
