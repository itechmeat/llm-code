# D1 Workers Binding API

## D1Database Methods

### prepare(query)

Creates a prepared statement.

```typescript
const stmt = env.DB.prepare("SELECT * FROM users WHERE id = ?");
```

### batch(statements)

Executes array of statements atomically (transaction).

```typescript
const results = await env.DB.batch([env.DB.prepare("INSERT INTO users (name) VALUES (?)").bind("Alice"), env.DB.prepare("INSERT INTO logs (action) VALUES (?)").bind("user_created"), env.DB.prepare("SELECT * FROM users")]);
// results — array of D1Result for each statement
```

**Important**: If any statement fails, all roll back.

### exec(query)

Executes raw SQL without parameterization.

```typescript
const result = await env.DB.exec(`
  CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT);
  INSERT INTO users (name) VALUES ('System');
`);
// result: D1ExecResult { count: 2, duration: 1.5 }
```

**Warning**: Do not use with user input — no SQL injection protection.

### withSession(bookmark?)

Creates session for read replication.

```typescript
const session = env.DB.withSession("first-unconstrained");
const { results } = await session.prepare("SELECT * FROM users").run();
const bookmark = session.getBookmark();
```

---

## D1PreparedStatement Methods

### bind(...values)

Binds values to `?` placeholders.

```typescript
// Positional parameters
const stmt = env.DB.prepare("SELECT * FROM users WHERE id = ? AND status = ?");
const bound = stmt.bind(123, "active");

// Supported types: string, number, boolean, null, ArrayBuffer
stmt.bind("text", 42, true, null);
```

**Type conversion**:
| JavaScript | SQLite | On read |
|------------|--------|---------|
| null | NULL | null |
| number | REAL/INTEGER | number |
| string | TEXT | string |
| boolean | INTEGER (0/1) | number |
| ArrayBuffer | BLOB | Array |

### run()

Executes statement and returns full D1Result.

```typescript
const result = await env.DB.prepare("UPDATE users SET name = ? WHERE id = ?").bind("Bob", 1).run();

// result.meta.changes — number of changed rows
// result.results — empty for UPDATE/INSERT/DELETE
```

### first(column?)

Returns first row or specific column value.

```typescript
// Full row
const user = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(1).first();
// user: { id: 1, name: "Alice" } or null

// Specific column
const name = await env.DB.prepare("SELECT name FROM users WHERE id = ?").bind(1).first("name");
// name: "Alice" or null
```

**Note**: Does not add LIMIT 1 automatically — add it yourself for performance.

### all()

Returns all rows as D1Result.

```typescript
const { results } = await env.DB.prepare("SELECT * FROM users LIMIT 10").all();
// results: Array<{ id: number, name: string }>
```

### raw(options?)

Returns data as array of arrays (no column names per row).

```typescript
const rows = await env.DB.prepare("SELECT id, name FROM users").raw();
// rows: [[1, "Alice"], [2, "Bob"]]

// With column names
const rowsWithColumns = await env.DB.prepare("SELECT id, name FROM users").raw({ columnNames: true });
// rowsWithColumns: [["id", "name"], [1, "Alice"], [2, "Bob"]]
```

---

## D1Result Structure

```typescript
interface D1Result<T> {
  success: boolean;
  meta: {
    served_by: string; // backend version
    served_by_region: string; // region (WEUR, ENAM, etc.)
    served_by_primary: boolean; // true if primary
    duration: number; // total time (ms)
    changes: number; // rows changed
    last_row_id: number; // last ROWID
    rows_read: number; // rows read (billing)
    rows_written: number; // rows written (billing)
  };
  results: T[];
}
```

## D1ExecResult Structure

```typescript
interface D1ExecResult {
  count: number; // number of executed statements
  duration: number; // total time (ms)
}
```

---

## TypeScript Generics

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

// Typed results
const { results } = await env.DB.prepare("SELECT * FROM users").all<User>();
// results: User[]

const user = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(1).first<User>();
// user: User | null
```

---

## Patterns

### Transaction-like batch

```typescript
async function transferFunds(from: number, to: number, amount: number) {
  const results = await env.DB.batch([env.DB.prepare("UPDATE accounts SET balance = balance - ? WHERE id = ?").bind(amount, from), env.DB.prepare("UPDATE accounts SET balance = balance + ? WHERE id = ?").bind(amount, to)]);
  return results.every((r) => r.success);
}
```

### Upsert pattern

```typescript
await env.DB.prepare(
  `
    INSERT INTO users (id, name, updated_at) 
    VALUES (?, ?, datetime('now'))
    ON CONFLICT(id) DO UPDATE SET 
      name = excluded.name,
      updated_at = excluded.updated_at
  `
)
  .bind(userId, userName)
  .run();
```

### Pagination

```typescript
const page = 1;
const pageSize = 20;

const { results } = await env.DB.prepare("SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?")
  .bind(pageSize, (page - 1) * pageSize)
  .all();
```
