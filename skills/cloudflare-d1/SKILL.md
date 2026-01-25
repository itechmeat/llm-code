# Cloudflare D1

Cloudflare D1 — managed serverless SQL database built on SQLite. Core: 10 GB per database, SQLite semantics, Time Travel (30 days), Workers/Pages integration.

## Quick Start

```bash
# Create database
npx wrangler d1 create my-database

# Execute SQL
npx wrangler d1 execute my-database --remote --command="SELECT 1"

# Apply schema
npx wrangler d1 execute my-database --remote --file=./schema.sql
```

## Binding (wrangler.jsonc)

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "<UUID>"
    }
  ]
}
```

TypeScript interface:

```typescript
export interface Env {
  DB: D1Database;
}
```

## Core API

### Prepared Statements (recommended)

```typescript
// Safe query with parameters
const { results } = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(userId).run();
```

### D1Database Methods

| Method                   | Purpose                                | Returns             |
| ------------------------ | -------------------------------------- | ------------------- |
| `prepare(sql)`           | Create prepared statement              | D1PreparedStatement |
| `batch([...stmts])`      | Execute multiple statements atomically | D1Result[]          |
| `exec(sql)`              | Execute raw SQL (no bind)              | D1ExecResult        |
| `withSession(bookmark?)` | Create session for read replication    | D1DatabaseSession   |

### D1PreparedStatement Methods

| Method                | Purpose                           |
| --------------------- | --------------------------------- |
| `bind(...values)`     | Bind parameters to ? placeholders |
| `run()`               | Execute (returns D1Result)        |
| `first(column?)`      | Get first row/field               |
| `all()`               | Get all rows                      |
| `raw({columnNames?})` | Get array of arrays               |

## D1Result Structure

```typescript
{
  success: boolean,
  meta: {
    served_by: string,
    served_by_region: string,    // WEUR, ENAM, APAC...
    served_by_primary: boolean,
    duration: number,            // ms
    changes: number,
    last_row_id: number,
    rows_read: number,
    rows_written: number
  },
  results: T[]
}
```

## Batch Operations

```typescript
// Atomic execution of multiple queries
const results = await env.DB.batch([env.DB.prepare("INSERT INTO users (name) VALUES (?)").bind("Alice"), env.DB.prepare("INSERT INTO users (name) VALUES (?)").bind("Bob"), env.DB.prepare("SELECT * FROM users")]);
// results[2].results contains SELECT data
```

**Important**: Batch executes atomically — if one query fails, all roll back.

## Read Replication (Sessions API)

```typescript
// Use sessions for read replication
const bookmark = request.headers.get("x-d1-bookmark") ?? "first-unconstrained";
const session = env.DB.withSession(bookmark);

const { results } = await session.prepare("SELECT * FROM users").run();

// Save bookmark for next request
response.headers.set("x-d1-bookmark", session.getBookmark() ?? "");
```

**Constraints**:

- `first-unconstrained` — any replica
- `first-primary` — primary only

## Migrations

```bash
# Create migration
npx wrangler d1 migrations create my-database create_users_table

# List migrations
npx wrangler d1 migrations list my-database --remote

# Apply migrations
npx wrangler d1 migrations apply my-database --remote
```

Files: `migrations/0001_create_users_table.sql`

Configuration in wrangler.jsonc:

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "<UUID>",
      "migrations_table": "d1_migrations",
      "migrations_dir": "migrations"
    }
  ]
}
```

## Time Travel (Point-in-Time Recovery)

```bash
# Get information about restore point
npx wrangler d1 time-travel info my-database --timestamp=1699900000

# Restore database
npx wrangler d1 time-travel restore my-database --timestamp=1699900000
```

- **Workers Paid**: 30 days history
- **Workers Free**: 7 days
- Restore overwrites database in place

## Import/Export

```bash
# Import SQL file
npx wrangler d1 execute my-database --remote --file=./data.sql

# Export full database
npx wrangler d1 export my-database --remote --output=./backup.sql

# Export single table
npx wrangler d1 export my-database --remote --table=users --output=./users.sql

# Schema only
npx wrangler d1 export my-database --remote --output=./schema.sql --no-data
```

## Local Development

```bash
# Local development (default)
npx wrangler dev

# Execute against local DB
npx wrangler d1 execute my-database --local --command="SELECT * FROM users"

# Work with remote DB in dev mode
# In wrangler.jsonc: "remote": true
```

## Workers Integration

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { pathname } = new URL(request.url);

    if (pathname === "/users") {
      const { results } = await env.DB.prepare("SELECT * FROM users LIMIT 10").run();
      return Response.json(results);
    }

    return new Response("Not Found", { status: 404 });
  },
};
```

## Pages Functions Integration

```typescript
// functions/api/users.ts
export async function onRequest(context) {
  const { results } = await context.env.DB.prepare("SELECT * FROM users").run();
  return Response.json(results);
}
```

Binding in Pages: Settings → Functions → D1 Database Bindings

## JSON Queries

```sql
-- Extract value from JSON
SELECT json_extract(data, '$.name') as name FROM users;

