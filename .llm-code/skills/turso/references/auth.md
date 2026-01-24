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
import { createClient } from "@tursodatabase/serverless";

const db = createClient({
  url: "https://<db>.turso.io",
  authToken: await getAuthToken(), // JWT from auth provider
});

const result = await db.execute("SELECT * FROM users");
```

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
