# D1 Pricing & Limits

## Pricing Plans

### Workers Free

| Metric            | Limit           |
| ----------------- | --------------- |
| Rows read         | 5 million / day |
| Rows written      | 100,000 / day   |
| Storage           | 5 GB total      |
| Databases         | 10              |
| Max database size | 500 MB          |
| Time Travel       | 7 days          |

### Workers Paid ($5/month base)

| Metric       | Included           | Overage          |
| ------------ | ------------------ | ---------------- |
| Rows read    | 25 billion / month | $0.001 / million |
| Rows written | 50 million / month | $1.00 / million  |
| Storage      | 5 GB               | $0.75 / GB-month |

| Limit             | Value   |
| ----------------- | ------- |
| Databases         | 50,000  |
| Max database size | 10 GB   |
| Time Travel       | 30 days |

---

## Billing Metrics

### Rows Read

- Number of rows scanned by query
- **Not** number of returned rows
- `SELECT * FROM users WHERE id = 1` without index reads ENTIRE table

### Rows Written

- Number of rows modified by query
- INSERT, UPDATE, DELETE

### How to check rows read/written

```typescript
const { results, meta } = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(1).run();

console.log({
  rowsRead: meta.rows_read,
  rowsWritten: meta.rows_written,
});
```

### Optimization

```sql
-- Bad: full table scan
SELECT * FROM users WHERE email = 'test@example.com';
-- rows_read = all rows in table

-- Good: index
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'test@example.com';
-- rows_read = 1 (or however many found)
```

---

## Limits Reference

| Parameter                     | Value                   |
| ----------------------------- | ----------------------- |
| Max row size                  | 2 MB                    |
| Max SQL statement             | 100 KB                  |
| Max bound parameters          | 100                     |
| Max columns per table         | 100                     |
| Max rows per table            | Unlimited\*             |
| Queries per Worker invocation | 1000 (Paid) / 50 (Free) |
| Max bindings per Worker       | ~5,000 databases        |

\*Limited by database size (10 GB / 500 MB)

---

## What Is Billed

| Operation                  | Rows Read  | Rows Written |
| -------------------------- | ---------- | ------------ |
| SELECT without WHERE       | All rows   | 0            |
| SELECT with index          | Found rows | 0            |
| INSERT                     | 0          | Inserted     |
| UPDATE                     | Scanned    | Updated      |
| DELETE                     | Scanned    | Deleted      |
| CREATE TABLE               | 0          | 0            |
| CREATE INDEX               | All rows   | All rows     |
| Wrangler/Dashboard queries | Yes        | Yes          |

---

## Storage Calculation

- Storage measured by `.sqlite` file size
- Includes data, indexes, free space
- `_cf_KV` system table is not billed

Get size:

```bash
npx wrangler d1 info my-database
```

```
size: 45.2 MB
```

---

## Cost Estimation

### Example: 10M reads/month, 100K writes/month

**Free plan**: Within limits ✓

**Paid plan** (if Free exceeded):

- Rows read: 10M < 25B included = $0
- Rows written: 100K < 50M included = $0
- Storage: 1 GB < 5 GB included = $0
- **Total**: $5/month (base Workers Paid)

### Example: 50B reads/month, 100M writes/month, 20 GB storage

- Rows read: (50B - 25B) × $0.001/M = $25,000
- Rows written: (100M - 50M) × $1.00/M = $50
- Storage: (20 - 5) GB × $0.75 = $11.25
- **Total**: $5 + $25,061.25 = $25,066.25/month

---

## Cost Optimization Tips

### 1. Use indexes

```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
-- Reduces rows_read from N to ~1
```

### 2. LIMIT in queries

```sql
SELECT * FROM logs ORDER BY created_at DESC LIMIT 100;
-- Instead of SELECT * FROM logs
```

### 3. Select needed columns

```sql
SELECT id, name FROM users WHERE ...
-- Instead of SELECT * — less I/O
```

### 4. Batch operations

```typescript
// One batch instead of many separate queries
await env.DB.batch([...items.map((item) => env.DB.prepare("INSERT INTO items (name) VALUES (?)").bind(item.name))]);
```

---

## Billing Notifications

In Cloudflare Dashboard:

1. Account Home → Notifications
2. Add notification → Workers & Pages
3. Select D1 usage alerts

---

## Free Plan Limits Exceeded

When daily limits are exceeded on Free plan:

- D1 API returns errors
- Reset at midnight UTC
- Upgrade to Paid removes limits within minutes
