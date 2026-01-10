# Operations and Paths

Defining API endpoints in OpenAPI.

## Path Item Object

Describes operations available on a single path.

```yaml
/users/{id}:
  $ref: "./paths/users.yaml" # Can reference external file
  summary: User operations
  description: Operations on user resource

  # Common parameters for all operations on this path
  parameters:
    - name: id
      in: path
      required: true
      schema:
        type: string

  # HTTP method operations
  get: {}
  put: {}
  post: {}
  delete: {}
  options: {}
  head: {}
  patch: {}
  trace: {}
  query: {} # IETF draft method

  # Additional/custom methods (OAS 3.2+)
  additionalOperations:
    COPY:
      summary: Copy resource
      responses:
        "200":
          description: Copied

  # Server override
  servers:
    - url: https://special.example.com
```

## Operation Object

Describes a single API operation.

```yaml
get:
  tags: [users]
  summary: Get user by ID # Short summary
  description: | # Long description (CommonMark)
    Returns a single user by their unique identifier.

    ## Usage Notes
    - Rate limited to 100 req/min

  externalDocs:
    url: https://docs.example.com/users

  operationId: getUserById # MUST be unique across API

  parameters:
    - name: include
      in: query
      description: Related resources to include
      schema:
        type: array
        items:
          type: string
          enum: [profile, settings]

  requestBody: # For methods with body
    $ref: "#/components/requestBodies/User"

  responses: # REQUIRED, at least one response
    "200":
      description: Success
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/User"
    "404":
      description: Not found
    default:
      description: Unexpected error

  callbacks:
    onUserUpdate:
      "{$request.body#/callbackUrl}":
        post:
          requestBody:
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/UserEvent"
          responses:
            "200":
              description: Callback received

  deprecated: false # Mark as deprecated

  security: # Override global security
    - bearerAuth: []
    - {} # Allow anonymous

  servers: # Override servers
    - url: https://special.example.com
```

### operationId Best Practices

```yaml
# Good - programming-friendly, unique, descriptive
operationId: getUserById
operationId: createUser
operationId: listUserOrders

# Bad - not unique, not descriptive
operationId: get
operationId: user
```

## Request Body Object

Describes the request payload.

```yaml
requestBody:
  description: User data to create
  required: true # Defaults to false
  content:
    application/json:
      schema:
        $ref: "#/components/schemas/UserCreate"
      examples:
        basic:
          summary: Basic user
          value:
            name: John Doe
            email: john@example.com

    application/xml:
      schema:
        $ref: "#/components/schemas/UserCreate"

    multipart/form-data: # For file uploads
      schema:
        type: object
        properties:
          file:
            type: string
            format: binary
          metadata:
            type: object
```

### Request Body Location Rules

| HTTP Method       | Request Body Support             |
| ----------------- | -------------------------------- |
| POST, PUT, PATCH  | Fully supported                  |
| GET, DELETE, HEAD | Discouraged (SHOULD avoid)       |
| OPTIONS, TRACE    | Not recommended                  |
| QUERY             | Explicitly supported (RFC draft) |

## Responses Object

Container for possible responses.

```yaml
responses:
  "200": # HTTP status code as string
    description: Success # REQUIRED

  "201":
    description: Created
    headers:
      Location:
        description: URL of created resource
        schema:
          type: string
          format: uri

  "4XX": # Range (400-499)
    description: Client error

  "5XX": # Range (500-599)
    description: Server error

  default: # Catch-all
    description: Unexpected error
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/Error"
```

### Response Status Codes

- Use specific codes when possible
- Ranges (`4XX`, `5XX`) for generic handling
- `default` for undeclared responses
- At least one response code REQUIRED
- Should include successful operation response

## Response Object

Single response definition.

```yaml
"200":
  summary: Successful response # Short summary
  description: Returns the user # REQUIRED

  headers:
    X-Rate-Limit-Remaining:
      description: Remaining requests
      schema:
        type: integer
    X-Rate-Limit-Reset:
      schema:
        type: integer
        format: unix-timestamp

  content:
    application/json:
      schema:
        $ref: "#/components/schemas/User"
      examples:
        admin:
          $ref: "#/components/examples/AdminUser"
        regular:
          value:
            id: "123"
            name: Regular User
            role: user

    text/plain:
      schema:
        type: string

  links:
    GetUserOrders:
      operationId: getUserOrders
      parameters:
        userId: $response.body#/id
      description: Get orders for this user
```

### Content Negotiation

- Key is media type or range (`text/*`, `*/*`)
- More specific types take precedence
- Empty content indicates no body

## Callback Object

Describes out-of-band callbacks.

```yaml
callbacks:
  paymentCallback:
    "{$request.body#/callbackUrl}":
      post:
        summary: Payment status callback
        requestBody:
          content:
            application/json:
              schema:
                type: object
                properties:
                  paymentId:
                    type: string
                  status:
                    type: string
                    enum: [completed, failed]
        responses:
          "200":
            description: Callback acknowledged
```

### Runtime Expressions

Used in callback URLs and link parameters:

| Expression                | Description                    |
| ------------------------- | ------------------------------ |
| `$url`                    | Full request URL               |
| `$method`                 | HTTP method                    |
| `$request.path.name`      | Path parameter value           |
| `$request.query.name`     | Query parameter value          |
| `$request.header.name`    | Request header value           |
| `$request.body#/pointer`  | Request body via JSON Pointer  |
| `$response.header.name`   | Response header value          |
| `$response.body#/pointer` | Response body via JSON Pointer |

## Link Object

Describes relationship between operations.

```yaml
responses:
  "200":
    description: User created
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/User"
    links:
      GetUserById:
        operationId: getUser # Reference by operationId
        parameters:
          userId: $response.body#/id # Map response to param
        description: Get the created user

      GetUserOrders:
        operationRef: "#/paths/~1users~1{userId}~1orders/get"
        parameters:
          userId: $response.body#/id
```

### Link Fields

| Field        | Description                               |
| ------------ | ----------------------------------------- |
| operationId  | Target operation by ID (recommended)      |
| operationRef | Target operation by URI reference         |
| parameters   | Map of parameter name to value/expression |
| requestBody  | Value/expression for request body         |
| description  | Description of the link                   |
| server       | Server object override                    |

## Deprecated Operations

```yaml
get:
  summary: Get user (deprecated)
  deprecated: true # Mark as deprecated
  description: |
    **Deprecated:** Use GET /v2/users/{id} instead.

    This endpoint will be removed in API v3.
  x-deprecated-since: "2024-01-01" # Custom extension
```
