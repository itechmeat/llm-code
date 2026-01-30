# SQLite

Native high-performance SQLite3 driver via `bun:sqlite`.

## Basic Usage

```typescript
import { Database } from "bun:sqlite";

const db = new Database("mydb.sqlite");
// const db = new Database(":memory:");  // In-memory

const query = db.query("SELECT * FROM users WHERE id = ?");
const user = query.get(1);
```

## Database Options

```typescript
// Read-only
new Database("mydb.sqlite", { readonly: true });

// Create if not exists
new Database("mydb.sqlite", { create: true });

// Strict mode (throws on missing params)
new Database(":memory:", { strict: true });

// BigInt support for large integers
new Database(":memory:", { safeIntegers: true });
```

## Import via ES Module

```typescript
import db from "./mydb.sqlite" with { type: "sqlite" };
```

## Queries

### Prepare Statement

```typescript
const query = db.query("SELECT * FROM users WHERE id = ?");
```

### Execute Methods

```typescript
// All results as array of objects
query.all(1);
// [{ id: 1, name: "John" }]

// First result
query.get(1);
// { id: 1, name: "John" } or undefined

// Execute (for INSERT/UPDATE/DELETE)
query.run(1);
// { lastInsertRowid: 5, changes: 1 }

// Results as arrays
query.values(1);
// [[1, "John"]]

// Iterate (memory efficient)
for (const row of query.iterate()) {
  console.log(row);
}
```

## Parameters

```typescript
// Positional
db.query("SELECT ?1, ?2").all("a", "b");

// Named (with prefix)
db.query("SELECT $name, $age").all({ $name: "John", $age: 30 });

// Named (strict mode, no prefix)
db.query("SELECT $name").all({ name: "John" }); // requires strict: true
```

## Map to Class

```typescript
class User {
  id: number;
  name: string;

  get displayName() {
    return `User #${this.id}: ${this.name}`;
  }
}

const users = db.query("SELECT * FROM users").as(User).all();
console.log(users[0].displayName);
```

## Transactions

```typescript
const insert = db.prepare("INSERT INTO users (name) VALUES ($name)");

const insertMany = db.transaction((users) => {
  for (const user of users) {
    insert.run(user);
  }
  return users.length;
});

// Auto-commit on success, rollback on error
const count = insertMany([
  { $name: "Alice" },
  { $name: "Bob" },
]);

// Transaction types
insertMany.deferred(users);   // BEGIN DEFERRED
insertMany.immediate(users);  // BEGIN IMMEDIATE
insertMany.exclusive(users);  // BEGIN EXCLUSIVE
```

## WAL Mode

Enable for better concurrent performance:

```typescript
db.run("PRAGMA journal_mode = WAL;");
```

## Quick Operations

```typescript
// Run SQL directly (for DDL, bulk writes)
db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)");
db.run("INSERT INTO users (name) VALUES (?)", ["John"]);
```

## Closing

```typescript
db.close();        // Allow pending queries to finish
db.close(true);    // Throw if pending queries

// Using statement (auto-close)
{
  using db = new Database("mydb.sqlite");
  // ... use db
} // Auto-closed here
```

## Serialize/Deserialize

```typescript
// Backup database to bytes
const backup = db.serialize();

// Restore from bytes
const restored = Database.deserialize(backup);
```

## Data Types

| JavaScript   | SQLite          |
| ------------ | --------------- |
| `string`     | TEXT            |
| `number`     | INTEGER/DECIMAL |
| `boolean`    | INTEGER (1/0)   |
| `Uint8Array` | BLOB            |
| `bigint`     | INTEGER         |
| `null`       | NULL            |

## Performance Tips

- Use prepared statements (`db.query()`) — cached and reused
- Enable WAL mode for concurrent access
- Use transactions for bulk writes
- Use `.values()` for raw arrays (faster than objects)
- Use `safeIntegers: true` only if needed

## Example: REST API

```typescript
import { Database } from "bun:sqlite";

const db = new Database("app.sqlite");
db.run("PRAGMA journal_mode = WAL");

db.run(`
  CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    done INTEGER DEFAULT 0
  )
`);

const getTodos = db.query("SELECT * FROM todos");
const getTodo = db.query("SELECT * FROM todos WHERE id = ?");
const addTodo = db.query("INSERT INTO todos (title) VALUES (?) RETURNING *");
const toggleTodo = db.query("UPDATE todos SET done = NOT done WHERE id = ?");

Bun.serve({
  routes: {
    "/todos": {
      GET: () => Response.json(getTodos.all()),
      POST: async (req) => {
        const { title } = await req.json();
        return Response.json(addTodo.get(title));
      },
    },
    "/todos/:id/toggle": (req) => {
      toggleTodo.run(req.params.id);
      return Response.json(getTodo.get(req.params.id));
    },
  },
});
```
