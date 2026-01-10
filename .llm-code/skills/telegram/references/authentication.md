# Telegram Authentication

This reference covers all Telegram authentication methods for web applications.

## Methods Overview

| Method | Context | Use Case |
|--------|---------|----------|
| **Login Widget** | Browser | Web admin panel, account linking |
| **URL Authorization** | Telegram app | Inline button → external site login |
| **Mini App initData** | Mini App | In-app authentication |

## Login Widget

Embed on your website to let users log in via Telegram.

### Setup

1. Create bot via @BotFather
2. Link domain: `/setdomain` → your domain
3. Add widget script:

```html
<script async src="https://telegram.org/js/telegram-widget.js?22"
        data-telegram-login="YourBotName"
        data-size="large"
        data-onauth="onTelegramAuth(user)"
        data-request-access="write">
</script>
```

### Data Structure

```python
class TelegramAuthData:
    id: int              # Telegram user ID
    first_name: str      # Required
    last_name: str | None
    username: str | None
    photo_url: str | None
    auth_date: int       # Unix timestamp
    hash: str            # HMAC-SHA-256 signature
```

## URL Authorization (Inline Buttons)

For login via inline keyboard buttons inside Telegram.

```python
from aiogram.types import InlineKeyboardButton, LoginUrl

button = InlineKeyboardButton(
    text="Log in",
    login_url=LoginUrl(
        url="https://example.com/auth/telegram",
        request_write_access=True,
    )
)
```

User sees confirmation prompt, then redirected with auth data in query string.

## Hash Verification (Critical)

**Always verify hash server-side before trusting data.**

### Algorithm

1. Build `data_check_string`: sorted `key=value` pairs, joined by `\n`
2. Compute `secret_key = SHA256(bot_token)`
3. Compute `HMAC_SHA256(data_check_string, secret_key)`
4. Compare with received `hash`

### Python Implementation

```python
import hashlib
import hmac
from typing import Any

def verify_telegram_auth(data: dict[str, Any], bot_token: str) -> bool:
    """Verify Telegram authentication data (Login Widget / URL Auth)."""
    received_hash = data.pop("hash", None)
    if not received_hash:
        return False
    
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items()) if v is not None
    )
    
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    computed_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_hash, received_hash)
```

### Auth Date Validation

Reject stale authentications (recommended max: 5 minutes):

```python
from datetime import datetime, timedelta, UTC

MAX_AUTH_AGE = timedelta(minutes=5)

def is_auth_fresh(auth_date: int) -> bool:
    auth_time = datetime.fromtimestamp(auth_date, tz=UTC)
    return datetime.now(UTC) - auth_time < MAX_AUTH_AGE
```

## Mini App Authentication

Different algorithm — uses `"WebAppData"` as HMAC key prefix.

```python
def validate_mini_app_init_data(init_data: str, bot_token: str) -> bool:
    """Validate Mini App initData."""
    from urllib.parse import parse_qsl
    
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop('hash', None)
    if not received_hash:
        return False
    
    data_check_string = '\n'.join(
        f'{k}={v}' for k, v in sorted(parsed.items())
    )
    
    # Different from Login Widget: HMAC with "WebAppData" prefix
    secret_key = hmac.new(
        b'WebAppData',
        bot_token.encode(),
        hashlib.sha256
    ).digest()
    
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_hash, received_hash)
```

## FastAPI Endpoint Example

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str

@router.post("/auth/telegram")
async def telegram_login(data: TelegramAuthData):
    if not verify_telegram_auth(data.model_dump(), settings.BOT_TOKEN):
        raise HTTPException(401, "Invalid auth")
    
    if not is_auth_fresh(data.auth_date):
        raise HTTPException(401, "Auth expired")
    
    account = await account_service.find_or_create_by_telegram(
        telegram_id=data.id,
        first_name=data.first_name,
    )
    
    return {"token": await create_session(account.id)}
```

## Security Checklist

- ✅ Always verify hash server-side
- ✅ Check `auth_date` freshness (5 minutes max)
- ✅ Use HTTPS for callback URLs
- ✅ Store `bot_token` in environment variables
- ✅ Use `hmac.compare_digest()` for constant-time comparison
- ✅ Link domains in @BotFather before use

## See Also

- [mini-apps.md](mini-apps.md) — Full Mini App documentation
- [keyboard-design.md](keyboard-design.md) — Inline keyboard patterns
