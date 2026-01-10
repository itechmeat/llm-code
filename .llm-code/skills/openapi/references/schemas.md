# Schemas and Data Types

OpenAPI uses JSON Schema (Draft 2020-12) for data modeling.

## JSON Schema Types

| Type    | Description                  | Example            |
| ------- | ---------------------------- | ------------------ |
| null    | Null value                   | `null`             |
| boolean | True or false                | `true`, `false`    |
| object  | Key-value pairs              | `{"key": "value"}` |
| array   | Ordered list                 | `[1, 2, 3]`        |
| number  | Any numeric value            | `3.14`, `-42`      |
| string  | Text                         | `"hello"`          |
| integer | Whole numbers (OAS-specific) | `42`, `-1`         |

## Basic Schema Definitions

### String

```yaml
type: string
minLength: 1
maxLength: 255
pattern: "^[a-zA-Z]+$" # Regex pattern
```

### Numeric

```yaml
type: number
minimum: 0
maximum: 100
exclusiveMinimum: 0              # > 0, not >= 0
multipleOf: 0.01                 # Precision constraint

type: integer
format: int32                    # 32-bit signed
format: int64                    # 64-bit signed
```

### Boolean

```yaml
type: boolean
default: false
```

### Array

```yaml
type: array
items:
  type: string
minItems: 1
maxItems: 100
uniqueItems: true # No duplicates
```

### Object

```yaml
type: object
required: # Required properties
  - id
  - name
properties:
  id:
    type: string
  name:
    type: string
  age:
    type: integer
additionalProperties: false # No extra properties
```

## Format Keyword

Common formats for semantic meaning:

| Format        | Type    | Description               |
| ------------- | ------- | ------------------------- |
| int32         | integer | 32-bit signed integer     |
| int64         | integer | 64-bit signed integer     |
| float         | number  | Single precision          |
| double        | number  | Double precision          |
| byte          | string  | Base64 encoded            |
| binary        | string  | Binary data               |
| date          | string  | Full-date (RFC 3339)      |
| date-time     | string  | Date-time (RFC 3339)      |
| duration      | string  | Duration (RFC 3339)       |
| password      | string  | Hint for UI masking       |
| email         | string  | Email address             |
| uri           | string  | URI (RFC 3986)            |
| uri-reference | string  | URI or relative reference |
| uuid          | string  | UUID                      |
| hostname      | string  | Internet hostname         |
| ipv4          | string  | IPv4 address              |
| ipv6          | string  | IPv6 address              |

## Nullable Values (OAS 3.1+)

```yaml
# Use type array for nullable
type: [string, "null"]

# Or with oneOf
oneOf:
  - type: string
  - type: "null"
```

## Composition Keywords

### allOf (AND)

All schemas must be satisfied:

```yaml
allOf:
  - $ref: "#/components/schemas/BaseModel"
  - type: object
    properties:
      extraField:
        type: string
```

**Use case:** Inheritance, extending base schemas.

### oneOf (XOR)

Exactly one schema must match:

```yaml
oneOf:
  - $ref: "#/components/schemas/Cat"
  - $ref: "#/components/schemas/Dog"
```

**Use case:** Polymorphism, mutually exclusive options.

### anyOf (OR)

At least one schema must match:

```yaml
anyOf:
  - type: string
  - type: number
```

**Use case:** Flexible types, multiple valid formats.

### not

Schema must NOT match:

```yaml
not:
  type: string
  pattern: "^admin" # Cannot start with "admin"
```

## Discriminator Object

Helps parsers identify the correct schema in polymorphic types.

```yaml
Pet:
  oneOf:
    - $ref: "#/components/schemas/Cat"
    - $ref: "#/components/schemas/Dog"
    - $ref: "#/components/schemas/Fish"
  discriminator:
    propertyName: petType # Property that identifies type
    mapping:
      cat: "#/components/schemas/Cat"
      dog: "#/components/schemas/Dog"
      fish: "#/components/schemas/Fish"
    defaultMapping: Fish # Default if no match (OAS 3.2+)

Cat:
  type: object
  required: [petType]
  properties:
    petType:
      const: "cat" # Fixed value
    name:
      type: string
    huntingSkill:
      type: string
```

