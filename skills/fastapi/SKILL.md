---
name: fastapi
description: "FastAPI Python framework. Covers REST APIs, validation, dependencies, security. Use when building Python web APIs with FastAPI, configuring Pydantic models, implementing dependency injection, or setting up OAuth2/JWT authentication. Keywords: FastAPI, Pydantic, async, OAuth2, JWT, REST API."
metadata:
  version: "0.141.1"
  release_date: "2026-07-29"
---

# FastAPI

This skill provides comprehensive guidance for building APIs with FastAPI.

## Quick Navigation

| Topic              | Reference                           |
| ------------------ | ----------------------------------- |
| Getting started    | `references/first-steps.md`         |
| Path parameters    | `references/path-parameters.md`     |
| Query parameters   | `references/query-parameters.md`    |
| Request body       | `references/request-body.md`        |
| Validation         | `references/validation.md`          |
| Body advanced      | `references/body-advanced.md`       |
| Cookies/Headers    | `references/cookies-headers.md`     |
| Pydantic models    | `references/models.md`              |
| Forms/Files        | `references/forms-files.md`         |
| Error handling     | `references/error-handling.md`      |
| Path config        | `references/path-config.md`         |
| Dependencies       | `references/dependencies.md`        |
| Security           | `references/security.md`            |
| Middleware         | `references/middleware.md`          |
| CORS               | `references/cors.md`                |
| Database           | `references/sql-databases.md`       |
| Project structure  | `references/bigger-applications.md` |
| Background tasks   | `references/background-tasks.md`    |
| Metadata/Docs      | `references/metadata-docs.md`       |
| Testing            | `references/testing.md`             |
| Advanced responses | `references/responses-advanced.md`  |
| WebSockets         | `references/websockets.md`          |
| Templates          | `references/templates.md`           |
| Settings/Env vars  | `references/settings.md`            |
| Lifespan events    | `references/lifespan.md`            |
| OpenAPI advanced   | `references/openapi-advanced.md`    |

## When to Use

- Creating REST APIs with Python
- Adding endpoints with automatic validation
- Implementing OAuth2/JWT authentication
- Working with Pydantic models
- Adding dependency injection
- Configuring CORS, middleware
- Uploading files, handling forms
- Testing API endpoints

## Installation

Requires Python 3.10+. Install: `pip install "fastapi[standard]"` (full with uvicorn) or `pip install fastapi` (minimal). Add `python-multipart` for forms/files.

## Release Highlights (0.139.2 -> 0.141.1)

- **Frontend dev experience (`0.141.0`)**: `check_dir` on `app.frontend()` now defaults to `"auto"`, which skips the frontend-directory existence check (with a warning) when `FASTAPI_ENV=development` and enforces it otherwise. `fastapi dev` sets `FASTAPI_ENV=development` automatically unless already set, so running the dev server before the frontend is built no longer raises an error.
- **Frontend fixes (`0.141.1`)**: background tasks and response headers produced by dependencies used on frontend routes (dependency support was added in `0.139.0`) are now applied correctly instead of being silently dropped. `FASTAPI_ENV` is documented in the FastAPI CLI guide.
- **Dependency-injection memory refactor (`0.140.0` – `0.140.7`)**: internal dependency trees are no longer repeatedly flattened for OpenAPI generation, request-parameter resolution, and body-field handling, reducing memory use in large applications; the internal `lru_cache` limit for dependency resolution was also raised to fit bigger apps. This is an internal optimization with no required code changes.
- **Streaming fixes (`0.140.8` – `0.140.13`)**: `include_router()` no longer loses the declared stream item type from a nested router's `yield`-based endpoints; `response_model_*` params (e.g. `response_model_exclude`) are now honored on plain (non-generator) endpoints that `return` an `Iterable[Model]`, not only on `yield`-based ones; `status_code` set on SSE/JSONL streaming endpoints is now honored instead of always returning 200; a dedicated API reference page for `fastapi.sse` was added.
- **`jsonable_encoder` fix (`0.140.9`)**: `exclude_defaults` now propagates into dict keys and values, not only into top-level model fields.

## Release Highlights (0.137.0 -> 0.139.2)

- **Frontend serving (`0.138.0`)**: `app.frontend("/", directory="dist")` serves a built static frontend directly from the FastAPI app. `0.139.0` adds dependencies support in `app.frontend()`, enabling automatic cookie authentication for frontends, and `0.139.1` fixes fallback for dotted paths like `/users/john.doe`.
- **Router internals (`0.137.0`)**: `include_router()` now preserves `APIRouter`/`APIRoute` instances instead of cloning routes, so routes added after inclusion are reflected automatically and memory use drops. Custom `APIRouter`/`APIRoute` subclasses gain `.matches()`/`.handle()` (alpha) for advanced routing.
- **Thread safety (`0.139.2`)**: route building is refactored to be thread-safe, mainly relevant for tests running across parallel threads.

## Release Highlights (0.133.0 → 0.136.1)

- **0.134.0:** streaming JSON Lines and streaming binary data support using `yield`.
- **0.135.0:** first-class Server-Sent Events (SSE) support (`EventSourceResponse`).
- **0.135.1:** fix around `TaskGroup` usage in request async exit stack (stability fix).
- **0.136.1:** FastAPI updates its Pydantic v2 code to avoid deprecations and bumps Starlette to `1.0.0`.

## Patch Notes (0.136.2 → 0.136.3)

- SSE responses now validate event fields more strictly, so malformed `ServerSentEvent` payloads fail earlier instead of quietly streaming invalid frames.
- Header parameters no longer accept underscore-named incoming headers when `convert_underscores=True` (the default). If a client truly sends underscore headers, declare `Header(convert_underscores=False)` and verify that your proxy chain allows them.

## Quick Start

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

Run: `fastapi dev main.py`

## Core Patterns

### Type-Safe Parameters

```python
from typing import Annotated
from fastapi import Path, Query

@app.get("/items/{item_id}")
def read_item(
    item_id: Annotated[int, Path(ge=1)],
    q: Annotated[str | None, Query(max_length=50)] = None
):
    return {"item_id": item_id, "q": q}
```

### Request Body with Validation

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)

@app.post("/items/", response_model=Item)
def create_item(item: Item):
    return item
```

### Dependencies

```python
from fastapi import Depends

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
def list_users(db: Annotated[Session, Depends(get_db)]):
    return db.query(User).all()
```

### Authentication

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    return decode_token(token)

@app.get("/users/me")
def read_me(user: Annotated[User, Depends(get_current_user)]):
    return user
```

## API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI: `/openapi.json`

## Best Practices

- Use `Annotated[Type, ...]` for parameters
- Define Pydantic models for request/response
- Use `response_model` for output filtering
- Add `status_code` for proper HTTP codes
- Use `tags` for API organization
- Add `dependencies` at router/app level for auth

## Prohibitions

- ❌ Return raw database models (use response models)
- ❌ Store passwords in plain text (use bcrypt/passlib)
- ❌ Mix `Body` with `Form`/`File` in same endpoint
- ❌ Use sync blocking I/O in async endpoints
- ❌ Skip HTTPException for error handling

## Links

- [Documentation](https://fastapi.tiangolo.com/)
- [Releases](https://github.com/fastapi/fastapi/releases)
- [GitHub](https://github.com/fastapi/fastapi)
- [PyPI](https://pypi.org/project/fastapi/)
