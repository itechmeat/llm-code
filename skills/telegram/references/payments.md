# Telegram Payments

> Reference: https://core.telegram.org/bots/payments

## Overview

Telegram Payments API — open platform for accepting payments via bots. Supports **physical goods** (via payment providers) and **digital goods** (via Telegram Stars).

## Two Payment Modes

| Mode | Currency | Use Case | Provider |
|------|----------|----------|----------|
| **Physical goods** | 30+ fiat currencies | Products requiring shipping | Stripe, YooKassa, etc. |
| **Digital goods** | Telegram Stars (XTR) | Subscriptions, in-app purchases, digital content | Telegram (no external provider) |

## Physical Goods: Payment Flow

### 1. Setup Provider Token

1. BotFather → `/mybots` → Select bot
2. Bot Settings → Payments
3. Choose provider (Stripe, etc.)
4. Get token (format: `123:LIVE:XXXX`)

### 2. Send Invoice

```python
from aiogram import Bot
from aiogram.types import LabeledPrice

async def send_invoice(bot: Bot, chat_id: int, provider_token: str):
    await bot.send_invoice(
        chat_id=chat_id,
        title="Product Name",
        description="Product description",
        payload="unique_payload_id",
        provider_token=provider_token,
        currency="USD",
        prices=[
            LabeledPrice(label="Product", amount=1000),  # $10.00 (in cents)
            LabeledPrice(label="Shipping", amount=500),   # $5.00
        ],
        # Optional
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=True,
        is_flexible=True,  # Enable shipping options callback
        start_parameter="product_123",  # For deep links
        max_tip_amount=1000,  # Max tip $10
        suggested_tip_amounts=[100, 200, 500],  # Suggested tips
    )
```

### 3. Handle Shipping Query (if `is_flexible=True`)

```python
from aiogram import Router, F
from aiogram.types import ShippingQuery, ShippingOption

router = Router()

@router.shipping_query()
async def on_shipping_query(query: ShippingQuery):
    # Check if delivery is available
    if query.shipping_address.country_code not in ["US", "CA"]:
        await query.answer(ok=False, error_message="Delivery not available")
        return
    
    # Offer shipping options
    await query.answer(
        ok=True,
        shipping_options=[
            ShippingOption(
                id="standard",
                title="Standard Delivery",
                prices=[LabeledPrice(label="Standard", amount=500)]
            ),
            ShippingOption(
                id="express",
                title="Express Delivery",
                prices=[LabeledPrice(label="Express", amount=1500)]
            ),
        ]
    )
```

### 4. Handle Pre-Checkout Query

```python
from aiogram.types import PreCheckoutQuery

@router.pre_checkout_query()
async def on_pre_checkout(query: PreCheckoutQuery):
    """MUST answer within 10 seconds."""
    # Verify order can be fulfilled
    if not await check_inventory(query.invoice_payload):
        await query.answer(
            ok=False,
            error_message="Sorry, this item is no longer available"
        )
        return
    
    await query.answer(ok=True)
```

### 5. Handle Successful Payment

```python
from aiogram.types import Message
from aiogram import F

@router.message(F.successful_payment)
async def on_successful_payment(message: Message):
    payment = message.successful_payment
    
    # Process order
    await process_order(
        user_id=message.from_user.id,
        payload=payment.invoice_payload,
        total_amount=payment.total_amount,
        currency=payment.currency,
        telegram_payment_charge_id=payment.telegram_payment_charge_id,
        provider_payment_charge_id=payment.provider_payment_charge_id,
        # Shipping info if requested
        shipping_address=payment.order_info.shipping_address if payment.order_info else None,
    )
    
    await message.answer("✅ Thank you! Your order has been placed.")
```

## Digital Goods: Telegram Stars

### Send Invoice for Stars

```python
async def send_stars_invoice(bot: Bot, chat_id: int):
    await bot.send_invoice(
        chat_id=chat_id,
        title="Premium Subscription",
        description="1 month of premium features",
        payload="premium_1month",
        provider_token="",  # Empty for Stars
        currency="XTR",     # Telegram Stars
        prices=[
            LabeledPrice(label="Premium", amount=100),  # 100 Stars
        ],
    )
```

### Handle Stars Payment

```python
@router.message(F.successful_payment)
async def on_stars_payment(message: Message):
    payment = message.successful_payment
    
    if payment.currency == "XTR":
        # Stars payment
        await grant_premium(
            user_id=message.from_user.id,
            stars_paid=payment.total_amount,
        )
```

### Refund Stars

```python
async def refund_stars(bot: Bot, user_id: int, charge_id: str):
    """Refund Telegram Stars payment."""
    await bot.refund_star_payment(
        user_id=user_id,
        telegram_payment_charge_id=charge_id,
    )
```

## Inline Invoices

