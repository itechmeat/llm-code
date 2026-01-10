# Webhooks and Update Processing

## Webhook Setup

One webhook URL per bot: `/webhook/{webhook_token}`.

```python
# Set webhook with secret token
await bot.set_webhook(
    url=f"https://example.com/webhook/{webhook_token}",
    secret_token="my-secret-token",
    allowed_updates=["message", "callback_query", "inline_query"],
)
```

### Security

Validate `X-Telegram-Bot-Api-Secret-Token` header on every request:

```python
from fastapi import Header, HTTPException

async def verify_telegram_secret(
    x_telegram_bot_api_secret_token: str = Header(None)
):
    if x_telegram_bot_api_secret_token != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
```

Store tokens in environment variables. Never hardcode or log them.

## Polling vs Webhooks

| Aspect | Polling | Webhooks |
|--------|---------|----------|
| Production | ❌ Not recommended | ✅ Recommended |
| Setup | Simpler | Requires HTTPS endpoint |
| Latency | Higher (polling interval) | Instant |
| Reliability | Less reliable | More reliable |

**Critical**: Never run polling and webhooks simultaneously for the same bot.

## Update Processing

### At-Least-Once Delivery

Telegram may retry webhook delivery on timeout/error:

- Make handlers **idempotent**
- Or implement de-duplication (store last `update_id` per bot)

### Fast Acknowledgement

```python
@router.message()
async def handle_message(message: Message):
    # Return 200 OK quickly to Telegram
    # Offload heavy work to background
    background_tasks.add_task(process_ai_response, message)
    return {"ok": True}
```

Keep webhook handling under 1 second. Offload AI/RAG work to task queues.

### Update Types

| Type | Use Case |
|------|----------|
| `message` | Text, commands, media, service messages |
| `callback_query` | Inline keyboard button presses |
| `inline_query` | Inline mode queries |
| `pre_checkout_query` | Payment confirmation |
| `shipping_query` | Shipping options request |

### Error Handling

```python
@router.message()
async def handle_message(message: Message):
    try:
        await process_message(message)
    except Exception as e:
        logger.error(
            "Message processing failed",
            extra={
                "bot_id": bot_id,
                "chat_id": message.chat.id,
                "update_id": update_id,
                "error": str(e),
            }
        )
    # Return 200 OK to prevent Telegram retries
    return {"ok": True}
```

## Rate Limits

- ~30 messages/second to different chats
- ~1 message/second to same chat
- ~20 messages/minute to same group

On 429 error, respect `retry_after`. Use exponential backoff.

## Logging Context

Always include:

- `bot_id`
- `chat_id`
- `user_telegram_id`
- `update_id`
