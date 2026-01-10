# PostgreSQL OAuth 2.0 Authentication (PostgreSQL 18+)

> Consolidated from PostgreSQL documentation Chapters 20.15 (OAuth Authorization/Authentication) and 50 (OAuth Validator Modules).

OAuth 2.0 authentication allows PostgreSQL to delegate authentication to external identity providers (IdP).

## Requirements

- PostgreSQL 18+ (built with `--with-openssl --with-libcurl`)
- OAuth 2.0 / OpenID Connect identity provider
- Server-side validator module (must be implemented separately; PostgreSQL does not ship with any default implementations)
- Compatible client (libpq with OAUTHBEARER support)

---

## Core Concepts

### Terminology (from PostgreSQL 18 docs)

| Term | Description |
|------|-------------|
| **Resource Owner (End User)** | The user who owns protected resources and can grant access. When using psql to connect with OAuth, you are the resource owner/end user. |
| **Client** | Applications using libpq (like psql) that access protected resources using access tokens. |
| **Resource Server** | The PostgreSQL cluster being connected to. |
| **Provider** | The organization/vendor developing and administering OAuth authorization servers and clients. Different providers have different implementation details; clients of one provider are not generally compatible with servers of another. |
| **Authorization Server** | Issues access tokens to clients after the authenticated resource owner gives approval. PostgreSQL does **not** provide this; it's the OAuth provider's responsibility. |
| **Issuer** | An HTTPS URL identifying the authorization server, providing a trusted "namespace" for OAuth clients. Allows a single authorization server to talk to clients of mutually untrusting entities using separate issuers. |

**Note from docs**: For small deployments, there may not be a meaningful distinction between "provider", "authorization server", and "issuer". For more complicated setups, a provider may rent out multiple issuer identifiers to separate tenants, then provide multiple authorization servers, possibly with different supported feature sets.

### Bearer Tokens

PostgreSQL supports bearer tokens (RFC 6750). The format is implementation-specific and chosen by each authorization server.

---

## Server Configuration

### postgresql.conf

```text
# Load validator modules
oauth_validator_libraries = 'my_validator'
```

**Parameter Details** (`oauth_validator_libraries`):

- If only one validator library is provided, it will be used by default for any OAuth connections
- If multiple validators are configured, **all** `oauth` HBA entries must explicitly set a `validator`
- If set to empty string (the default), OAuth connections will be refused
- This parameter can only be set in `postgresql.conf`
- Validator modules must be implemented/obtained separately; PostgreSQL does not ship with any default implementations

### pg_hba.conf

```text
# TYPE   DATABASE  USER    ADDRESS      METHOD  OPTIONS
host     all       myuser  ::1/128      oauth   issuer=https://idp.example.com scope="openid profile" validator=my_validator

# With pg_ident.conf mapping
host     all       myuser  0.0.0.0/0    oauth   issuer=https://idp.example.com scope="openid" validator=my_validator map=oauth_map

# With delegated mapping (validator handles identity)
host     all       myuser  0.0.0.0/0    oauth   issuer=https://idp.example.com scope="openid" validator=my_validator delegate_ident_mapping=1
```

### OAuth HBA Options (from official docs)

| Option | Required | Description |
|--------|----------|-------------|
| `issuer` | **Yes** | HTTPS URL: either the **exact** issuer identifier from the authorization server's discovery document, or a well-known URI pointing directly to that document. |
| `scope` | **Yes** | Space-separated list of OAuth scopes needed to both authorize the client and authenticate the user. Appropriate values are determined by the authorization server and the OAuth validator module. |
| `validator` | Conditional | Must exactly match one of the libraries in `oauth_validator_libraries`. Required if multiple validators configured; optional otherwise. |
| `map` | No | Allows mapping between OAuth identity provider and database user names. See Section 20.2 for details. If not specified, user name from token must exactly match requested role. **Incompatible with `delegate_ident_mapping`.** |
| `delegate_ident_mapping` | No | **Advanced option, not for common use.** When `1`: standard user mapping with pg_ident.conf is skipped. Validator takes full responsibility for mapping end user identities to database roles. Connection proceeds if validator authorizes, regardless of authentication status. **Incompatible with `map`.** |

### Issuer Discovery URL Construction

From the docs:
- When a client connects, a URL for the discovery document is constructed using the issuer identifier
- By default: path `/.well-known/openid-configuration` is appended to the issuer identifier
- If issuer already contains a `/.well-known/` path segment, that URL is provided to the client as-is

