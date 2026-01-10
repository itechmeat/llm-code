# Performance & Rate Limits

## Telegram rate limits

Telegram imposes rate limits on bot API calls:

- ~30 messages per second to different chats
- ~1 message per second to the same chat
- Editing messages: similar limits apply

## Message throttling

When streaming or editing messages, throttle edits to avoid rate limits:

- Batch edits (e.g., update every 1-2 seconds, not on every token)
- Use exponential backoff on 429 errors

## Webhook handler performance

- Keep webhook handling fast (< 1 second)
- Avoid heavy AI/RAG work directly in the webhook request path
- Offload to background tasks/queues

## Background processing

Use task queues for:

- AI model inference
- RAG retrieval and generation
- External API calls
- Database-heavy operations

## Logging and monitoring

Log failures with enough context:

- `bot_id`
- `chat_id`
- `user_telegram_id`
- `update_id`
- Error details

## Health checks

If Telegram-related health checks are implemented:

- Treat as external dependency checks
- Keep lightweight
- Check webhook connectivity separately from bot API
