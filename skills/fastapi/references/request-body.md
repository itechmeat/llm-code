# Request Body

Send JSON data from client to API using Pydantic models.

## Basic Example

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## Pydantic Model Rules

- Required fields: no default value
- Optional fields: `= None`
- Fields with defaults: `= value`

Valid JSON for above model:

```json
{"name": "Foo", "price": 45.2}
{"name": "Foo", "description": "A thing", "price": 45.2, "tax": 3.5}
```

## What FastAPI Does Automatically

1. Reads request body as JSON
2. Converts types (string → int, etc.)
3. Validates data structure
4. Returns clear errors for invalid data
5. Provides editor autocomplete for model attributes
6. Generates JSON Schema for OpenAPI docs

## Using the Model

```python
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()  # Convert to dict
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
```

## Combining Parameters

FastAPI distinguishes parameter types automatically:

```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,              # Path parameter
    item: Item,                # Request body (Pydantic model)
    q: str | None = None       # Query parameter
):
    return {"item_id": item_id, **item.model_dump(), "q": q}
```

Recognition rules:

- Declared in path → **path parameter**
- Pydantic model → **request body**
- Singular type (str, int, etc.) → **query parameter**

## HTTP Methods for Body

- `POST` - Create (most common)
- `PUT` - Update/Replace
- `PATCH` - Partial update
- `DELETE` - Delete (rarely has body)

⚠️ `GET` with body is discouraged (undefined behavior in specs).

## Multiple Body Parameters

Multiple Pydantic models = JSON keys by parameter names:

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str
    full_name: str | None = None

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    return {"item_id": item_id, "item": item, "user": user}
```

Expected body:

```json
{
  "item": { "name": "Foo", "price": 42.0 },
  "user": { "username": "dave", "full_name": "Dave Grohl" }
}
```

## Singular Values in Body

Use `Body()` for non-model values in body:

```python
from typing import Annotated
from fastapi import Body

@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body()]
):
    return {"item_id": item_id, "importance": importance}
```

Expected body:

```json
{
    "item": {...},
    "user": {...},
    "importance": 5
}
```

## Embed Single Body Parameter

Force key wrapping for single model:

```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[Item, Body(embed=True)]
):
    return {"item_id": item_id, "item": item}
```

With `embed=True`:

```json
{ "item": { "name": "Foo", "price": 42.0 } }
```

Without `embed=True`:

```json
{ "name": "Foo", "price": 42.0 }
```

## `null` Is Not an Omitted Value (0.151.0)

JSON bodies distinguish an explicit `null` from an omitted key:

| Client sends                          | Result                                                                       |
| ------------------------------------- | ---------------------------------------------------------------------------- |
| key omitted                           | Default (or default factory) applies; the field is not validated against it  |
| `"description": null`                 | Validated as `None` — nullable types accept it, non-nullable types reject it |
| whole body is `null` (embedded/multi) | Validation error                                                              |

Details:

- `null` is validated as `None`. A nullable type (`str | None`) accepts it; a non-nullable type (`str`) rejects it **even when a default is defined**. Clients that used `null` to request the default should omit the value instead.
- Defaults and default factories apply only when the value is omitted.
- When a JSON object is expected because of `Body(embed=True)` or multiple body parameters, sending `null` as the entire body returns a validation error.
- This applies to parameters inside JSON objects and to parameters representing the entire body.

## Body Defaults Are Not Validated (0.148.0)

`Body(validate_default=True)` is honored, so an omitted body parameter can opt into default validation:

```python
from typing import Annotated
from fastapi import Body

@app.post("/items/")
async def create_item(
    item: Annotated[Item, Body(validate_default=True)],
):
    ...
```

Without it, a default is not validated against the parameter's constraints. See `references/validation.md` for the full default-handling rules.

## Field Validation

Use `Field` from Pydantic for model attributes:

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None,
        title="The description of the item",
        max_length=300
    )
    price: float = Field(gt=0, description="Must be greater than zero")
    tax: float | None = None
```

`Field` parameters: same as `Query`, `Path`, `Body`.

## Nested Models

Use Pydantic models as types in other models:

```python
from pydantic import BaseModel, HttpUrl

class Image(BaseModel):
    url: HttpUrl  # Validated URL
    name: str

class Item(BaseModel):
    name: str
    price: float
    images: list[Image] | None = None
```

## Special Types

- `set[str]` - Unique items, deduplicated
- `list[str]` - Regular list
- `dict[int, float]` - Keys convert from JSON strings
- `HttpUrl` - Validated URL
- `EmailStr` - Validated email (requires `pydantic[email]`)

## Bodies of Pure Lists

```python
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images
```

## Arbitrary Dict Bodies

```python
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights
```

JSON keys (strings) are converted to `int`.

## Extra Data Types

| Type                 | Request/Response Format |
| -------------------- | ----------------------- |
| `UUID`               | String                  |
| `datetime.datetime`  | ISO 8601 string         |
| `datetime.date`      | ISO 8601 string         |
| `datetime.time`      | ISO 8601 string         |
| `datetime.timedelta` | Float (total seconds)   |
| `bytes`              | String (binary format)  |
| `Decimal`            | Float                   |
| `frozenset`          | List (unique items)     |

```python
from datetime import datetime, timedelta
from uuid import UUID

@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
):
    start_process = start_datetime + process_after
    return {"item_id": item_id, "start_process": start_process}
```
