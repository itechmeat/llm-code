# Advanced Responses

Custom responses, status codes, cookies, headers for FastAPI.

## Return Response Directly

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

@app.get("/item/")
def read_item():
    # Use jsonable_encoder for datetime, Pydantic models etc
    data = jsonable_encoder({"created": datetime.now()})
    return JSONResponse(content=data)
```

## Custom Response Types

```python
from fastapi.responses import (
    HTMLResponse,      # text/html
    PlainTextResponse, # text/plain
    JSONResponse,      # application/json (default)
    ORJSONResponse,    # Fast JSON (pip install orjson)
    UJSONResponse,     # Fast JSON (pip install ujson)
    RedirectResponse,  # HTTP redirect
    StreamingResponse, # Streaming content
    FileResponse       # File downloads
)

# HTML Response
@app.get("/", response_class=HTMLResponse)
def get_html():
    return "<h1>Hello</h1>"

# Streaming Response
@app.get("/stream")
def stream():
    def generate():
        for i in range(10):
            yield f"chunk {i}\n"
    return StreamingResponse(generate(), media_type="text/plain")

# File Response
@app.get("/file")
def get_file():
    return FileResponse(
        path="report.pdf",
        filename="download.pdf",
        media_type="application/pdf"
    )

# Redirect
@app.get("/old")
def redirect():
    return RedirectResponse(url="/new", status_code=301)
```

## Default Response Class

```python
from fastapi.responses import ORJSONResponse

# App-wide default
app = FastAPI(default_response_class=ORJSONResponse)

# Endpoint-specific
@app.get("/items/", response_class=ORJSONResponse)
def read_items():
    return [{"id": 1}]
```

## Additional Status Codes

```python
from fastapi import status
from fastapi.responses import JSONResponse

@app.put("/items/{item_id}")
def upsert_item(item_id: str, item: Item):
    if item_id in items:
        items[item_id] = item
        return item  # 200 default
    else:
        items[item_id] = item
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(item)
        )
```

## Dynamic Status Code

```python
from fastapi import Response

@app.put("/items/{item_id}")
def update_item(item_id: str, response: Response):
    if item_id not in items:
        response.status_code = status.HTTP_201_CREATED
    return {"item_id": item_id}
```

## Response Cookies

```python
from fastapi import Response

# Via Response parameter
@app.post("/login")
def login(response: Response):
    response.set_cookie(
        key="session",
        value="abc123",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=3600
    )
    return {"message": "logged in"}

# Via direct Response
@app.post("/login")
def login():
    response = JSONResponse(content={"message": "logged in"})
    response.set_cookie(key="session", value="abc123")
    return response

# Delete cookie
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="session")
    return {"message": "logged out"}
```

## Response Headers

```python
from fastapi import Response

# Via Response parameter
@app.get("/items/")
def read_items(response: Response):
    response.headers["X-Custom"] = "value"
    response.headers["Cache-Control"] = "max-age=3600"
    return {"items": []}

# Via direct Response
@app.get("/items/")
def read_items():
    return JSONResponse(
        content={"items": []},
        headers={"X-Custom": "value"}
    )
```

Note: Custom headers with `X-` prefix. For CORS, expose custom headers in `CORSMiddleware(expose_headers=[...])`.

## Multiple Response Docs (OpenAPI)

```python
from fastapi import HTTPException
from pydantic import BaseModel

class Item(BaseModel):
    name: str

class Message(BaseModel):
    message: str

@app.get(
    "/items/{item_id}",
    response_model=Item,
    responses={
        200: {"model": Item, "description": "Item found"},
        404: {"model": Message, "description": "Item not found"},
        422: {"description": "Validation error"}
    }
)
def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]
```

## Combine Response Info

```python
responses = {
    404: {"description": "Not found"},
    403: {"description": "Forbidden"}
}

@app.get("/users/{user_id}", responses={**responses, 200: {"model": User}})
def read_user(user_id: int):
    ...
```
