---
name: telegram
description: "Telegram Bot development playbook: bot fundamentals, aiogram 3 patterns (handlers/middlewares/FSM), webhooks, keyboard UX, inline mode, Mini Apps, payments (Stars/subscriptions), authentication. Use when building or modifying Telegram bots, setting up webhook infrastructure, implementing inline keyboards/callback queries, integrating Telegram payments or Stars, or working with aiogram 3 handlers and FSM. Keywords: Telegram, aiogram, Bot API, webhook, handlers, middlewares, FSM, inline keyboard, reply keyboard, callback_query, inline mode, Mini Apps, Web Apps, payments, Telegram Stars, Login Widget."
metadata:
  version: "3.31.0"
  release_date: "2026-09-04"
---

# Telegram (Skill Router)

Router skill: pick the reference that matches your task.

## Quick Navigation

| Task                                    | Reference                                             |
| --------------------------------------- | ----------------------------------------------------- |
| New to Telegram bots                    | [bots-overview.md](references/bots-overview.md)       |
| Bot capabilities overview               | [bot-features.md](references/bot-features.md)         |
| API methods/types                       | [bot-api.md](references/bot-api.md)                   |
| Webhook setup & security                | [webhooks.md](references/webhooks.md)                 |
| aiogram 3 handlers/FSM                  | [aiogram-patterns.md](references/aiogram-patterns.md) |
| Keyboard UX                             | [keyboard-design.md](references/keyboard-design.md)   |
| Inline mode                             | [inline-mode.md](references/inline-mode.md)           |
| Mini Apps (Web Apps)                    | [mini-apps.md](references/mini-apps.md)               |
| Payments (Stars)                        | [payments.md](references/payments.md)                 |
| Authentication (Login Widget, URL Auth) | [authentication.md](references/authentication.md)     |
| Rate limits & performance               | [performance.md](references/performance.md)           |

## Critical Prohibitions

- ❌ No polling + webhooks simultaneously for same bot
- ❌ No hardcoded tokens/secrets — use environment variables
- ❌ No secrets in callback_data or logs
- ❌ No ignoring `answer_callback_query` — always respond
- ❌ No blocking work in webhook handlers — use background tasks
- ❌ No trusting Login Widget data without hash verification

## Definition of Done

- [ ] Webhook handlers validate `X-Telegram-Bot-Api-Secret-Token`
- [ ] Keyboards: max 2 buttons per row, mobile-first
- [ ] Callback data validated, not trusted blindly
- [ ] Handlers are idempotent or have de-duplication

## Release Note (3.29.x - 3.31.x / Bot API 10.1 - 10.3)

- aiogram `3.31.0` adds full **Bot API 10.3** support, bringing rich messages (rich block buttons, expandable block quotations, document blocks), ephemeral messages (`EphemeralMessageParameters`, message drafts with `can_stop`/`keep_on_stop`), and new reply-markup controls (`DisabledButton`, `force_reply`). `3.30.0` added **Bot API 10.2** and `3.29.0` added **Bot API 10.1**. Assume the newer method/type schema when targeting recent aiogram.
- `3.31.0` also fixes webhook-path dispatcher context loss, Bot API-level `parse_mode` not applying to newer photo/video entities, live-photo content-type detection, and territory-specific i18n locale resolution; vulnerable dependencies were bumped to patched versions.
- `3.29.1` fixes a severe (exponential) slowdown when validating nested unions, so heavy handler/filter models parse far faster on the patched line.

## Release Note (3.28.x / Bot API 10.0)

- aiogram `3.28.x` adds Bot API `10.0` support, bringing guest-mode updates, richer poll/media flows, live photos, reaction-management methods, and managed/business-bot access settings.
- The `3.28.1+` patch line also fixes `InputPollOption.media` validation, so poll/media integrations should assume the newer schema and the patched aiogram serializer behavior.

## Links

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [aiogram Releases](https://github.com/aiogram/aiogram/releases)
- [aiogram Documentation](https://docs.aiogram.dev/)

## Related Skills

- [PostgreSQL](../postgresql/SKILL.md) — for database layer
- [FastAPI](../fastapi-api-layer/SKILL.md) — for API layer (if exists)
