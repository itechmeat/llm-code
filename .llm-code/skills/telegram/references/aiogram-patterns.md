# aiogram 3 Patterns

Async framework for Telegram bots. Python 3.9+.

## Router & Handler Organization

```python
from aiogram import Router, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

router = Router(name="main")

@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Hello!")

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer("Help text...")
```

### Nested Routers

```python
# main.py
dp = Dispatcher()
dp.include_router(main_router)
dp.include_router(admin_router)

# admin_router.py
admin_router = Router(name="admin")
admin_router.message.filter(IsAdmin())  # Filter for all handlers in router
```

### Handler Order

Handlers are checked in registration order. First match wins.

```python
@router.message(F.text == "specific")  # First: exact match
async def handle_specific(message: Message): ...

@router.message(F.text)  # Last: catch-all
async def handle_text(message: Message): ...
```

## Callback Query Handlers

```python
from aiogram.types import CallbackQuery

@router.callback_query(F.data == "confirm")
async def on_confirm(callback: CallbackQuery) -> None:
    await callback.answer("Confirmed!")  # Always answer to remove loading
    await callback.message.edit_text("Done")

@router.callback_query(F.data.startswith("item:"))
async def on_item(callback: CallbackQuery) -> None:
    item_id = callback.data.split(":")[1]
    await callback.answer()
    # Process item...
```

**Critical**: Always call `callback.answer()` to dismiss the loading indicator.

## Middlewares

```python
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable

class DatabaseMiddleware(BaseMiddleware):
    """Provides database session to handlers."""

    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_maker() as session:
            data["db_session"] = session
            return await handler(event, data)

# Register
router.message.middleware(DatabaseMiddleware(session_maker))
```

## FSM (Finite State Machine)

```python
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class OrderForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    confirm = State()

@router.message(Command("order"))
async def start_order(message: Message, state: FSMContext) -> None:
    await state.set_state(OrderForm.waiting_for_name)
    await message.answer("Enter your name:")

@router.message(OrderForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(OrderForm.waiting_for_phone)
    await message.answer("Enter phone:")

@router.message(OrderForm.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await message.answer(f"Order from {data['name']}, phone: {message.text}")
```

### FSM Storage

```python
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage

# Production: Redis
storage = RedisStorage.from_url("redis://localhost:6379/0")

# Development: Memory (lost on restart)
storage = MemoryStorage()

dp = Dispatcher(storage=storage)
```

## Filters

```python
from aiogram.filters import Filter
from aiogram.types import Message

class IsAdmin(Filter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

# Usage
@router.message(Command("ban"), IsAdmin([123456789]))
async def ban_user(message: Message): ...
```

### Magic Filters

```python
from aiogram import F

@router.message(F.text.lower().contains("hello"))
async def greet(message: Message): ...

@router.message(F.photo)
async def handle_photo(message: Message): ...

@router.callback_query(F.data.in_({"yes", "no"}))
async def handle_choice(callback: CallbackQuery): ...
```

## Error Handling

```python
from aiogram.types import ErrorEvent

@router.error()
async def error_handler(event: ErrorEvent) -> None:
    logger.error(
        "Exception in handler",
        exc_info=event.exception,
        extra={
            "update_id": event.update.update_id if event.update else None,
        }
    )
    # Optionally notify user
```

## Dependency Injection

```python
from aiogram import Bot

@router.message(Command("info"))
async def cmd_info(
    message: Message,
    bot: Bot,  # Injected automatically
    db_session: AsyncSession,  # From middleware
) -> None:
    me = await bot.get_me()
    await message.answer(f"I am {me.username}")
```

## Logging Context

Always include in logs:

- `chat_id` — conversation context
- `user_id` — Telegram user
- `update_id` — for tracing

```python
import structlog

logger = structlog.get_logger()

@router.message()
async def handle(message: Message) -> None:
    logger.info(
        "message_received",
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )
```

## Critical Rules

- ❌ No sync I/O in handlers — use `aiofiles`, `httpx`, async DB
- ❌ No bare `except:` — catch specific exceptions
- ✅ Always `callback.answer()` for callback queries
- ✅ Use routers for handler organization
