# Parameters and Serialization

How to define and serialize API parameters.

## Parameter Locations

| `in` value  | Description                                       |
| ----------- | ------------------------------------------------- |
| path        | Part of the URL path (e.g., `/users/{id}`)        |
| query       | Query string parameters (e.g., `?page=1`)         |
| querystring | Entire query string as single parameter (OAS 3.2) |
| header      | HTTP request headers                              |
| cookie      | Cookie values                                     |

## Parameter Object

```yaml
parameters:
  - name: userId # REQUIRED
    in: path # REQUIRED
    required: true # REQUIRED for path params
    description: User identifier
    deprecated: false
    allowEmptyValue: false # Query only, deprecated
    schema:
      type: string
      format: uuid
    example: "123e4567-e89b-12d3-a456-426614174000"
```

## Path Parameters

MUST be `required: true` and match a `{template}` in the path.

```yaml
paths:
  /users/{userId}/orders/{orderId}:
    parameters:
      - name: userId
        in: path
        required: true # MUST be true
        schema:
          type: string
      - name: orderId
        in: path
        required: true
        schema:
          type: string
```

## Query Parameters

```yaml
parameters:
  - name: page
    in: query
    schema:
      type: integer
      minimum: 1
      default: 1

  - name: filter
    in: query
    style: deepObject # For nested objects
    explode: true
    schema:
      type: object
      properties:
        status:
          type: string
        createdAfter:
          type: string
          format: date
```

## Header Parameters

```yaml
parameters:
  - name: X-Request-ID
    in: header
    required: true
    schema:
      type: string
      format: uuid

  - name: Accept-Language
    in: header
    schema:
      type: string
      default: en
```

**Note:** Header names are case-insensitive per HTTP spec.

### Reserved Header Names

These parameter definitions are ignored (handled by OpenAPI):

- `Accept`
- `Content-Type`
- `Authorization`

## Cookie Parameters

```yaml
parameters:
  - name: sessionId
    in: cookie
    required: true
    schema:
      type: string

  - name: preferences
    in: cookie
    style: form
    explode: true
    schema:
      type: object
      properties:
        theme:
          type: string
        language:
          type: string
```

## Serialization Styles

### Style Options

| Style      | `in`          | Array Example (`[3,4,5]`)      | Object Example (`{a:1,b:2}`) |
| ---------- | ------------- | ------------------------------ | ---------------------------- |
| simple     | path, header  | `3,4,5`                        | `a,1,b,2`                    |
| label      | path          | `.3.4.5`                       | `.a.1.b.2`                   |
| matrix     | path          | `;id=3,4,5`                    | `;a=1;b=2` (explode)         |
| form       | query, cookie | `id=3,4,5` or `id=3&id=4&id=5` | `a=1&b=2` (explode)          |
| deepObject | query         | N/A                            | `id[a]=1&id[b]=2`            |

### Default Styles

| Location | Default Style | Default Explode |
| -------- | ------------- | --------------- |
| path     | simple        | false           |
| query    | form          | true            |
| header   | simple        | false           |
| cookie   | form          | true            |

### Explode Behavior

```yaml
# explode: false (default for simple)
# Array [1,2,3] → color=1,2,3
# Object {a:1,b:2} → color=a,1,b,2

# explode: true (default for form)
# Array [1,2,3] → color=1&color=2&color=3
# Object {a:1,b:2} → a=1&b=2
```

## Style Examples

### Simple Style (Path)

```yaml
/files/{path}:
  parameters:
    - name: path
      in: path
      required: true
      style: simple
      explode: false
      schema:
        type: array
        items:
          type: string
```

Input: `["docs", "readme.md"]` → `/files/docs,readme.md`

### Matrix Style (Path)

```yaml
/users{;id}:
  parameters:
    - name: id
      in: path
      required: true
      style: matrix
      schema:
        type: integer
```

Input: `5` → `/users;id=5`

### Label Style (Path)

```yaml
/calendar{.year,month}:
  parameters:
    - name: year
      in: path
      required: true
      style: label
      schema:
        type: integer
    - name: month
      in: path
      required: true
      style: label
      schema:
        type: integer
```

Input: `2024`, `3` → `/calendar.2024.3`

### Form Style (Query)

```yaml
/search:
  parameters:
    - name: tags
      in: query
      style: form
      explode: true # Default for form
      schema:
        type: array
        items:
          type: string
```

