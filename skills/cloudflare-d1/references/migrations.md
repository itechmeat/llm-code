# D1 Migrations

## Concept

Migrations are SQL files with versioned schema changes. Stored in `migrations/` folder, applied sequentially.

## Workflow

### 1. Create migration

```bash
npx wrangler d1 migrations create my-database create_users_table
```

Creates file: `migrations/0001_create_users_table.sql`

### 2. Write migration

```sql
-- migrations/0001_create_users_table.sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  name TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_users_email ON users(email);
```

### 3. Check status

```bash
# Local DB
npx wrangler d1 migrations list my-database --local

# Production DB
npx wrangler d1 migrations list my-database --remote
```

### 4. Apply migrations

```bash
# Locally (for development)
npx wrangler d1 migrations apply my-database --local

# Production
npx wrangler d1 migrations apply my-database --remote
```

---

## Configuration

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "<UUID>",
      "migrations_table": "d1_migrations", // default
      "migrations_dir": "migrations" // default
    }
  ]
}
```

## Migrations Table Structure

D1 creates `d1_migrations` table automatically:

```sql
CREATE TABLE d1_migrations (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  applied_at TEXT NOT NULL
);
```

---

## Migration Examples

### Add column

```sql
-- 0002_add_status_to_users.sql
ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active';
```

### Create related tables

```sql
-- 0003_create_orders.sql
CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  total REAL NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### Create index

```sql
-- 0004_add_orders_date_index.sql
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

### Drop table (with check)

```sql
-- 0005_drop_legacy_table.sql
DROP TABLE IF EXISTS legacy_data;
```

---

## Best Practices

### Idempotency

Use `IF NOT EXISTS` / `IF EXISTS`:

```sql
CREATE TABLE IF NOT EXISTS users (...);
DROP INDEX IF EXISTS old_index;
```

### Atomicity

Each migration — one logical operation. Split complex changes into multiple files.

### Naming

```
NNNN_<descriptive_action>.sql

0001_create_users_table.sql
0002_add_email_index.sql
0003_create_orders_table.sql
```

### Never modify applied migrations

After migration is applied to production — **never edit it**. Create new migration instead.

---

## Rollback

D1 does not support automatic rollback. Options:

### 1. Time Travel (recommended)

```bash
# Restore DB to before migration
npx wrangler d1 time-travel restore my-database --timestamp=<before_migration>
```

### 2. Manual rollback migration

```sql
-- 0006_rollback_status_column.sql
ALTER TABLE users DROP COLUMN status;
```

**Note**: SQLite does not support `DROP COLUMN` before version 3.35.0. D1 supports it.

---

## CI/CD Integration

```yaml
# .github/workflows/deploy.yml
- name: Apply migrations
  run: npx wrangler d1 migrations apply my-database --remote
  env:
    CLOUDFLARE_API_TOKEN: ${{ secrets.CF_API_TOKEN }}

- name: Deploy Worker
  run: npx wrangler deploy
```

**Order**: Migrations first, then deploy Worker.

---

## Seed Data

For initial data, create separate file (not a migration):

```sql
-- seed.sql
INSERT INTO users (email, name) VALUES
  ('admin@example.com', 'Admin'),
  ('test@example.com', 'Test User');
```

```bash
npx wrangler d1 execute my-database --remote --file=./seed.sql
```
