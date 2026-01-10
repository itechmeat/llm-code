# Security Schemes

Defining API authentication and authorization in OpenAPI.

## Security Scheme Types

| Type          | Description                               |
| ------------- | ----------------------------------------- |
| apiKey        | API key in header, query, or cookie       |
| http          | HTTP authentication (Basic, Bearer, etc.) |
| oauth2        | OAuth 2.0 flows                           |
| openIdConnect | OpenID Connect Discovery                  |
| mutualTLS     | Mutual TLS (client certificate)           |

## API Key

```yaml
components:
  securitySchemes:
    # Header-based API key
    ApiKeyHeader:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key passed in header

    # Query parameter API key
    ApiKeyQuery:
      type: apiKey
      in: query
      name: api_key

    # Cookie-based API key
    ApiKeyCookie:
      type: apiKey
      in: cookie
      name: api_session
```

### Apply API Key

```yaml
security:
  - ApiKeyHeader: [] # Empty array (no scopes)
```

## HTTP Authentication

### Basic Authentication

```yaml
components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
      description: Base64 encoded username:password
```

### Bearer Token

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT # Hint only, not validated
      description: JWT access token
```

### Other HTTP Schemes

```yaml
components:
  securitySchemes:
    DigestAuth:
      type: http
      scheme: digest

    HobaAuth:
      type: http
      scheme: hoba
```

Valid schemes from IANA registry: basic, bearer, digest, hoba, mutual, negotiate, oauth, scram-sha-1, scram-sha-256, vapid.

## OAuth 2.0

### Authorization Code Flow (Recommended)

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      description: OAuth 2.0 Authorization Code with PKCE
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          refreshUrl: https://auth.example.com/refresh # Optional
          scopes:
            read:users: Read user information
            write:users: Modify user information
            admin: Full administrative access
```

### Client Credentials Flow

For machine-to-machine authentication:

```yaml
components:
  securitySchemes:
    OAuth2ClientCreds:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://auth.example.com/token
          scopes:
            api:read: Read API data
            api:write: Write API data
```

### Implicit Flow (Deprecated)

**Warning:** Implicit flow is deprecated for security reasons.

```yaml
components:
  securitySchemes:
    OAuth2Implicit:
      type: oauth2
      flows:
        implicit:
          authorizationUrl: https://auth.example.com/authorize
          scopes:
            read: Read access
```

### Password Flow

```yaml
components:
  securitySchemes:
    OAuth2Password:
      type: oauth2
      flows:
        password:
          tokenUrl: https://auth.example.com/token
          scopes:
            read: Read access
            write: Write access
```

### Device Authorization Flow (OAS 3.2+)

```yaml
components:
  securitySchemes:
    OAuth2Device:
      type: oauth2
      flows:
        deviceAuthorization:
          deviceAuthorizationUrl: https://auth.example.com/device
          tokenUrl: https://auth.example.com/token
          scopes:
            read: Read access
```

### Multiple Flows

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes:
            read: Read access
            write: Write access
        clientCredentials:
          tokenUrl: https://auth.example.com/token
          scopes:
            api:admin: Administrative access
```

### OAuth2 Metadata URL (OAS 3.2+)

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      oauth2MetadataUrl: https://auth.example.com/.well-known/oauth-authorization-server
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes:
            read: Read access
```

## OpenID Connect

```yaml
components:
  securitySchemes:
    OpenIdConnect:
      type: openIdConnect
      openIdConnectUrl: https://auth.example.com/.well-known/openid-configuration
      description: OpenID Connect authentication
```

The discovery URL provides authorization, token URLs, and supported scopes.

## Mutual TLS

```yaml
components:
  securitySchemes:
    MutualTLS:
      type: mutualTLS
      description: Client certificate required
```

No additional configuration - relies on TLS handshake.

## Applying Security

### Global Security

Apply to all operations:

```yaml
security:
  - BearerAuth: []
```

### Per-Operation Security

```yaml
paths:
  /public/info:
    get:
      security: [] # No authentication required
      responses:
        "200":
          description: Public information

  /users/me:
    get:
      security:
        - BearerAuth: [] # Bearer token required
      responses:
        "200":
          description: Current user
```

### Multiple Options (OR)

Any one scheme satisfies the requirement:

```yaml
security:
  - ApiKeyHeader: []
  - BearerAuth: []
  - OAuth2: [read]
```

### Combined Requirements (AND)

All schemes must be satisfied:

```yaml
security:
  - ApiKeyHeader: []
    BearerAuth: [] # Both required
```

### OAuth2 Scopes

```yaml
security:
  - OAuth2:
      - read:users
      - write:users
```

### Optional Authentication

Include empty object for anonymous access:

```yaml
security:
  - {} # Anonymous allowed
  - BearerAuth: [] # Or authenticated
```

## Security Requirement Object

```yaml
# Format: {scheme_name}: [scope1, scope2, ...]

security:
  # No scopes (apiKey, http, mutualTLS)
  - ApiKey: []

  # With scopes (oauth2, openIdConnect)
  - OAuth2:
      - read
      - write

  # Combined requirements
  - ApiKey: []
    OAuth2:
      - admin
```

## Deprecated Security Schemes

```yaml
components:
  securitySchemes:
    LegacyApiKey:
      type: apiKey
      in: header
      name: X-Legacy-Key
      deprecated: true
      description: |
        **Deprecated:** Use BearerAuth instead.
        Will be removed in API v3.
```

## Common Patterns

### API Key + OAuth2 Fallback

```yaml
security:
  - ApiKey: []
  - OAuth2:
      - read

paths:
  /admin:
    get:
      security:
        - OAuth2:
            - admin # Override: only OAuth2 admin
```

### Webhook Authentication

```yaml
webhooks:
  orderStatus:
    post:
      security:
        - WebhookSignature: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/OrderStatus"

components:
  securitySchemes:
    WebhookSignature:
      type: apiKey
      in: header
      name: X-Webhook-Signature
      description: HMAC-SHA256 signature of request body
```

### Multi-Tenant API

```yaml
security:
  - BearerAuth: []
    TenantId: [] # Tenant + Auth both required

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
    TenantId:
      type: apiKey
      in: header
      name: X-Tenant-ID
```

## Security Best Practices

### DO

- Use Authorization Code + PKCE for web/mobile apps
- Use Client Credentials for machine-to-machine
- Define clear, granular scopes
- Mark deprecated schemes with `deprecated: true`
- Document security requirements clearly

### DON'T

- Use Implicit flow (deprecated, insecure)
- Use Password flow for third-party apps
- Send API keys in query strings (appears in logs)
- Use Basic auth without HTTPS
- Rely on client-side security alone

## Security Considerations

### Documenting Sensitive Endpoints

```yaml
paths:
  /admin/users:
    get:
      security:
        - OAuth2:
            - admin:users
      tags: [admin]
      x-internal: true # Custom extension for internal APIs
```

### Rate Limiting Documentation

```yaml
paths:
  /api/data:
    get:
      responses:
        "429":
          description: Rate limit exceeded
          headers:
            X-RateLimit-Limit:
              schema:
                type: integer
            X-RateLimit-Remaining:
              schema:
                type: integer
            X-RateLimit-Reset:
              schema:
                type: integer
                format: unix-timestamp
```

### Security Filtering

API providers may hide endpoints based on authentication:

- Paths Object MAY be empty (access denied to all)
- Path Item Object MAY be empty (path visible, no operations)
- Undocumented security may exist beyond what's in the spec