-- JSON array expansion
SELECT value FROM json_each('[1,2,3]');

-- Validate JSON
SELECT json_valid('{"key": "value"}');
```

## Generated Columns

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  data TEXT,
  name TEXT GENERATED ALWAYS AS (json_extract(data, '$.name')) STORED
);
```

## Foreign Keys

```sql
-- Enable foreign keys (at start of transaction)
PRAGMA foreign_keys = ON;

CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
```

## Indexes

```sql
-- Create index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Composite index
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);
```

**Rule**: Create indexes on columns used in WHERE, JOIN, ORDER BY.

## Wrangler Commands Reference

| Command                  | Description      |
| ------------------------ | ---------------- |
| `d1 create <name>`       | Create database  |
| `d1 delete <name>`       | Delete database  |
| `d1 list`                | List databases   |
| `d1 info <name>`         | Database info    |
| `d1 execute <name>`      | Execute SQL      |
| `d1 export <name>`       | Export database  |
| `d1 migrations create`   | Create migration |
| `d1 migrations list`     | List migrations  |
| `d1 migrations apply`    | Apply migrations |
| `d1 time-travel info`    | Time Travel info |
| `d1 time-travel restore` | Restore database |
| `d1 insights`            | Query metrics    |

**Flags**:

- `--local` — local DB (wrangler dev)
- `--remote` — production DB

## Limits

| Parameter               | Paid    | Free   |
| ----------------------- | ------- | ------ |
| Databases per account   | 50,000  | 10     |
| Max database size       | 10 GB   | 500 MB |
| Max storage per account | 1 TB    | 5 GB   |
| Time Travel             | 30 days | 7 days |
| Max row size            | 2 MB    | 2 MB   |
| Max SQL statement       | 100 KB  | 100 KB |
| Bound parameters        | 100     | 100    |
| Queries per invocation  | 1000    | 50     |

## Pricing (Workers Paid)

| Metric       | Included  | Overage     |
| ------------ | --------- | ----------- |
| Rows read    | 25B/month | $0.001/M    |
| Rows written | 50M/month | $1.00/M     |
| Storage      | 5 GB      | $0.75/GB-mo |

**Free plan**: 5M reads/day, 100K writes/day, 5 GB total.

## Environments

```jsonc
{
  "env": {
    "staging": {
      "d1_databases": [
        {
          "binding": "DB",
          "database_name": "staging-db",
          "database_id": "<STAGING_UUID>"
        }
      ]
    },
    "production": {
      "d1_databases": [
        {
          "binding": "DB",
          "database_name": "production-db",
          "database_id": "<PROD_UUID>"
        }
      ]
    }
  }
}
```

Deploy: `npx wrangler deploy --env production`

## Location Hints

```bash
npx wrangler d1 create my-database --location=weur
# weur/eeur - Europe, wnam/enam - North America, apac - Asia Pacific, oc - Oceania
```

## Jurisdictions (Data Locality)

```bash
npx wrangler d1 create eu-database --jurisdiction=eu
# eu - European Union, fedramp - FedRAMP compliance
```

**Important**: Jurisdiction cannot be changed after creation.

## Error Handling

```typescript
try {
  const result = await env.DB.prepare("SELECT * FROM nonexistent").run();
} catch (e) {
  // e.message contains D1_ERROR
  console.error("D1 Error:", e.message);
  // Example: "D1_ERROR: no such table: nonexistent"
}
```

## Testing with Miniflare

```typescript
import { Miniflare } from "miniflare";

const mf = new Miniflare({
  d1Databases: {
    DB: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  },
});

const db = await mf.getD1Database("DB");
const { results } = await db.prepare("SELECT 1").run();
```

## ORM Support

### Drizzle ORM

```typescript
import { drizzle } from "drizzle-orm/d1";

const db = drizzle(env.DB);
const users = await db.select().from(usersTable);
```

### Prisma ORM

```typescript
import { PrismaD1 } from "@prisma/adapter-d1";
import { PrismaClient } from "./generated/prisma";

const adapter = new PrismaD1(env.DB);
const prisma = new PrismaClient({ adapter });
```

## Prohibitions

1. **DO NOT** use `exec()` with user input — no parameterization
2. **DO NOT** rely on `--local` flag as default in wrangler 3.33+
3. **DO NOT** store `.sqlite3` files directly — use SQL dump only
4. **DO NOT** use alpha databases (deprecated)
5. **DO NOT** exceed 2 MB per row
6. **DO NOT** run long-running transactions

## References

- [references/binding.md](references/binding.md) — binding configuration
- [references/api.md](references/api.md) — full API reference
- [references/migrations.md](references/migrations.md) — migration system
- [references/time-travel.md](references/time-travel.md) — Point-in-Time Recovery
- [references/replication.md](references/replication.md) — Read Replication and Sessions API
- [references/pricing.md](references/pricing.md) — billing and limits

## Related Skills

- `cloudflare-workers` — D1 works through Workers bindings
- `cloudflare-pages` - Pages Functions support D1 bindings
- `cloudflare-r2` — Can export D1 to R2 via Workflows
