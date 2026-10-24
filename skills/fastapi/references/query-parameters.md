# Query Parameters

Parameters passed via URL query string (`?key=value&key2=value2`).

## Basic Usage

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return items[skip : skip + limit]
```

URL: `http://127.0.0.1:8000/items/?skip=20&limit=5`

## Parameter Types

### Required Parameters

```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, needy: str):
    return {"item_id": item_id, "needy": needy}
```

No default = required. Missing parameter returns error.

### Optional Parameters

```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

### Default Values

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return items[skip : skip + limit]
```

## Boolean Conversion

FastAPI auto-converts truthy strings to `bool`:

```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, short: bool = False):
    ...
```

All these evaluate to `True`:

- `?short=1`
- `?short=True`
- `?short=true`
- `?short=on`
- `?short=yes`

## Mixed Parameters

Combine path and query parameters freely:

```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,           # path
    item_id: str,           # path
    q: str | None = None,   # query, optional
    short: bool = False     # query, default
):
    ...
```

FastAPI distinguishes by:

- **Path parameters**: Declared in route path `{param}`
- **Query parameters**: Other function parameters

## Common Patterns

### Pagination

```python
@app.get("/items/")
async def list_items(skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()
```

### Filtering

```python
@app.get("/items/")
async def search_items(
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = None
):
    ...
```

### Required + Optional Mix

```python
@app.get("/search/")
async def search(
    query: str,                    # required
    page: int = 1,                 # default
    per_page: int | None = None    # optional
):
    ...
```

## Query Parameter Models (0.115.0+)

Group related query parameters in a Pydantic model and declare it with `Query()`:

```python
from typing import Annotated, Literal
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query
```

Each field is read from the query string at the same level — there is no `filter_query.` prefix in the URL. FastAPI extracts the field values and hands you the model, so the model applies its own defaults, field validators, and model validators.

Use `model_config = {"extra": "forbid"}` to reject undeclared query parameters:

```json
{
  "detail": [
    {
      "type": "extra_forbidden",
      "loc": ["query", "tool"],
      "msg": "Extra inputs are not permitted",
      "input": "plumbus"
    }
  ]
}
```

### Optional Query Parameter Models (0.159.0)

Add `| None` and a default of `None` to make the whole group optional:

```python
from datetime import date

class DateRange(BaseModel):
    start: date
    end: date

@app.get("/items/")
async def read_items(
    limit: int = 10,
    date_range: Annotated[DateRange | None, Query()] = None,
):
    return {"limit": limit, "date_range": date_range}
```

- If neither `start` nor `end` is sent, `date_range` is `None`.
- If either is sent, FastAPI validates the model and requires both fields.
- Using `| None` without a default keeps the parameter required.
- Unknown parameters follow the model's extra configuration; ignored extras do not make the model present.
- OpenAPI lists the group's fields individually and marks them as optional.

Optional header and cookie parameter models work the same way — see `references/cookies-headers.md`.

### Combining Parameter Models (0.157.0)

Several query, header, and cookie parameter models can be combined with each other and with individual parameters:

```python
class Pagination(BaseModel):
    limit: int = Field(10, ge=1)
    offset: int = Field(0, ge=0)

class Filters(BaseModel):
    tags: list[str] = []

@app.get("/items/")
def read_items(
    pagination: Annotated[Pagination, Query()],
    filters: Annotated[Filters, Query()],
    search: str | None = None,
):
    return {"pagination": pagination, "filters": filters, "search": search}
```

Request: `/items/?limit=5&offset=10&tags=red&tags=blue&search=shirt`

- The parameters stay at the same level — there are no `pagination` or `filters` keys in the query string.
- Each model receives its own fields; Pydantic applies each model's defaults and validators.
- If two models share a parameter name or alias, each model validates that parameter independently. Use distinct names or aliases for independent values, and keep shared declarations type-compatible, because OpenAPI lists a shared parameter only once.
- With `extra="forbid"`, parameters declared elsewhere in the same operation or its dependencies are allowed; undeclared parameters are still rejected.
- The same applies when the models or individual parameters are declared in dependencies.

## Defaults Are Not User Input (0.148.0)

A missing query parameter is not validated against its default, and applying the default does not mark the field as explicitly set:

```python
q: Annotated[str, Query(min_length=3, validate_default=True)] = "abc"
```

- Defaults are validated only when `validate_default=True` is set.
- `model_dump(exclude_unset=True)` excludes a field that only got its default.
- Default factories run once per request.
- Validation errors no longer include injected defaults in `input`.

See `references/validation.md` for the full default-handling rules.
