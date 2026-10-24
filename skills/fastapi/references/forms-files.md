# Forms and File Uploads

Form data handling and file uploads in FastAPI.

## Form Data

```python
from typing import Annotated
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/login/")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    return {"username": username}
```

### Key Points

- **Dependency**: `pip install python-multipart`
- **Import**: `from fastapi import Form`
- **Encoding**: `application/x-www-form-urlencoded`
- **Validation**: Same as `Body()`, `Query()`, `Path()`

### OAuth2 Password Flow

```python
# OAuth2 spec requires exact field names
@app.post("/token")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    # Authenticate user
    return {"access_token": token}
```

## File Uploads

### bytes Parameter

```python
from typing import Annotated
from fastapi import FastAPI, File

@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}
```

- Entire file stored in memory
- Good for small files only
- Uploaded file positions are preserved when converting a file to `bytes` (`0.156.8`)
- `byte` file list parameters handle empty values correctly (`0.143.5`)

### UploadFile Parameter

```python
from fastapi import FastAPI, UploadFile

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
```

#### UploadFile Attributes

| Attribute      | Type                   | Description                    |
| -------------- | ---------------------- | ------------------------------ |
| `filename`     | `str`                  | Original filename              |
| `content_type` | `str`                  | MIME type (e.g., `image/jpeg`) |
| `file`         | `SpooledTemporaryFile` | Python file object             |

#### Async Methods

```python
contents = await myfile.read()      # Read all bytes
await myfile.seek(0)                # Go to start
await myfile.write(data)            # Write bytes
await myfile.close()                # Close file
```

#### Sync Access (in def functions)

```python
contents = myfile.file.read()
```

### Optional File Upload

```python
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No file sent"}
    return {"filename": file.filename}
```

### File with Metadata

```python
@app.post("/uploadfile/")
async def create_upload_file(
    file: Annotated[UploadFile, File(description="A file read as UploadFile")]
):
    return {"filename": file.filename}
```

## Multiple File Uploads

```python
from fastapi import FastAPI, File, UploadFile

@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}

# With metadata
@app.post("/uploadfiles/")
async def create_upload_files(
    files: Annotated[list[UploadFile], File(description="Multiple files")]
):
    return {"filenames": [file.filename for file in files]}
```

## Forms and Files Together

```python
from fastapi import FastAPI, File, Form, UploadFile

@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()]
):
    return {
        "file_size": len(file),
        "fileb_content_type": fileb.content_type,
        "token": token
    }
```

## Form Models

Declare form fields with a Pydantic model and mark the parameter with `Form()`:

```python
from typing import Annotated
from fastapi import FastAPI, Form
from pydantic import BaseModel

app = FastAPI()

class FormData(BaseModel):
    username: str
    password: str

@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data
```

Each model field is extracted from the form data and validated like an individual `Form` parameter, including the browser form rules below. Use `model_config = {"extra": "forbid"}` to reject undeclared form fields.

### Optional Form Models (0.158.2)

Add `| None` and a default of `None` to make the whole group optional:

```python
class Profile(BaseModel):
    name: str
    age: int

@app.post("/profiles/")
async def create_profile(
    token: Annotated[str, Form()],
    profile: Annotated[Profile | None, Form()] = None,
):
    return {"token": token, "profile": profile}
```

- If neither field is sent, `profile` is `None`.
- If either is sent, the model is validated and both fields are required.
- Using `| None` without a default keeps the parameter required.
- An empty submitted value also counts as supplying a field.
- Unknown fields follow the model's extra configuration; ignored extras do not make the model present.

### Combining Form Models (0.158.0)

Several form models can be combined with individual `Form` parameters:

```python
class Profile(BaseModel):
    name: str

class Preferences(BaseModel):
    tags: list[str] = []

@app.post("/profiles/")
async def create_profile(
    profile: Annotated[Profile, Form()],
    preferences: Annotated[Preferences, Form()],
    token: Annotated[str, Form()],
):
    return {"profile": profile, "preferences": preferences, "token": token}
```