**⚠️ Warning (from docs)**: The OAuth client in libpq requires the server's issuer setting to **exactly** match the issuer identifier which is provided in the discovery document, which must in turn match the client's `oauth_issuer` setting. **No variations in case or formatting are permitted.**

### pg_ident.conf (User Mapping)

```text
# MAPNAME    SYSTEM-USERNAME    PG-USERNAME
oauth_map   abcdef_user_id     myuser
oauth_map   /^(.*)@corp\.com$  \1
```

The `SYSTEM-USERNAME` comes from the validator's returned authenticated ID (`authn_id`).

---

## Validator Module (Chapter 50)

### Overview

PostgreSQL provides infrastructure for creating custom modules to perform server-side validation of OAuth bearer tokens. Because OAuth implementations vary widely, and bearer token validation is heavily dependent on the issuing party, **the server cannot check the token itself**; validator modules provide the integration layer between the server and the OAuth provider in use.

**⚠️ Warning (from docs)**: Since a misbehaving validator might let unauthorized users into the database, correct implementation is crucial for server safety.

### Validator Responsibilities (from Section 50.1.1)

Implementations generally need to perform three separate actions:

#### 1. Validate the Token

The validator must ensure that the presented token is a valid Bearer token for use in client authentication.

**Offline Validation**:
- Typically validate signature with IdP's public keys
- Must verify issuer, audience, validity period
- Follow provider's instructions exactly
- Cannot catch revoked tokens (use short TTL)
- Much faster than online validation

**Online Validation** (Token Introspection):
- Present token to provider's introspection endpoint
- Allows central revocation
- Requires network call per authentication (must complete within `authentication_timeout`)
- Provider may not provide introspection endpoints for external resource servers

If the token cannot be validated, the module should immediately fail.

#### 2. Authorize the Client

Ensure the end user has given the client permission to access the server on their behalf:
- Check scopes assigned to the token
- Scopes must cover database access for current HBA parameters

**Purpose** (from docs): Prevent OAuth client from obtaining token under false pretenses. If validator requires tokens to carry database access scopes, the provider should prompt the user to grant that access during the flow, giving them opportunity to reject if client shouldn't be using their credentials for database access.

Even if authorization fails, module may choose to continue to pull authentication information from the token for auditing and debugging.

#### 3. Authenticate the End User

Determine a user identifier for the token and return it to the server:
- Either ask provider for this information or extract from token
- Server makes final authorization decision using HBA configuration
- Identifier available via `system_user` and recorded in server logs if `log_connections` enabled

