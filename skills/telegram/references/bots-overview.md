# Telegram Bots Overview

## What Bots Can Do

Telegram bots are small applications that run entirely within the Telegram app. Key capabilities:

- **Replace websites**: Host Mini Apps built with JavaScript
- **AI chatbots**: Native support for threaded conversations and streaming responses
- **Business integration**: Process messages on behalf of business accounts
- **Payments**: Sell digital products via Telegram Stars, physical via third-party providers
- **Custom tools**: File conversion, chat management, utilities
- **Games**: HTML5 games with leaderboards
- **Inline mode**: Search and share content from any chat

## How Bots Differ from Users

| Aspect | User | Bot |
|--------|------|-----|
| Status | "last seen" / "online" | "bot" label |
| Cloud storage | Full history | Older messages may be removed |
| Starting conversations | Can message anyone | User must send first message or add to group |
| Group visibility | All messages | Only relevant messages (privacy mode) |
| Phone number | Required | Not needed |

## Bot Links

- Standard format: `@YourBot` (requires 'bot' suffix)
- Short link: `t.me/YourBot`
- Collectible usernames: Can omit 'bot' suffix (e.g., @stickers, @gif)

## Creating a Bot

1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Choose a name and username
4. Receive authentication token

**Critical**: Store bot token securely. Anyone with the token has full control.

## Global Commands

All bots should support these commands:

| Command | Purpose |
|---------|---------|
| `/start` | Begin interaction, can pass deep-linking parameters |
| `/help` | Return help message with bot description |
| `/settings` | Show/edit bot settings (if applicable) |

## Command Scopes

Bots can show different commands to different users:

- Based on chat type (private, group, channel)
- Based on user role (admin, member)
- Based on user's `language_code`

**Important**: Always validate commands server-side regardless of scope.

## Privacy Mode

Default behavior in groups:

**Bots receive:**
- Commands explicitly for them (`/command@this_bot`)
- General commands if bot was last to message
- Inline messages sent via the bot
- Replies to bot's messages
- All service messages

**Bots don't receive:**
- Regular messages not addressed to them

**Exceptions:**
- Admin bots receive all messages
- Privacy mode can be disabled in @BotFather

## Admin Rights

Bot admins always receive all messages in groups. Consider requesting only needed permissions:

- `can_delete_messages` — for moderation bots
- `can_restrict_members` — for anti-spam bots
- `can_pin_messages` — for announcement bots
- `can_manage_chat` — for general management

## Deep Linking

Pass parameters via `/start`:

```
https://t.me/YourBot?start=payload123
```

Bot receives: `/start payload123`

Use for:
- Referral tracking
- Feature activation
- User onboarding flows