Input: `["red", "blue"]` → `?tags=red&tags=blue`

### Deep Object Style (Query)

```yaml
/filter:
  parameters:
    - name: filter
      in: query
      style: deepObject
      explode: true # Required for deepObject
      schema:
        type: object
        properties:
          status:
            type: string
          dateRange:
            type: object
            properties:
              start:
                type: string
              end:
                type: string
```

Input: `{status: "active", dateRange: {start: "2024-01"}}` →
`?filter[status]=active&filter[dateRange][start]=2024-01`

## Content-Based Serialization

For complex serialization, use `content` instead of `schema`:

```yaml
parameters:
  - name: coordinates
    in: query
    content:
      application/json:
        schema:
          type: object
          required: [lat, long]
          properties:
            lat:
              type: number
            long:
              type: number
        examples:
          location:
            value:
              lat: 40.7128
              long: -74.0060
            serializedValue: '{"lat":40.7128,"long":-74.0060}'
```

Result: `?coordinates={"lat":40.7128,"long":-74.0060}` (URL-encoded)

## Allow Reserved Characters

```yaml
parameters:
  - name: callback
    in: query
    allowReserved: true # Don't percent-encode reserved chars
    schema:
      type: string
```

Use for URLs or values containing `:/?#[]@!$&'()*+,;=`

## Empty Values

```yaml
parameters:
  - name: refresh
    in: query
    allowEmptyValue: true # Deprecated, avoid
    schema:
      type: boolean
```

Allows `?refresh=` or `?refresh` (presence indicates true).

**Note:** `allowEmptyValue` is deprecated. Use nullable or boolean instead.

## Parameter Examples

### Single Example

```yaml
parameters:
  - name: userId
    in: path
    required: true
    schema:
      type: string
    example: "usr_abc123"
```

### Multiple Examples

```yaml
parameters:
  - name: format
    in: query
    schema:
      type: string
    examples:
      json:
        summary: JSON format
        value: json
      xml:
        summary: XML format
        value: xml
      csv:
        summary: CSV format
        value: csv
```

### Serialization Examples

```yaml
parameters:
  - name: ids
    in: query
    style: form
    explode: false
    schema:
      type: array
      items:
        type: integer
    examples:
      multiple:
        dataValue: [1, 2, 3]
        serializedValue: "ids=1,2,3"
```

## Header Object

Same as Parameter Object but without `name` and `in`:

```yaml
components:
  headers:
    X-Rate-Limit:
      description: Rate limit remaining
      schema:
        type: integer
    X-Request-ID:
      required: true
      schema:
        type: string
        format: uuid
```

Usage in responses:

```yaml
responses:
  "200":
    headers:
      X-Rate-Limit:
        $ref: "#/components/headers/X-Rate-Limit"
```

## Encoding Object

For multipart/form-data and application/x-www-form-urlencoded:

```yaml
requestBody:
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          file:
            type: string
            format: binary
          metadata:
            type: object
      encoding:
        file:
          contentType: image/png, image/jpeg
        metadata:
          contentType: application/json
          headers:
            X-Custom-Header:
              schema:
                type: string
```

### Encoding Fields

| Field         | Description                      |
| ------------- | -------------------------------- |
| contentType   | Media type(s) for the property   |
| headers       | Additional headers for multipart |
| style         | Serialization style              |
| explode       | Explode behavior                 |
| allowReserved | Allow reserved characters        |

## Common Patterns

### Pagination

```yaml
parameters:
  - name: page
    in: query
    schema:
      type: integer
      minimum: 1
      default: 1
  - name: limit
    in: query
    schema:
      type: integer
      minimum: 1
      maximum: 100
      default: 20
  - name: offset
    in: query
    schema:
      type: integer
      minimum: 0
```

### Filtering

```yaml
parameters:
  - name: filter
    in: query
    style: deepObject
    explode: true
    schema:
      type: object
      additionalProperties: true
  - name: sort
    in: query
    schema:
      type: string
      pattern: "^[+-]?[a-zA-Z_]+$"
      example: "-createdAt"
```

### ID Parameter (Reusable)

```yaml
components:
  parameters:
    resourceId:
      name: id
      in: path
      required: true
      schema:
        type: string
        pattern: "^[a-z]+_[a-zA-Z0-9]+$"
      example: "usr_abc123"
```
