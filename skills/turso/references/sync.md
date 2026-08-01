# Sync

Synchronize local Turso database with Turso Cloud.

## Setup

### 1. Get Turso Cloud credentials

```bash
turso db show <db>                 # Get URL (turso://... or libsql://...)
turso db tokens create <db>        # Create auth token
```

### 2. Connect with sync

```typescript
import { connect } from "@tursodatabase/sync";

const db = await connect({
  path: "./app.db", // local file
  url: "turso://...", // Turso Cloud URL
  authToken: process.env.TURSO_AUTH_TOKEN, // auth token
  // longPollTimeoutMs: 10_000,              // optional: server wait time
  // bootstrapIfEmpty: false,                // skip initial bootstrap
});
```

**Note:** First run bootstraps from remote (must be reachable). The remote `url` accepts either `turso://` or `libsql://` — every sync binding (Rust, Python, JavaScript, Go, React Native) normalizes both schemes to the same endpoint, so use whichever one `turso db show` prints.

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

---

## MVCC Remotes

A Turso Cloud database replicates either through classic page-based WAL shipping or through MVCC's logical-log format. The sync engine detects which one a remote uses automatically:

- On first contact, the server advertises its pull protocol, and the client persists that choice in its local sync metadata. No client-side flag is required for this — an explicit `logical_mvcc_pull` option still exists as a manual override, but auto-detection is the default.
- If a local replica is still in WAL journal mode when it discovers an MVCC remote, the sync engine converts the local database to MVCC journal mode in place (WAL checkpoint, header rewrite, MVCC store bootstrap) before applying the remote base, then replays preserved local changes on top.
- No code changes are needed to benefit from this — connect the same way regardless of the remote's journal mode.

Related fixes: a change-count leak from sequences running under MVCC is fixed, and `pull()` no longer breaks on tables with composite or non-rowid primary keys — replaying a `DELETE` could previously panic, and upsert conflict targets only matched the first column of a composite key instead of the full key.
