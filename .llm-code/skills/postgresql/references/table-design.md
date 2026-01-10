# PostgreSQL Table Design

## Scope

Use this reference when designing or refactoring PostgreSQL tables: data types, constraints, indexes, partitioning, JSONB.

For RLS/multi-tenancy rules, see the main [SKILL.md](../SKILL.md).

## Core Rules

- Prefer `snake_case` identifiers. Avoid quoted/mixed-case.
- Define keys deliberately:
  - Multi-tenant: `bot_id` MUST be `UUID`
  - Surrogate keys: `BIGINT GENERATED ALWAYS AS IDENTITY`
- Normalize first (3NF). Denormalize only after measuring read bottlenecks.
- Use `NOT NULL` whenever domain requires it; use `DEFAULT` for common values.
- Create indexes for access paths you actually query.

## PostgreSQL Gotchas

- **FK indexes are not automatic**: PostgreSQL does not auto-index foreign keys. Add explicit indexes.
- **UNIQUE + NULL**: UNIQUE allows multiple NULLs. Use `UNIQUE (...) NULLS NOT DISTINCT` (PG15+) for single NULL.
- **Identity gaps are normal**: rollbacks and concurrency create gaps; don't try to "fix" them.
- **MVCC bloat**: updates/deletes leave dead tuples; vacuum handles them. Avoid wide hot-row churn.

## Data Types (Recommended Defaults)

| Use Case | Type | Notes |
|----------|------|-------|
| Time | `TIMESTAMPTZ` | Avoid `TIMESTAMP` without timezone |
| Money | `NUMERIC(p,s)` | Never float; avoid `money` |
| Strings | `TEXT` | Use `CHECK (length(col) <= n)` if max needed |
| External IDs | `UUID` | Bot-scoped / externally-visible |
| Internal PKs | `BIGINT GENERATED ALWAYS AS IDENTITY` | |
| JSON | `JSONB` | Prefer over `JSON` |

### Avoid

| Type | Why |
|------|-----|
| `serial` | Use identity |
| `timestamp` | Without timezone is ambiguous |
| `char(n)` / `varchar(n)` | Use `text` + `check` |
| `money` | Locale-dependent, imprecise |

## Constraints

### Primary Key

Implies `UNIQUE` + `NOT NULL`, creates B-tree index automatically.

### Foreign Key

Always specify `ON DELETE` / `ON UPDATE`:

```sql
REFERENCES parent(id) ON DELETE CASCADE
REFERENCES parent(id) ON DELETE SET NULL
REFERENCES parent(id) ON DELETE RESTRICT
```

**Add index on FK column** — PostgreSQL doesn't do this automatically.

### CHECK

NULL passes checks; combine with `NOT NULL` when needed:

```sql
status TEXT NOT NULL CHECK (status IN ('active', 'inactive'))
```

### UNIQUE

```sql
-- Standard (multiple NULLs allowed)
UNIQUE (email)

-- Single NULL only (PG15+)
UNIQUE NULLS NOT DISTINCT (email)
```

## Indexing Patterns

| Type | Use Case |
|------|----------|
| B-tree | Equality and range queries (default) |
| GIN | JSONB, arrays, full-text search |
| GiST | Ranges, exclusion constraints |
| BRIN | Huge, naturally ordered tables |

### Composite Indexes

Order matters; put most selective columns first:

```sql
CREATE INDEX ON orders (customer_id, created_at);
-- Supports: WHERE customer_id = ? AND created_at > ?
-- Supports: WHERE customer_id = ?
-- Does NOT support: WHERE created_at > ?
```

### Covering Indexes (INCLUDE)

Enable index-only scans:

```sql
CREATE INDEX ON orders (customer_id) INCLUDE (total, status);
```

### Partial Indexes

Hot subsets:

```sql
CREATE INDEX ON orders (created_at) WHERE status = 'pending';
```

### Expression Indexes

```sql
CREATE INDEX ON users (LOWER(email));
```

### Multi-tenant Indexing

For tenant-scoped queries, indexes typically start with `bot_id`:

```sql
CREATE INDEX ON messages (bot_id, created_at);
CREATE INDEX ON messages (bot_id, user_id);
```

## JSONB Guidance

GIN index for containment queries:

```sql
CREATE INDEX ON tbl USING GIN (attrs);

-- Query
SELECT * FROM tbl WHERE attrs @> '{"type": "premium"}';
```

Extract frequently queried scalar:

```sql
ALTER TABLE tbl
  ADD COLUMN theme TEXT GENERATED ALWAYS AS (attrs->>'theme') STORED;

CREATE INDEX ON tbl (theme);
```

## Partitioning

Use only for very large tables with consistent partition key filtering (often time).

```sql
CREATE TABLE events (
  id BIGINT GENERATED ALWAYS AS IDENTITY,
  created_at TIMESTAMPTZ NOT NULL,
  data JSONB
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2024_01 PARTITION OF events
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**Note**: Unique constraints must include partition key.

## Safe Schema Evolution

### Adding Columns

```sql
-- 1. Add nullable
ALTER TABLE tbl ADD COLUMN new_col TEXT;

-- 2. Backfill in batches
UPDATE tbl SET new_col = 'default' WHERE id BETWEEN 1 AND 10000;
-- Repeat...

-- 3. Add NOT NULL
ALTER TABLE tbl ALTER COLUMN new_col SET NOT NULL;
```

### Adding Indexes

```sql
-- Non-blocking (cannot run in transaction)
CREATE INDEX CONCURRENTLY ON tbl (col);
```

### Avoid on Large Tables

Volatile defaults that force table rewrites:

```sql
-- BAD: rewrites entire table
ALTER TABLE tbl ADD COLUMN created_at TIMESTAMPTZ DEFAULT now();

-- GOOD: add nullable, backfill, then add default
ALTER TABLE tbl ADD COLUMN created_at TIMESTAMPTZ;
UPDATE tbl SET created_at = now() WHERE created_at IS NULL;
ALTER TABLE tbl ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE tbl ALTER COLUMN created_at SET NOT NULL;
```

## Example: Tenant-Scoped Table

```sql
CREATE TABLE messages (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  bot_id UUID NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
  user_id BIGINT NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- FK index (manual)
CREATE INDEX ON messages (bot_id);

-- Access pattern indexes
CREATE INDEX ON messages (bot_id, user_id);
CREATE INDEX ON messages (bot_id, created_at);

-- Optional: JSONB if queried
CREATE INDEX ON messages USING GIN (metadata);
```

## See Also

- [Main PostgreSQL SKILL](../SKILL.md) — RLS, multi-tenancy, Alembic
- [authentication.md](authentication.md) — Auth methods
- [sql-expert skill](../../sql-expert/SKILL.md) — Query patterns, EXPLAIN
