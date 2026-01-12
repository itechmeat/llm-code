# D1 Time Travel (Point-in-Time Recovery)

## Overview

Time Travel allows restoring database to any minute in the past:

- **Workers Paid**: up to 30 days
- **Workers Free**: up to 7 days

Works automatically — no configuration or additional costs required.

---

## Bookmarks

Bookmark — unique identifier of database state at specific moment in time.

### Get bookmark for timestamp

```bash
npx wrangler d1 time-travel info my-database --timestamp=1699900000
```

Output:

```
Bookmark: 00000080-ffffffff-00004c60-390376cb1c4dd679b74a19d19f5ca5be
```

### Timestamp formats

```bash
# Unix timestamp (seconds)
--timestamp=1699900000

# RFC3339
--timestamp=2023-11-13T15:30:00Z
```

---

## Restoration

### By timestamp

```bash
npx wrangler d1 time-travel restore my-database --timestamp=1699900000
```

### By bookmark

```bash
npx wrangler d1 time-travel restore my-database --bookmark=00000080-ffffffff-...
```

### Interactive confirmation

```
🚧 Restoring database my-database from bookmark 00000080-...

⚠️ This will overwrite all data in database my-database.
In-flight queries and transactions will be cancelled.

✔ OK to proceed (y/N) … yes
⚡️ Time travel in progress...
✅ Database my-database restored back to bookmark 00000080-...
```

**Warning**: Restoration overwrites database in place. All data after restore point is lost.

---

## Undo Restoration

If restored to wrong point — can return to state before restore:

```bash
# Get bookmark of current (before rollback) state
npx wrangler d1 time-travel info my-database --timestamp=<timestamp_before_restore>

# Restore to it
npx wrangler d1 time-travel restore my-database --bookmark=<that_bookmark>
```

---

## Use Cases

### 1. Rollback failed migration

```bash
# Before migration
BEFORE_TIMESTAMP=$(date +%s)

# Apply migration
npx wrangler d1 migrations apply my-database --remote

# If something went wrong
npx wrangler d1 time-travel restore my-database --timestamp=$BEFORE_TIMESTAMP
```

### 2. Recovery after DELETE without WHERE

```sql
-- Accidentally executed
DELETE FROM users;
```

```bash
# Restore to 5 minutes before incident
npx wrangler d1 time-travel restore my-database --timestamp=$(( $(date +%s) - 300 ))
```

### 3. Historical data analysis

For viewing without restoration — use Sessions API with bookmark:

```typescript
const session = env.DB.withSession("00000080-...");
const { results } = await session.prepare("SELECT * FROM users").run();
```

---

## Limits

| Parameter             | Value                          |
| --------------------- | ------------------------------ |
| Maximum history depth | 30 days (Paid) / 7 days (Free) |
| Restore operations    | 10 per 10 minutes per DB       |
| Granularity           | 1 minute                       |

---

## Billing

- Time Travel is **not billed separately**
- History storage is included in base price
- Restore operations are free

---

## Check Database Version

Time Travel works only with production storage subsystem:

```bash
npx wrangler d1 info my-database
```

```
version: production  # ✓ Time Travel available
# or
version: alpha       # ✗ Old version, migration needed
```

For alpha databases see [Alpha Migration Guide](https://developers.cloudflare.com/d1/platform/alpha-migration/).

---

## Automated Backup to R2

For storage longer than 30 days — export to R2:

```bash
# Export to SQL
npx wrangler d1 export my-database --remote --output=./backup-$(date +%Y%m%d).sql

# Upload to R2
npx wrangler r2 object put my-bucket/backups/backup-$(date +%Y%m%d).sql --file=./backup-$(date +%Y%m%d).sql
```

Or via Cloudflare Workflows for automation.

---

## CLI Quick Reference

```bash
# Get restore point info
npx wrangler d1 time-travel info <database> --timestamp=<ts>

# Restore
npx wrangler d1 time-travel restore <database> --timestamp=<ts>
npx wrangler d1 time-travel restore <database> --bookmark=<bookmark>

# JSON output (for scripts)
npx wrangler d1 time-travel info <database> --timestamp=<ts> --json
```
