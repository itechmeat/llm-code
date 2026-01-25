# Inline Mode

## Overview

Inline mode allows users to call your bot from any chat by typing `@YourBot query` in the message input field. Results appear instantly without sending messages.

**Enable inline mode**: Send `/setinline` to @BotFather and provide placeholder text.

## How It Works

1. User types `@YourBot query` in any chat
2. Bot receives `InlineQuery` update
3. Bot returns results via `answerInlineQuery`
4. User selects result, it's sent to current chat
5. Bot receives `ChosenInlineResult` if feedback is enabled

## Supported Result Types (20+)

- `InlineQueryResultArticle` — generic text/media
- `InlineQueryResultPhoto` — photos
- `InlineQueryResultGif` — GIFs
- `InlineQueryResultMpeg4Gif` — animated GIFs (MPEG4)
- `InlineQueryResultVideo` — videos
- `InlineQueryResultAudio` — audio files
- `InlineQueryResultVoice` — voice messages
- `InlineQueryResultDocument` — documents
- `InlineQueryResultLocation` — locations
- `InlineQueryResultVenue` — venues
- `InlineQueryResultContact` — contacts
- `InlineQueryResultSticker` — stickers
- `InlineQueryResultCachedPhoto` — cached photos
- And more...

## Basic Implementation (aiogram 3)

```python
from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

router = Router()

@router.inline_query()
async def inline_handler(query: InlineQuery):
    results = []
    
    # Search based on query.query
    search_text = query.query or ""
    
    # Build results
    results.append(
        InlineQueryResultArticle(
            id="1",
            title="Result Title",
            description="Result description",
            input_message_content=InputTextMessageContent(
                message_text=f"You searched: {search_text}"
            ),
        )
    )
    
    await query.answer(
        results=results,
        cache_time=300,  # Cache results for 5 minutes
        is_personal=True,  # Results specific to this user
    )
```

## Switch to PM (Private Message)

For bots that need user setup (auth, linking accounts):

```python
await query.answer(
    results=[],
    switch_pm_text="Sign in to continue",
    switch_pm_parameter="inline_auth",  # Received in /start
)
```

User clicks button → opens PM with bot → `/start inline_auth` received.

After setup, return user to original chat:

```python
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="Return to chat",
        switch_inline_query=""  # Opens inline query in original chat
    )]
])
```

## Location-Based Results

Enable with `/setinlinegeo` in @BotFather.

```python
@router.inline_query()
async def inline_location_handler(query: InlineQuery):
    if query.location:
        lat = query.location.latitude
        lon = query.location.longitude
        # Use location for nearby results
```

User must grant location permission to bot.

## Feedback Collection

Enable with `/setinlinefeedback` in @BotFather.

```python
from aiogram.types import ChosenInlineResult

@router.chosen_inline_result()
async def chosen_result_handler(chosen: ChosenInlineResult):
    result_id = chosen.result_id
    user_id = chosen.from_user.id
    query = chosen.query
    # Track which results users select
```

**Warning**: High-traffic bots may receive more feedback than actual requests due to caching. Adjust probability setting in @BotFather.

## Caching

`cache_time` parameter in `answerInlineQuery`:

| Value | Effect |
|-------|--------|
| 0 | No caching (every keystroke = new request) |
| 300 | 5 minutes (recommended default) |
| Higher | Less load, but stale results |

`is_personal`:
- `True` — cache per user
- `False` — cache shared across users (for generic results)

## Best Practices

1. **Fast response**: Users expect instant results
2. **Meaningful previews**: Good titles and descriptions
3. **Limit results**: 10-50 results max, paginate if needed
4. **Cache appropriately**: Balance freshness vs. load
5. **Handle empty query**: Show popular/default results

## Viral Spreading

Messages sent via inline show bot username next to sender. Users can tap it to use inline query themselves.

## Example Bots

- @gif — GIF search
- @pic — Image search
- @wiki — Wikipedia search
- @bold — Text formatting
- @youtube — Video search (with auth)
- @foursquare — Location-based venues

## Links

- Official docs: https://core.telegram.org/bots/inline
- Bot API: https://core.telegram.org/bots/api#inline-mode