Different providers record different claims. Use claims that providers document as trustworthy for authorization (e.g., don't use changeable display names).

Anonymous/pseudonymous login is possible with `delegate_ident_mapping`.

### General Coding Guidelines (from Section 50.1.2)

#### Token Confidentiality

- Modules should **not** write tokens (or pieces of tokens) into the server log
- True even if module considers the token invalid (attacker confusion scenario)
- Network transmissions (e.g., introspection) must authenticate peer and ensure strong transport security

#### Logging

- Use standard extension logging facilities
- Rules for client log entries are different during authentication phase
- Log verification problems at `COMMERROR` level and return normally
- **Do not** use `ERROR`/`FATAL` to unwind the stack (avoids leaking info to unauthenticated clients)

#### Interruptibility

- Modules must remain interruptible by signals
- Server needs to handle authentication timeouts and shutdown signals from pg_ctl
- Use `WaitLatchOrSocket()`, `WaitEventSetWait()` instead of blocking socket calls
- Long-running loops should periodically call `CHECK_FOR_INTERRUPTS()`
- Failure may result in unresponsive backend sessions

#### Testing

Negative testing should be considered **mandatory**. It's trivial to design a module that lets authorized users in; the whole point is to keep unauthorized users out.

#### Documentation

Validator implementations should document:
- Contents and format of authenticated ID reported for each end user (email? org ID? UUID?)
- Whether safe to use in `delegate_ident_mapping=1` mode
- Additional configuration required for that mode

### Usermap Delegation (Section 50.1.3)

With `delegate_ident_mapping`, the validator bypasses username mapping entirely:
- Validator assumes responsibility for authorizing user connections
- May use token scopes or equivalent to decide if user can connect under desired role
- User identifier still recorded but doesn't determine connection authorization

**Anonymous Access**: As long as module reports authorized, login continues even without user identifier. This enables anonymous/pseudonymous access where provider authenticates but doesn't provide user-identifying info to server.

**⚠️ Warning (from docs)**: Usermap delegation provides most architectural flexibility, but turns the validator module into a single point of failure for connection authorization. Use with caution.

**Note on Device Authorization** (from docs): The Device Authorization client flow supported by libpq does not usually meet the "trusted client" bar, since it's designed for use by public/untrusted clients.

### Module Initialization (Section 50.2)

Validator modules are dynamically loaded from shared libraries listed in `oauth_validator_libraries`. Modules are loaded on demand when requested from a login in progress. Normal library search path is used.

```c
/* The module must provide this exported function */
typedef const OAuthValidatorCallbacks *(*OAuthValidatorModuleInit)(void);

/* Entry point name */
const OAuthValidatorCallbacks *_PG_oauth_validator_module_init(void);

/* Callbacks structure */
typedef struct OAuthValidatorCallbacks
{
    uint32  magic;  /* must be set to PG_OAUTH_VALIDATOR_MAGIC */

    ValidatorStartupCB  startup_cb;   /* optional */
    ValidatorShutdownCB shutdown_cb;  /* optional */
    ValidatorValidateCB validate_cb;  /* REQUIRED */
} OAuthValidatorCallbacks;
```

- Return value must be of server lifetime (typically `static const` variable in global scope)
- Only `validate_cb` is required; others are optional

### OAuth Validator Callbacks (Section 50.3)

#### Startup Callback (50.3.1)

```c
typedef void (*ValidatorStartupCB)(ValidatorModuleState *state);
```

- Executed immediately after module is loaded
- Used to initialize local state or perform additional setup
- Can store state in `state->private_data`

#### Validate Callback (50.3.2) — **REQUIRED**

```c
typedef bool (*ValidatorValidateCB)(
    const ValidatorModuleState *state,
    const char *token,      /* Bearer token to validate */
    const char *role,       /* Requested PostgreSQL role */
    ValidatorModuleResult *result
);

typedef struct ValidatorModuleResult {
    bool   authorized;   /* true = allow connection */
    char  *authn_id;     /* Authenticated user identifier (palloc'd) */
} ValidatorModuleResult;
```

- Called during OAuth exchange when user attempts to authenticate
- Connection proceeds only if `result->authorized` is set to `true`
- Module must ensure token carries sufficient permissions for user to log in under requested role

#### Shutdown Callback (50.3.3)

```c
typedef void (*ValidatorShutdownCB)(ValidatorModuleState *state);
```

- Executed when backend process associated with connection exits
- Responsible for freeing allocated state to prevent resource leaks

### Minimal Validator Example

```c
#include "postgres.h"
#include "libpq/oauth.h"

static void my_startup(ValidatorModuleState *state) {
    /* Initialize: load signing keys, set up caches, etc. */
    /* Can store data in state->private_data */
}

static bool my_validate(const ValidatorModuleState *state,
                        const char *token, const char *role,
                        ValidatorModuleResult *result) {
    /*
     * 1. Validate token (offline signature check or online introspection)
     * 2. Authorize client (check scopes cover database access)
     * 3. Authenticate end user (extract user identifier from token)
     * 4. Set result fields
     */
    
    result->authorized = true;  /* or false */
    result->authn_id = pstrdup("username_from_token");
    return true;  /* false = internal error */
}

static void my_shutdown(ValidatorModuleState *state) {
    /* Free any resources allocated during lifetime */
}

/* Module entry point — must return pointer with server lifetime */
const OAuthValidatorCallbacks *
_PG_oauth_validator_module_init(void) {
    static OAuthValidatorCallbacks callbacks = {
        .magic = PG_OAUTH_VALIDATOR_MAGIC,
        .startup_cb = my_startup,
        .validate_cb = my_validate,
        .shutdown_cb = my_shutdown
    };
    return &callbacks;
}
```

---

## Client Configuration

### Connection Parameters (from libpq docs)

| Parameter | Required | Description |
|-----------|----------|-------------|
| `oauth_issuer` | **Yes** | HTTPS URL of trusted issuer to contact if server requests OAuth token. Must **exactly** match server's `issuer` setting. |
| `oauth_client_id` | **Yes** | OAuth 2.0 client identifier issued by authorization server. Required if server requests OAuth token and no custom hook installed. |
| `oauth_client_secret` | Conditional | Client password for contacting authorization server. Required for "confidential" clients; "public" clients generally don't use one. Provider-dependent. |
| `oauth_scope` | No | Space-separated scope list. **Advanced**: If set, server-requested scope list is ignored. If client scopes don't include server-required scopes, connection will fail. Empty list behavior is provider-dependent. |

### Security Warning (from docs)

> Issuers are highly privileged during the OAuth connection handshake. As a rule of thumb, if you would not trust the operator of a URL to handle access to your servers, or to impersonate you directly, that URL should not be trusted as an `oauth_issuer`.

### Well-Known Endpoints Supported

libpq supports setting `oauth_issuer` to these well-known URIs directly:
- `/.well-known/openid-configuration`
- `/.well-known/oauth-authorization-server`

In this case, if server asks for different URL, connection fails, but custom OAuth flow may speed up handshake using cached tokens. (Recommended to also set `oauth_scope` since client won't ask server for correct scope.)

### Discovery Document Validation

From docs: As part of standard authentication handshake, libpq asks server for discovery document URL. Server must provide URL directly constructed from `oauth_issuer` components, and this value must **exactly** match issuer identifier in discovery document itself, or connection fails. This prevents "mix-up attacks" on OAuth clients.

### psql / libpq

Connection string:

```bash
psql "postgres://myuser@host:5432/mydb?oauth_issuer=https://idp.example.com&oauth_client_id=my-app"
```

With client secret (confidential client):

```bash
psql "dbname=mydb oauth_issuer=https://idp.example.com oauth_client_id=my-app oauth_client_secret=secret"
```

### Device Authorization Flow

libpq implements RFC 8628 Device Authorization Grant by default (requires `--with-libcurl` build):

```bash
$ psql "dbname=postgres oauth_issuer=https://example.com oauth_client_id=..."
Visit https://example.com/device and enter the code: ABCD-EFGH
```

**Flow**:
1. libpq requests device code from IdP
2. Displays `verification_uri` and `user_code`
3. User visits URL in browser, enters code, authenticates
4. libpq polls token endpoint until authorization complete
5. Sends bearer token to PostgreSQL

**⚠️ Note**: Built-in Device Authorization flow is not supported on Windows. Use custom OAuth hooks instead.

### Custom OAuth Hooks (libpq C API)

For custom token acquisition (e.g., browser-based flows, cached tokens):

```c
/* Hook callback signature */
int hook_fn(PGauthData type, PGconn *conn, void *data);

/* Set custom hook */
void PQsetAuthDataHook(PQauthDataHook_type hook);

/* Get current hook */
PQauthDataHook_type PQgetAuthDataHook(void);
```

#### Hook Types

| Type | Data | Purpose |
|------|------|---------|
| `PQAUTHDATA_OAUTH_BEARER_TOKEN` | `PGoauthBearerRequest*` | Custom token acquisition |
| `PQAUTHDATA_PROMPT_OAUTH_DEVICE` | `PGpromptOAuthDevice*` | Custom device flow prompt |

#### Token Request Structure

```c
typedef struct PGoauthBearerRequest {
    /* Inputs (read-only) */
    const char *openid_configuration;  /* OIDC discovery URL */
    const char *scope;                 /* Required scope(s) */
    
    /* Outputs */
    PostgresPollingStatusType (*async)(PGconn *conn,
                                       struct PGoauthBearerRequest *request,
                                       SOCKTYPE *altsock);
    void (*cleanup)(PGconn *conn, struct PGoauthBearerRequest *request);
    
    char *token;   /* Set this to acquired bearer token */
    void *user;    /* Hook-defined data */
} PGoauthBearerRequest;
```

#### Device Prompt Structure

```c
typedef struct PGpromptOAuthDevice {
    const char *verification_uri;           /* URL to visit */
    const char *user_code;                  /* Code to enter */
    const char *verification_uri_complete;  /* Combined URI+code (for QR) */
    int         expires_in;                 /* Seconds until code expires */
} PGpromptOAuthDevice;
```

#### Custom Hook Example

```c
static int my_oauth_hook(PGauthData type, PGconn *conn, void *data) {
    if (type == PQAUTHDATA_OAUTH_BEARER_TOKEN) {
        PGoauthBearerRequest *req = (PGoauthBearerRequest *)data;
        
        /* Return cached/pre-obtained token */
        req->token = strdup(getenv("OAUTH_TOKEN"));
        return 1;  /* Success */
    }
    return 0;  /* Use default handler */
}

/* Install hook before connecting */
PQsetAuthDataHook(my_oauth_hook);
conn = PQconnectdb("dbname=mydb oauth_issuer=...");
```

---

## SASL OAUTHBEARER Protocol

### Message Flow

```text
Client                              Server
  |                                    |
  |<---- AuthenticationSASL -----------|  "OAUTHBEARER" mechanism offered
  |                                    |
  |----- SASLInitialResponse --------->|  Token or discovery request
  |                                    |
  |<---- AuthenticationSASLContinue ---|  Discovery info (if requested)
  |                                    |
  |----- SASLResponse ---------------->|  Bearer token
  |                                    |
  |<---- AuthenticationSASLFinal ------|  Success outcome
  |<---- AuthenticationOk -------------|
```

### Initial Response Formats (RFC 7628)

**Discovery request** (empty kvpairs):

```text
n,,\x01\x01
```

**Token submission**:

```text
n,,\x01auth=Bearer <token>\x01\x01
```

Where:
- `n,,` — No channel binding, no authorization identity
- `\x01` — Key-value pair separator
- `auth=Bearer <token>` — The bearer token

---

## Common IdP Configurations

### Keycloak

```text
# pg_hba.conf
host all all 0.0.0.0/0 oauth \
  issuer=https://keycloak.example.com/realms/myrealm \
  scope="openid profile" \
  validator=jwt_validator
```

### Azure AD / Entra ID

```text
host all all 0.0.0.0/0 oauth \
  issuer=https://login.microsoftonline.com/<tenant-id>/v2.0 \
  scope="api://<app-id>/.default" \
  validator=azure_validator
```

### Auth0

```text
host all all 0.0.0.0/0 oauth \
  issuer=https://<tenant>.auth0.com/ \
  scope="openid profile" \
  validator=auth0_validator
```

### Google

```text
host all all 0.0.0.0/0 oauth \
  issuer=https://accounts.google.com \
  scope="openid email" \
  validator=google_validator
```

### Okta

```text
host all all 0.0.0.0/0 oauth \
  issuer=https://<domain>.okta.com \
  scope="openid profile" \
  validator=okta_validator
```

---

## Best Practices

### Security

- [ ] Use HTTPS for issuer URL
- [ ] Validate token scopes in validator
- [ ] Set appropriate `authentication_timeout`
- [ ] Use `delegate_ident_mapping` only with trusted, carefully-implemented validators
- [ ] Require SSL (`hostssl`) for OAuth connections
- [ ] Never log tokens or token fragments (even for invalid tokens)
- [ ] Use strong transport security for introspection calls

### Token Management

- [ ] For offline validation: use short token TTL (5-15 min) since revocation cannot be checked
- [ ] For online validation: ensure network calls complete within `authentication_timeout`
- [ ] Implement token refresh in connection pools
- [ ] Handle `AuthenticationSASLContinue` for re-auth

### Validator Implementation

- [ ] Implement comprehensive negative testing
- [ ] Document authenticated ID format (email? UUID? org ID?)
- [ ] Document `delegate_ident_mapping` safety and requirements
- [ ] Use `COMMERROR` level for validation problems, not `ERROR`/`FATAL`
- [ ] Ensure interruptibility (`CHECK_FOR_INTERRUPTS()`, non-blocking I/O)

---

## Troubleshooting

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `issuer mismatch` | Server/client/discovery issuer URLs differ | Ensure **exact** match (case-sensitive, no trailing slash variations) |
| `validator not found` | Module not in `oauth_validator_libraries` | Add to postgresql.conf |
| `token expired` | Token lifetime exceeded | Implement refresh logic; use shorter TTL |
| `SCRAM selected` | OAuth not configured for connection | Check pg_hba.conf rules order |
| Unresponsive backend | Validator not handling interrupts | Use non-blocking I/O, call `CHECK_FOR_INTERRUPTS()` |

### Debug

```bash
# libpq debug (WARNING: logs sensitive data)
PGOAUTHDEBUG=UNSAFE psql "..."

# Server logs
log_connections = on
```

---

## See Also

- [authentication.md](authentication.md) — General authentication methods (pg_hba.conf)
- [user-management.md](user-management.md) — Role management after authentication
- [protocol.md](protocol.md) — SASL authentication protocol details

### RFCs

- [RFC 6749 - OAuth 2.0](https://tools.ietf.org/html/rfc6749)
- [RFC 6750 - Bearer Tokens](https://tools.ietf.org/html/rfc6750)
- [RFC 7628 - SASL OAUTHBEARER](https://tools.ietf.org/html/rfc7628)
- [RFC 8628 - Device Authorization Grant](https://tools.ietf.org/html/rfc8628)

### PostgreSQL Documentation

- [Chapter 20.15: OAuth Authorization/Authentication](https://www.postgresql.org/docs/current/auth-oauth.html)
- [Chapter 50: OAuth Validator Modules](https://www.postgresql.org/docs/current/oauth-validators.html)
- [libpq Connection Parameters](https://www.postgresql.org/docs/current/libpq-connect.html)
