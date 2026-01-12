# Durable Objects Storage API

## Storage Backends

| Backend | Configuration                      | Features               |
| ------- | ---------------------------------- | ---------------------- |
| SQLite  | `new_sqlite_classes` in migrations | SQL API, sync KV, PITR |
| KV      | `new_classes` in migrations        | Async KV only          |

**Recommendation**: Use SQLite for new Durable Objects.

---

## SQLite Storage API

### SQL API (`ctx.storage.sql`)

```typescript
// Execute query
const cursor = this.ctx.storage.sql.exec("SELECT * FROM users WHERE status = ?", "active");

// Get results
const rows = cursor.toArray(); // All rows as array
const row = cursor.one(); // Exactly one row (throws otherwise)
const raw = cursor.raw(); // Raw values without column names

// Iterate
for (const row of cursor) {
  console.log(row.id, row.name);
}

// Cursor properties
cursor.columnNames; // string[]
cursor.rowsRead; // number
cursor.rowsWritten; // number
```

### Database Size

```typescript
const bytes = this.ctx.storage.sql.databaseSize;
```

### Transactions (Synchronous)

```typescript
this.ctx.storage.transactionSync(() => {
  this.ctx.storage.sql.exec("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, fromId);
  this.ctx.storage.sql.exec("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, toId);
});
```

**Note**: Callback must be synchronous. Cannot use `await` inside.

### PITR (Point In Time Recovery)

```typescript
// Get current bookmark
const bookmark = await this.ctx.storage.getCurrentBookmark();

// Get bookmark for past time
const pastBookmark = await this.ctx.storage.getBookmarkForTime(
  Date.now() - 24 * 60 * 60 * 1000 // 24 hours ago
);

// Schedule restore on next restart
await this.ctx.storage.onNextSessionRestoreBookmark(pastBookmark);
```

---

## Synchronous KV API (SQLite only)

```typescript
// Access via ctx.storage.kv
const kv = this.ctx.storage.kv;

// Get
const value = kv.get("key"); // Returns value or undefined

// Put
kv.put("key", { data: "value" });

// Delete
const existed = kv.delete("key"); // Returns boolean

// List
for (const [key, value] of kv.list({ prefix: "user:" })) {
  console.log(key, value);
}
```

---

## Async KV API (Both backends)

### Get

```typescript
// Single key
const value = await this.ctx.storage.get<MyType>("key");

// Multiple keys (up to 128)
const map = await this.ctx.storage.get(["key1", "key2", "key3"]);
// Returns Map<string, MyType>
```

### Put

```typescript
// Single key
await this.ctx.storage.put("key", value);

// Multiple keys (up to 128)
await this.ctx.storage.put({
  key1: value1,
  key2: value2,
  key3: value3,
});
```

### Delete

```typescript
// Single key
const existed = await this.ctx.storage.delete("key");

// Multiple keys (up to 128)
const count = await this.ctx.storage.delete(["key1", "key2"]);
```

### List

```typescript
const map = await this.ctx.storage.list();

// With options
const map = await this.ctx.storage.list({
  prefix: "user:",
  start: "user:100",
  end: "user:200",
  limit: 50,
  reverse: true,
});
```

### Delete All

```typescript
await this.ctx.storage.deleteAll();
```

### Sync (Flush to Disk)

```typescript
await this.ctx.storage.sync();
```

---

## Storage Options

```typescript
interface StorageGetOptions {
  allowConcurrency?: boolean; // Don't pause event delivery
  noCache?: boolean; // Bypass cache
}

interface StoragePutOptions {
  allowConcurrency?: boolean;
  allowUnconfirmed?: boolean; // Don't block output gate
  noCache?: boolean;
}
```

---

## Write Coalescing

Multiple writes without `await` are batched:

```typescript
// All coalesced into single transaction
this.ctx.storage.put("a", 1);
this.ctx.storage.put("b", 2);
this.ctx.storage.put("c", 3);
// Committed together

// Awaiting disables coalescing
await this.ctx.storage.put("a", 1); // Separate transaction
await this.ctx.storage.put("b", 2); // Separate transaction
```

---

## Async Transactions (KV)

```typescript
await this.ctx.storage.transaction(async (txn) => {
  const balance = await txn.get("balance");
  if (balance >= amount) {
    await txn.put("balance", balance - amount);
  } else {
    txn.rollback();
  }
});
```

---

## Storage Limits

### SQLite

| Limit             | Value  |
| ----------------- | ------ |
| Storage per DO    | 10 GB  |
| Columns per table | 100    |
| Statement length  | 100 KB |
| Bound params      | 100    |
| Row size          | 2 MB   |
| String/BLOB size  | 2 MB   |

### KV

| Limit      | Value    |
| ---------- | -------- |
| Key size   | 2 KiB    |
| Value size | 128 KiB  |
| Batch size | 128 keys |
