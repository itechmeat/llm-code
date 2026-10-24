# Parameter Validation

Advanced validation for Query, Path, Header, Cookie parameters.

## Query Validation with `Query`

```python
from typing import Annotated
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(
    q: Annotated[str | None, Query(max_length=50)] = None
):
    return {"q": q}
```

## String Validations

```python
q: Annotated[str | None, Query(
    min_length=3,
    max_length=50,
    pattern="^[a-z]+$"  # Regex pattern
)] = None
```

## Numeric Validations (Path/Query)

```python
from fastapi import Path

@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(ge=1, le=1000)],  # 1 ≤ value ≤ 1000
    size: Annotated[float, Query(gt=0, lt=100)]   # 0 < value < 100
):
    ...
```

| Parameter | Meaning               |
| --------- | --------------------- |
| `gt`      | Greater than          |
| `ge`      | Greater than or equal |
| `lt`      | Less than             |
| `le`      | Less than or equal    |

## Metadata for Documentation

```python
q: Annotated[str | None, Query(
    title="Search query",
    description="Full-text search in item names",
    min_length=3,
    max_length=50,
    deprecated=True  # Shows as deprecated in docs
)] = None
```

## Alias Parameter Name

```python
# URL: /items/?item-query=foo
@app.get("/items/")
async def read_items(
    q: Annotated[str | None, Query(alias="item-query")] = None
):
    return {"q": q}
```

## Multiple Values (List)

```python
# URL: /items/?q=foo&q=bar
@app.get("/items/")
async def read_items(
    q: Annotated[list[str] | None, Query()] = None
):
    return {"q": q}  # ["foo", "bar"]
```

With defaults:

```python
q: Annotated[list[str], Query()] = ["default1", "default2"]
```

## Required Parameters with Validation

```python
# Required (no default)
q: Annotated[str, Query(min_length=3)]

# Required but can be None
q: Annotated[str | None, Query(min_length=3)]  # No default!
```

## Custom Validation

```python
from pydantic import AfterValidator

def validate_id(value: str) -> str:
    if not value.startswith(("isbn-", "imdb-")):
        raise ValueError("ID must start with isbn- or imdb-")
    return value

@app.get("/items/")
async def read_items(
    id: Annotated[str, AfterValidator(validate_id)]
):
    ...
```

## Exclude from OpenAPI

```python
hidden: Annotated[str | None, Query(include_in_schema=False)] = None
```

## Extra JSON Schema Properties (0.155.0)

The deprecated `**extra` keyword arguments were removed from `Path`, `Query`, `Header`, `Cookie`, `Body`, `Form`, and `File`. Unknown keyword arguments now raise `TypeError`.

To add custom properties to the generated JSON Schema, use `json_schema_extra`:

```python
# ✅ 0.155.0+
q: Annotated[str | None, Query(json_schema_extra={"custom": "value"})] = None

# ❌ removed in 0.155.0 — raises TypeError
q: Annotated[str | None, Query(custom="value")] = None
```

The same applies to `Path`, `Header`, `Cookie`, `Body`, `Form`, and `File`.

## Defaults Are Not Validated by Default (0.148.0)

Defaults for omitted `Query`, `Header`, `Cookie`, and `Form` parameters — and for the fields of parameter models — are no longer treated as user input:

- The default is **not** validated unless `validate_default=True` is set.
- Applying a default does **not** mark the field as explicitly set, so `model_dump(exclude_unset=True)` excludes it.
- Default factories run once per request.
- Validation errors no longer include injected defaults in `input`.

```python
from pydantic import BaseModel, Field

# Individual parameter
q: Annotated[str, Query(min_length=3, validate_default=True)] = "abc"

# Field of a parameter model
class FilterParams(BaseModel):
    limit: int = Field(10, gt=0, validate_default=True)
```

`Body(validate_default=True)` is honored too. If you relied on validators running for omitted values, enable default validation explicitly.

## Pydantic Validation Options (0.154.0)

Request parameters accept Pydantic validation options, so a parameter can use the same rules as a model field:

```python
q: Annotated[str, Query(validate_default=True, strict=False)]
```

Available options include `validate_default`, `strict`, `discriminator`, `union_mode`, `fail_fast`, `multiple_of`, `allow_inf_nan`, `max_digits`, `decimal_places`, `alias_priority`, `validation_alias`, and `serialization_alias`.

## Alias Choices

`alias` accepts an `AliasChoices` instance to read a parameter from more than one name:

```python
from pydantic import AliasChoices

q: Annotated[str | None, Query(alias=AliasChoices("q", "search"))] = None
```

`AliasChoices` is supported for query/header/cookie parameters (`0.156.3`), path parameters (`0.156.5`), named JSON body parameters, and form model extraction (`0.156.4`). For form and file parameters, validation error locations report the correct alias (`0.156.7`).

## Best Practice: Use Annotated

```python
# ✅ Recommended (Python 3.9+)
q: Annotated[str | None, Query(max_length=50)] = None

# ❌ Old style (avoid)
q: str | None = Query(default=None, max_length=50)
```