```python
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputInvoiceMessageContent

@router.inline_query()
async def on_inline_query(query: InlineQuery):
    results = [
        InlineQueryResultArticle(
            id="product_123",
            title="Buy Premium",
            description="100 Stars",
            input_message_content=InputInvoiceMessageContent(
                title="Premium Subscription",
                description="1 month premium",
                payload="inline_premium_123",
                provider_token="",
                currency="XTR",
                prices=[LabeledPrice(label="Premium", amount=100)],
            ),
        )
    ]
    await query.answer(results)
```

## Paid Media (Channels/Bots)

```python
from aiogram.types import InputMediaPhoto

async def send_paid_media(bot: Bot, chat_id: int):
    """Send paid photos/videos (Stars required to view)."""
    await bot.send_paid_media(
        chat_id=chat_id,
        star_count=10,  # Price in Stars
        media=[
            InputMediaPhoto(media="file_id_or_url"),
        ],
        caption="Exclusive content! Pay 10 Stars to unlock.",
    )
```

## Star Subscriptions

```python
from aiogram.types import ChatInviteLink

async def create_paid_subscription(bot: Bot, chat_id: int):
    """Create invite link with monthly Star subscription."""
    link = await bot.create_chat_subscription_invite_link(
        chat_id=chat_id,
        subscription_period=2592000,  # 30 days in seconds
        subscription_price=50,         # 50 Stars/month
        name="VIP Access",
    )
    return link.invite_link
```

## Star Reactions (Channels)

Channel owners can enable paid Star reactions:
- Channel Settings → Reactions → Enable Paid Reactions
- Owner receives 100% of Stars
- Stars can be converted to Toncoin or ad credits

## Affiliate Programs

Developers can create affiliate programs for mini apps:

```python
# Users get referral links
# When referred users make Star purchases, referrer earns commission
# Commission % and duration set by developer
```

## Testing Payments

### Stripe Test Mode

1. BotFather → Payments → Select "Stripe TEST MODE"
2. Use test card: `4242 4242 4242 4242`
3. Any future expiry, any CVC

### Test Token Format

- Test: `123:TEST:XXXX`
- Live: `123:LIVE:XXXX`

## Currency Amounts

Amounts in **smallest currency units** (cents, kopecks, etc.):

| Currency | Amount | Meaning |
|----------|--------|---------|
| USD | 1000 | $10.00 |
| EUR | 1500 | €15.00 |
| RUB | 100000 | 1000.00 ₽ |
| XTR | 100 | 100 Stars |

### Limits

- Min: ~$1 equivalent
- Max: ~$10,000 equivalent
- Stars: No external limits

## Supported Currencies (30+)

USD, EUR, GBP, RUB, UAH, BYN, KZT, AED, AUD, CAD, CHF, CNY, CZK, DKK, HKD, HUF, IDR, ILS, INR, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PLN, RON, SEK, SGD, THB, TRY, TWD, ZAR, BRL, ARS, CLP, COP, PEN, VND...

**XTR** — Telegram Stars (digital goods only)

## Webhook vs Polling

Payments work with both modes, but **webhooks recommended** for:
- Lower latency
- Production reliability
- Required for some payment flows

## Error Handling

```python
from aiogram.exceptions import TelegramBadRequest

@router.pre_checkout_query()
async def on_pre_checkout(query: PreCheckoutQuery):
    try:
        await query.answer(ok=True)
    except TelegramBadRequest as e:
        logger.error(f"Pre-checkout failed: {e}")
        # Payment flow cancelled
```

## Live Checklist

Before going live:
- [ ] Enable 2FA on bot owner account
- [ ] Implement `/terms` command with Terms & Conditions
- [ ] Implement `/support` command or contact method
- [ ] Handle disputes and chargebacks
- [ ] Backup payment records
- [ ] Complete provider's live checklist (e.g., Stripe)
- [ ] Replace TEST token with LIVE token

## Monetization Summary

| Feature | Stars Required | Who Receives |
|---------|---------------|--------------|
| Digital product purchase | Yes | Bot developer |
| Paid media (photos/videos) | Yes | Channel/bot owner |
| Star reactions | Yes | Channel owner (100%) |
| Star subscriptions | Yes | Channel owner |
| Affiliate commissions | User's Stars | Referrer |

## Withdrawing Stars

Developers can withdraw earned Stars as:
1. **Toncoin** via Fragment (minimal commission)
2. **Telegram Ads credits** (30% bonus subsidy)

## Prohibitions

- ❌ Do NOT store provider_token in code — use env variables only
- ❌ Do NOT accept payments without inventory check in pre_checkout
- ❌ Do NOT ignore shipping_query (10 sec timeout)
- ❌ Do NOT use LIVE token without completing live checklist
- ❌ Do NOT sell prohibited items (see Stripe Prohibited Businesses)

## See Also

- [bot-api.md](bot-api.md) — Payment methods reference
- [mini-apps.md](mini-apps.md) — answerWebAppQuery for Mini App payments
- [inline-mode.md](inline-mode.md) — Inline invoices
