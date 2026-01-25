# Sync

Synchronize local Turso database with Turso Cloud.

## Setup

### 1. Get Turso Cloud credentials

```bash
turso db show <db>                 # Get URL (libsql://...)
turso db tokens create <db>        # Create auth token
```

### 2. Connect with sync

```typescript
import { connect } from "@tursodatabase/sync";

const db = await connect({
  path: "./app.db", // local file
  url: "libsql://...", // Turso Cloud URL
  authToken: process.env.TURSO_AUTH_TOKEN, // auth token
  // longPollTimeoutMs: 10_000,              // optional: server wait time
  // bootstrapIfEmpty: false,                // skip initial bootstrap
});
```

**Note:** First run bootstraps from remote (must be reachable).

## Operations

### Push (local → remote)

```typescript
await db.exec("INSERT INTO notes VALUES ('n1', 'hello')");
await db.push(); // Send local changes to cloud
```

Conflict resolution: "last push wins"

### Pull (remote → local)

```typescript
const changed = await db.pull(); // Returns true if changes applied
```

Use `longPollTimeoutMs` to wait for changes (avoids empty replies).

### Checkpoint

Compacts local WAL to bound disk usage:

```typescript
await db.checkpoint();
```

### Stats

```typescript
const s = await db.stats();
// cdcOperations, mainWalSize, networkReceivedBytes, networkSentBytes, revision
```

---

## Partial Sync

Sync only what you need. Lazy page fetching on demand.

### Bootstrap Strategies

**Prefix bootstrap** — download first N bytes:

```typescript
const db = await connect({
  path: "./app.db",
  url: "libsql://...",
  authToken: process.env.TURSO_AUTH_TOKEN,
  partialSync: {
    bootstrapStrategy: { kind: "prefix", length: 128 * 1024 }, // 128 KiB
  },
});
```

**Query bootstrap** — download pages touched by query:

```typescript
const db = await connect({
  path: "./app.db",
  url: "libsql://...",
  authToken: process.env.TURSO_AUTH_TOKEN,
  partialSync: {
    bootstrapStrategy: {
      kind: "query",
      query: `SELECT * FROM messages WHERE user_id = 'u_123' LIMIT 100`,
    },
  },
});
```

### Optimizations

**Segment size** — batch nearby pages (default 128 KiB):

```typescript
partialSync: {
  segmentSize: 16 * 1024,  // 16 KiB segments
}
```

**Prefetch** — proactively fetch likely-needed pages:

```typescript
partialSync: {
  prefetch: true,
}
```

Use both for best performance on real workloads.
