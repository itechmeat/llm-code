# Authorization

JWT-based authorization via JWKS or Turso CLI tokens.

## Token Types

1. **JWKS tokens** — from your auth provider (Clerk, Auth0)
2. **Database tokens** — created via CLI
3. **Group tokens** — access to multiple databases

## JWKS Setup

### 1. Generate JWT Template

```bash
# Full access to database
turso org jwks template --database <db> --scope full-access

# Read-only access to group
turso org jwks template --group <group> --scope read-only

# Fine-grained permissions
turso org jwks template \
  --database <db> \
  --permissions all:data_read \
  --permissions comments:data_add \
  --permissions posts:data_add,data_update
```

### Permission Actions

| Action        | Description           |
| ------------- | --------------------- |
| data_read     | Read data from tables |
| data_add      | Insert new data       |
| data_update   | Update existing data  |
| data_delete   | Delete data           |
| schema_add    | Create tables         |
| schema_update | Modify schemas        |
| schema_delete | Drop tables           |

### 2. Add JWKS Endpoint

```bash
turso org jwks save clerk https://your-app.clerk.accounts.dev/.well-known/jwks.json
```

### 3. Use in Application

```javascript
import { createClient } from "@tursodatabase/serverless/compat";

const db = createClient({
  url: "https://<db>.turso.io",
  authToken: await getAuthToken(), // JWT from auth provider
});

const result = await db.execute("SELECT * FROM users");
```

**Note:** `execute()` lives on the `/compat` libsql-compatibility layer shown above. It does not exist on the driver's native-mirroring surface (`connect()` from `@tursodatabase/serverless`), which was aligned with `@tursodatabase/database` and now only exposes `run`/`get`/`all`/`iterate`/`exec`/`batch`/`transaction(Async)` — `Connection.execute()` was removed from that surface. If your code called `connect()` directly and used `.execute()`, switch to `run`/`get`/`all` or move to the `/compat` `createClient()` shown here.

### Custom Request Headers

Per-query headers can be attached without a new client instance, via the trailing query-options argument (accepted by `run`/`get`/`all`/`iterate` on the native `connect()` surface):

```javascript
import { connect } from "@tursodatabase/serverless";

const conn = connect({
  url: "https://<db>.turso.io",
  authToken: await getAuthToken(),
});

await conn.all("SELECT * FROM users", {
  requestHeaders: { "X-Turso-Request-Identity": requestId },
});
```

Per-query headers merge over any connection-level `requestHeaders` and apply only to that call's HTTP request(s). To stamp every request in a transaction, including `BEGIN`/`COMMIT`, set the header at the connection level or use an atomic `batch()` call, which sends the whole transaction as one HTTP request.

## CLI Token Management

```bash
# Create database token
turso db tokens create <db>

# List JWKS endpoints
turso org jwks list

# Remove JWKS endpoint
turso org jwks remove <name>
```

## Notes

- During Beta: only Clerk & Auth0 supported as OIDC providers
- Without JWT template: tokens have access to **all databases in all groups**
- `data_read` allowed on SQLite system tables by default
