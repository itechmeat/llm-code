# D1 Binding Configuration

## wrangler.jsonc

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2024-01-01",
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  ]
}
```

## wrangler.toml (alternative)

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

## Configuration Fields

| Field                 | Required | Description                                            |
| --------------------- | -------- | ------------------------------------------------------ |
| `binding`             | Yes      | Variable name in `env` (e.g., `env.DB`)                |
| `database_name`       | Yes      | Database name in Cloudflare                            |
| `database_id`         | Yes      | Database UUID (from `wrangler d1 create` or Dashboard) |
| `preview_database_id` | No       | UUID for preview/local deployments                     |
| `migrations_table`    | No       | Migrations table name (default: `d1_migrations`)       |
| `migrations_dir`      | No       | Migrations folder (default: `migrations`)              |

## TypeScript Interface

```typescript
export interface Env {
  DB: D1Database;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // env.DB is available
    const result = await env.DB.prepare("SELECT 1").run();
    return Response.json(result);
  },
};
```

## Get database_id

```bash
# During creation
npx wrangler d1 create my-database
# Output contains database_id

# For existing database
npx wrangler d1 info my-database
# or
npx wrangler d1 list
```

## Multiple Databases

```jsonc
{
  "d1_databases": [
    {
      "binding": "USERS_DB",
      "database_name": "users-database",
      "database_id": "xxx-xxx"
    },
    {
      "binding": "ORDERS_DB",
      "database_name": "orders-database",
      "database_id": "yyy-yyy"
    }
  ]
}
```

## Preview Database (for Pages/local)

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "production-uuid",
      "preview_database_id": "preview-uuid"
    }
  ]
}
```

`preview_database_id` is used during:

- `wrangler pages dev`
- `wrangler dev` without `--remote`

## Remote Binding (for local development with prod data)

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "xxx",
      "remote": true
    }
  ]
}
```

**Caution**: `remote: true` works with production data in dev mode.

## Pages Functions Binding

In Cloudflare Dashboard:

1. Workers & Pages → Your Project
2. Settings → Functions
3. D1 database bindings → Add binding

Or via `wrangler pages dev`:

```bash
wrangler pages dev --d1 DB=database-uuid
```