The client sends `name`, `tags`, and `token` as flat form fields — there is no `profile`/`preferences` prefix. Each model receives its own fields and validates them independently. If two declarations use the same field name, each validates it; keep the types compatible so the OpenAPI schema stays consistent.

### Unions of Form Models (0.159.1)

A single form parameter can accept a union of models:

```python
from typing import Literal

class Person(BaseModel):
    kind: Literal["person"]
    name: str

class Company(BaseModel):
    kind: Literal["company"]
    company_name: str

@app.post("/contacts/")
async def create_contact(
    contact: Annotated[Person | Company | None, Form(discriminator="kind")] = None,
):
    return contact
```

If no form fields are sent, `contact` is `None`. The discriminator selects the model to validate. Unions of form models apply the same browser form handling as individual models (`0.153.0`).

### Form Models and Files

```python
@app.post("/profiles/")
async def create_profile(profile: Annotated[Profile, Form()], avatar: UploadFile):
    return {"profile": profile, "filename": avatar.filename}
```

The client sends the `name` field and the `avatar` file as `multipart/form-data`.

## Browser Form Semantics (0.147.0 - 0.150.0)

HTML forms and browsers do not send "no value" the way a JSON client does. FastAPI applies these rules to `Form` parameters and form models:

| Browser sends                                          | FastAPI treats it as      |
| ----------------------------------------------------- | ------------------------- |
| Text input left empty (`""`)                          | Missing value             |
| Unchecked checkbox (field absent from the payload)    | `False`                   |
| File input with no file selected (empty name/content) | Missing value             |
| Empty string inside a list of values                  | An empty string (kept)    |

Details:

- **Omitted booleans become `False` (`0.147.0`)**: omitted `bool` and `bool | None` form fields are interpreted as `False`, matching an unchecked checkbox. This applies to individual `Form` parameters and to form models, including required fields and fields whose default is `True` or `None`. The inferred value counts as explicitly set, so it appears in `model_dump(exclude_unset=True)`. JSON requests and direct Pydantic validation are unchanged.
- **Empty scalars are missing (`0.149.0`)**: browsers submit empty text inputs as `""`. In form models — and in individual `Form` parameters — an empty scalar value is treated as missing: required fields return a validation error, fields with a default or default factory use it, and the field stays unset in `model_dump(exclude_unset=True)`. Empty strings inside lists are preserved.
- **Unselected files are missing (`0.150.0`)**: browsers submit a file part with an empty filename and empty content when nothing was selected. FastAPI treats it as missing: required file fields return a validation error, fields with defaults use them, and unselected inputs are ignored in lists of files. A named zero-byte file is still accepted.
- **Unions follow the same rules (`0.153.0`)**: unions of form models apply the same browser form handling as individual models.

## Form Media Types in OpenAPI (0.158.1)

Forms are encoded as `application/x-www-form-urlencoded`, or `multipart/form-data` when files are included. FastAPI preserves these media types in the generated OpenAPI.

Set `media_type` explicitly to describe a multipart form:

```python
token: Annotated[str, Form(media_type="multipart/form-data")]
```

Setting it on one parameter is enough when combining form parameters or models.

## Encoding Types

| Content Type                        | When Used           |
| ----------------------------------- | ------------------- |
| `application/x-www-form-urlencoded` | Forms without files |
| `multipart/form-data`               | Forms with files    |

## Prohibitions

- ❌ Cannot mix `Body` (JSON) with `Form`/`File` in same endpoint
- ❌ Don't use `bytes` for large files (memory)

## Recipes

### File Upload with Validation

```python
from fastapi import HTTPException

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/upload/")
async def upload_file(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file type")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(400, "File too large")

    # Process file...
    return {"filename": file.filename}
```

### Save Uploaded File

```python
import shutil
from pathlib import Path

UPLOAD_DIR = Path("uploads")

@app.post("/upload/")
async def upload_file(file: UploadFile):
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "path": str(file_path)}
```
