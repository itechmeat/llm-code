# Telegram Bot API Reference

## Overview

The Bot API is an HTTP-based interface for building Telegram bots. It provides:

- HTTPS requests to `https://api.telegram.org/bot<token>/METHOD_NAME`
- JSON responses
- Webhook or long polling for updates

**Bot API 9.4** is supported in aiogram v3.25.0.

## Authentication

All requests require bot token:

```
https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/getMe
```

**Critical**: Never expose token in client code or logs.

## Getting Updates

### Polling (getUpdates)

```python
# Not recommended for production
response = await client.get(
    f"https://api.telegram.org/bot{token}/getUpdates",
    params={"offset": last_update_id + 1, "timeout": 30}
)
```

### Webhooks (recommended)

```python
# Set webhook
await client.post(
    f"https://api.telegram.org/bot{token}/setWebhook",
    json={
        "url": "https://example.com/webhook/secret123",
        "secret_token": "my-secret-token",  # For verification
        "allowed_updates": ["message", "callback_query"],
    }
)
```

## Core Methods

### Messages

| Method                   | Description               |
| ------------------------ | ------------------------- |
| `sendMessage`            | Send text message         |
| `sendPhoto`              | Send photo                |
| `sendDocument`           | Send file                 |
| `sendLocation`           | Send location             |
| `sendVenue`              | Send venue                |
| `sendContact`            | Send contact              |
| `sendPoll`               | Send poll                 |
| `sendDice`               | Send dice/emoji animation |
| `editMessageText`        | Edit message text         |
| `editMessageReplyMarkup` | Edit inline keyboard      |
| `deleteMessage`          | Delete message            |
| `forwardMessage`         | Forward message           |
| `copyMessage`            | Copy message              |

### Chats

| Method                  | Description          |
| ----------------------- | -------------------- |
| `getChat`               | Get chat info        |
| `getChatMember`         | Get member info      |
| `getChatMemberCount`    | Get member count     |
| `getChatAdministrators` | List admins          |
| `banChatMember`         | Ban user             |
| `unbanChatMember`       | Unban user           |
| `restrictChatMember`    | Restrict permissions |
| `promoteChatMember`     | Promote to admin     |
| `setChatTitle`          | Set chat title       |
| `setChatDescription`    | Set description      |
| `pinChatMessage`        | Pin message          |
| `leaveChat`             | Leave chat           |

### Bot Info

| Method                  | Description           |
| ----------------------- | --------------------- |
| `getMe`                 | Get bot info          |
| `setMyCommands`         | Set bot commands      |
| `getMyCommands`         | Get bot commands      |
| `setMyDescription`      | Set bot description   |
| `setMyShortDescription` | Set short description |

### Inline Mode

| Method              | Description          |
| ------------------- | -------------------- |
| `answerInlineQuery` | Answer inline query  |
| `answerWebAppQuery` | Answer web app query |

### Callbacks

| Method                | Description            |
| --------------------- | ---------------------- |
| `answerCallbackQuery` | Answer button callback |

### Payments

| Method                   | Description          |
| ------------------------ | -------------------- |
| `sendInvoice`            | Send payment invoice |
| `answerPreCheckoutQuery` | Confirm checkout     |
| `answerShippingQuery`    | Answer shipping      |
| `createInvoiceLink`      | Create invoice link  |
| `refundStarPayment`      | Refund Stars         |

## Update Types

```python
class Update:
    update_id: int
    message: Message | None
    edited_message: Message | None
    channel_post: Message | None
    edited_channel_post: Message | None
    callback_query: CallbackQuery | None
    inline_query: InlineQuery | None
    chosen_inline_result: ChosenInlineResult | None
    shipping_query: ShippingQuery | None
    pre_checkout_query: PreCheckoutQuery | None
    poll: Poll | None
    poll_answer: PollAnswer | None
    my_chat_member: ChatMemberUpdated | None
    chat_member: ChatMemberUpdated | None
    chat_join_request: ChatJoinRequest | None
```

## Common Types

### Message

```python
class Message:
    message_id: int
    date: int
    chat: Chat
    from_user: User | None
    text: str | None
    entities: list[MessageEntity] | None
    reply_to_message: Message | None
    # ... many more fields
```

### Chat

```python
class Chat:
    id: int
    type: str  # "private", "group", "supergroup", "channel"
    title: str | None
    username: str | None
```

### User

```python
class User:
    id: int
    is_bot: bool
    first_name: str
    last_name: str | None
    username: str | None
    language_code: str | None
```

### Contact

```python
class Contact:
    phone_number: str
    first_name: str
    last_name: str | None
    user_id: int | None
    vcard: str | None
    full_name: str | None  # Bot API 9.4
```

### CallbackQuery

```python
class CallbackQuery:
    id: str
    from_user: User
    message: Message | None
    inline_message_id: str | None
    chat_instance: str
    data: str | None  # max 64 bytes
```

## Error Handling

Bot API returns:

```json
{
  "ok": false,
  "error_code": 400,
  "description": "Bad Request: message text is empty"
}
```

Common error codes:

- `400` — Bad request (invalid parameters)
- `401` — Unauthorized (invalid token)
- `403` — Forbidden (bot blocked by user)
- `404` — Not found
- `429` — Too many requests (rate limited)

## Rate Limits

- ~30 messages/second to different chats
- ~1 message/second to same chat
- ~20 messages/minute to same group
- Bulk limits for notifications

On 429 error, check `retry_after` in response.

## Formatting

### MarkdownV2

````
*bold*
_italic_
__underline__
~strikethrough~
||spoiler||
`inline code`
```pre```
[link](https://example.com)
````

Escape special characters: `_*[]()~`>#+-=|{}.!\`

### HTML

```html
<b>bold</b>
<i>italic</i>
<u>underline</u>
<s>strikethrough</s>
<tg-spoiler>spoiler</tg-spoiler>
<code>inline code</code>
<pre>code block</pre>
<a href="https://example.com">link</a>
```

## Links

- Full API docs: https://core.telegram.org/bots/api
- Changelog: https://core.telegram.org/bots/api-changelog
- @BotNews — API updates channel
