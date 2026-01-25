# Telegram Bot Features Overview

Quick reference of what bots can do. For details, see specialized references.

## Commands

- Start with `/`, up to 32 chars, lowercase recommended
- Standard: `/start`, `/help`, `/settings`
- Configure via @BotFather or `setMyCommands` API
- Scope by chat type, user role, language

See also: [bots-overview.md](bots-overview.md)

## Keyboards

| Type | Purpose |
|------|---------|
| **Reply Keyboard** | Custom keyboard below input field |
| **Inline Keyboard** | Buttons attached to messages |

Button types: callback, URL, switch-inline, login_url, web_app, pay.

See also: [keyboard-design.md](keyboard-design.md)

## Inline Mode

Users query bot from any chat: `@YourBot query`

Enable in @BotFather → `/setinline`

See also: [inline-mode.md](inline-mode.md)

## Payments

| Mode | Currency | Use Case |
|------|----------|----------|
| Physical goods | Fiat (USD, EUR, etc.) | Shipping required |
| Digital goods | Telegram Stars (XTR) | Subscriptions, in-app |

See also: [payments.md](payments.md)

## Mini Apps

JavaScript web apps inside Telegram with native features:
- Theme integration
- Haptic feedback
- Cloud storage
- QR scanner
- Fullscreen mode

See also: [mini-apps.md](mini-apps.md)

## HTML5 Games

1. Create via @BotFather `/newgame`
2. Send via `sendGame`
3. Track scores with `setGameScore`

## Rate Limits

| Tier | Rate | Cost |
|------|------|------|
| Standard | 30 msg/sec | Free |
| Increased | 1000 msg/sec | 0.1 Star/msg |

## Monetization Options

- Digital product sales (Telegram Stars)
- Paid media (photos/videos)
- Star subscriptions
- Star reactions (channels)
- Affiliate programs
- Telegram Ads revenue share (50%)

## Links

- Commands: https://core.telegram.org/bots/features#commands
- Keyboards: https://core.telegram.org/bots/features#keyboards
- Inline Mode: https://core.telegram.org/bots/inline
- Payments: https://core.telegram.org/bots/payments
- Mini Apps: https://core.telegram.org/bots/webapps
