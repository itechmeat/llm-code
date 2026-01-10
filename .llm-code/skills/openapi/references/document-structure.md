# OpenAPI Document Structure

Detailed anatomy of an OpenAPI Description (OAD) document.

## Root Object (OpenAPI Object)

The root of every OpenAPI document.

### Required Fields

| Field   | Type   | Description                            |
| ------- | ------ | -------------------------------------- |
| openapi | string | OAS version (e.g., `3.2.0`). REQUIRED. |
| info    | Info   | API metadata. REQUIRED.                |

### At Least One Required

At least one of these MUST be present:

- `paths` - Available API endpoints
- `webhooks` - Incoming webhook definitions
- `components` - Reusable components

### Optional Fields

| Field             | Type                   | Description                          |
| ----------------- | ---------------------- | ------------------------------------ |
| $self             | string                 | Self-assigned URI of this document   |
| jsonSchemaDialect | string                 | Default `$schema` for Schema Objects |
| servers           | [Server]               | Server connectivity info             |
| security          | [Security Requirement] | Global security requirements         |
| tags              | [Tag]                  | Metadata for operation grouping      |
| externalDocs      | External Documentation | Additional documentation             |

## Info Object

API metadata.

```yaml
info:
  title: Pet Store API # REQUIRED
  version: 1.0.0 # REQUIRED (API version)
  summary: A sample pet store API
  description: |
    Full API description.
    Supports **CommonMark** markdown.
  termsOfService: https://example.com/terms/
  contact:
    name: API Support
    url: https://www.example.com/support
    email: support@example.com
  license:
    name: Apache 2.0
    identifier: Apache-2.0 # SPDX identifier
    # OR use url (mutually exclusive with identifier)
    # url: https://www.apache.org/licenses/LICENSE-2.0.html
```

### Important Notes

- `info.version` is the API version, NOT the OAS version
- `license.identifier` and `license.url` are mutually exclusive
- All `description` fields support CommonMark 0.27+

## Server Object

Defines API server(s).

```yaml
servers:
  - url: https://api.example.com/v1
    description: Production server
    name: prod # Optional unique name

  - url: https://{username}.example.com:{port}/{basePath}
    description: Development server
    variables:
      username:
        default: demo
        description: User-specific subdomain
      port:
        enum: ["443", "8443"]
        default: "8443"
      basePath:
        default: v2
```

### URL Resolution

- Server URLs MAY be relative (resolved against document location)
- Path from `paths` is appended to server URL (no relative resolution)
- Default server if not specified: `url: /`

## Paths Object

Container for all API endpoints.

```yaml
paths:
  /pets:
    get:
      summary: List all pets
      responses:
        "200":
          description: A list of pets

  /pets/{petId}:
    parameters:
      - name: petId
        in: path
        required: true
        schema:
          type: string
    get:
      summary: Get a pet by ID
      responses:
        "200":
          description: A single pet
```

### Path Templating

- Path MUST begin with `/`
- Template variables: `{variableName}`
- Concrete paths match before templated
- Templates with same hierarchy but different names are invalid
  - ❌ `/pets/{petId}` and `/pets/{id}` cannot coexist

## Components Object

Holds reusable definitions.

```yaml
components:
  schemas:
    Pet:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string

  parameters:
    petId:
      name: petId
      in: path
      required: true
      schema:
        type: string

  responses:
    NotFound:
      description: Resource not found

  requestBodies:
    Pet:
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Pet"

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
```

### Component Name Restrictions

All component keys MUST match: `^[a-zA-Z0-9\.\-_]+$`

Valid: `User`, `User_1`, `User-Name`, `my.org.User`

## Multi-Document Structure

An OAD MAY span multiple documents connected by `$ref`.

### Entry Document

- Document where parsing begins
- Recommended naming: `openapi.json` or `openapi.yaml`
- Contains root OpenAPI Object

### Referenced Documents

- MUST have OpenAPI Object or Schema Object at root
- Connected via `$ref` fields

### Base URI Resolution

1. `$self` field (highest priority)
2. Encapsulating entity
3. Retrieval URI
4. Configured/default base

## Tags

Organize operations with tags.

```yaml
tags:
  - name: pets
    summary: Pet operations
    description: Everything about pets
    externalDocs:
      url: https://docs.example.com/pets

  - name: users
    summary: User operations
    parent: account # Hierarchical nesting (OAS 3.2+)

paths:
  /pets:
    get:
      tags: [pets] # Reference tags by name
```

### Tag Behavior

- Tags in operations don't need declaration in root `tags`
- Undeclared tags: tool-specific ordering
- Declared tags: ordered as listed
- Each tag name MUST be unique

## External Documentation

```yaml
externalDocs:
  description: Find more info here
  url: https://example.com/docs # REQUIRED, must be URI
```

## Specification Extensions

Extend the specification with custom fields.

```yaml
paths:
  /pets:
    x-rate-limit: 100 # Custom extension
    x-internal-only: true
    get:
      summary: List pets
```

### Rules

- Extension fields MUST begin with `x-`
- Reserved prefixes: `x-oai-`, `x-oas-`
- Value can be any valid JSON value
- Support is OPTIONAL per implementation