### Discriminator Mapping

- **Implicit:** Uses schema name (e.g., `Cat` → `#/components/schemas/Cat`)
- **Explicit:** Define custom mappings
- Property value determines which schema applies

## Enum and Const

### Enum (multiple allowed values)

```yaml
status:
  type: string
  enum:
    - pending
    - active
    - completed
    - cancelled
```

### Const (single value)

```yaml
type:
  const: "user" # Must be exactly "user"
```

## Default Values

```yaml
properties:
  status:
    type: string
    default: pending # Default if not provided
  count:
    type: integer
    default: 0
```

**Note:** `default` documents receiver behavior, doesn't insert values.

## Read-Only and Write-Only

```yaml
properties:
  id:
    type: string
    readOnly: true # Sent in responses only
  password:
    type: string
    writeOnly: true # Sent in requests only
```

## Deprecated Properties

```yaml
properties:
  oldField:
    type: string
    deprecated: true
    description: Use newField instead
```

## External Documentation

```yaml
User:
  type: object
  externalDocs:
    description: User model documentation
    url: https://docs.example.com/models/user
```

## Binary Data

### Raw Binary (multipart, octet-stream)

```yaml
# No type, indicate binary with contentMediaType
contentMediaType: image/png
```

### Encoded Binary (JSON context)

```yaml
type: string
contentMediaType: image/png
contentEncoding: base64 # or base64url
```

## Examples in Schemas

```yaml
User:
  type: object
  properties:
    id:
      type: string
      example: "usr_123" # Deprecated, use examples
    name:
      type: string
  examples: # Preferred (JSON Schema)
    - id: "usr_123"
      name: "John Doe"
    - id: "usr_456"
      name: "Jane Smith"
```

## Additional Properties

Control extra properties in objects:

```yaml
# Strict - no extra properties
type: object
additionalProperties: false

# Allow any extra properties
additionalProperties: true

# Type extra properties
additionalProperties:
  type: string

# Dictionary/map pattern
type: object
additionalProperties:
  $ref: '#/components/schemas/Value'
```

## Pattern Properties

Properties matching a regex pattern:

```yaml
type: object
patternProperties:
  "^x-": # Extension properties
    type: string
  "^[a-z]{2}$": # Language codes
    type: string
```

## Property Names

Constrain property name format:

```yaml
type: object
propertyNames:
  pattern: "^[a-z][a-zA-Z0-9]*$" # camelCase only
  maxLength: 50
```

## Conditional Schemas

```yaml
if:
  properties:
    type:
      const: admin
then:
  required: [adminLevel]
  properties:
    adminLevel:
      type: integer
      minimum: 1
      maximum: 5
else:
  properties:
    adminLevel: false # Disallow for non-admins
```

## XML Modeling

For XML serialization hints:

```yaml
Pet:
  type: object
  xml:
    name: pet # XML element name
    namespace: http://example.com/schema
    prefix: ex
  properties:
    id:
      type: integer
      xml:
        nodeType: attribute # As XML attribute
    tags:
      type: array
      xml:
        wrapped: true # Wrap in container element
        name: tags
      items:
        type: string
        xml:
          name: tag
```

## Schema References

```yaml
# Internal reference
$ref: '#/components/schemas/User'

# External file
$ref: './schemas/user.yaml'

# External with JSON pointer
$ref: './common.yaml#/components/schemas/Error'
```

**Important:** In Reference Objects, `$ref` cannot have sibling properties except `summary` and `description` which override the referenced values.

## Generic/Template Schemas (Advanced)

Using `$dynamicRef` for generics:

```yaml
GenericList:
  $id: generic-list
  type: array
  items:
    $dynamicRef: "#item"
  $defs:
    defaultItem:
      $dynamicAnchor: item

StringList:
  $id: string-list
  $ref: generic-list
  $defs:
    stringItem:
      $dynamicAnchor: item
      type: string
```
