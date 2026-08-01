# Agent Databases

AI agents need databases for context, state, and memory. Two approaches:

- **Embedded** — local-first, offline-capable
- **Turso Sync** — distributed coordination with cloud persistence

## Embedded (Local-First)

```javascript
import { connect } from "@tursodatabase/database";

const db = await connect("agent.db");

db.prepare(
  `CREATE TABLE IF NOT EXISTS steps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL,
  result TEXT
)`,
).run();

db.prepare("INSERT INTO steps (action, result) VALUES (?, ?)").run("fetch_data", "success");
```

**Benefits:** Zero latency, offline, single-file deployment.

## Turso Sync (Cloud-Connected)

```javascript
const db = await connect({
  path: "agent-memory.db",
  url: "https://your-database.turso.io",
  authToken: "your-auth-token",
  sync: "full",
});

await db.sync(); // Manual sync
```

**Sync modes:** `sync` (bidirectional), `pull` (cloud → agent), `push` (agent → cloud)

## Multi-Agent Patterns

### Isolated Databases

```javascript
const agent1DB = await connect("agent-1.db");
const agent2DB = await connect("agent-2.db");
```

### Shared Database

```javascript
const agent1DB = await connect({
  path: "agent-1-local.db",
  url: "https://shared-tasks.turso.io",
  sync: "full",
});

const agent2DB = await connect({
  path: "agent-2-local.db",
  url: "https://shared-tasks.turso.io", // Same URL
  sync: "full",
});
```

### Hub-and-Spoke

```javascript
const workerDB = await connect({ sync: "push", ... });      // Worker: push only
const coordinatorDB = await connect({ sync: "pull", ... }); // Coordinator: pull only
```

## Query Budgets and Timeouts

The JavaScript/serverless surface exposes explicit timeout controls. For agent loops, prefer bounded query/connection time over implicit hanging network calls.

- Use per-connection or per-statement timeouts when the client surface exposes them.
- In HTTP/serverless flows, wire cancellation into your runtime budget rather than waiting for the default connection lifecycle.
- Fail fast on expired work instead of letting one stuck query consume the whole agent turn.

## Atomic Transactions

`@tursodatabase/database` and `@tursodatabase/serverless` expose a callback-based transaction helper, in the style of `better-sqlite3`, that is a good fit for an agent's multi-step write ("record this action, then update the state row") without hand-rolling `BEGIN`/`COMMIT`:

```javascript
import { connect } from "@tursodatabase/database";

const db = await connect("agent.db");

const recordStep = db.transactionAsync(async (txn, steps) => {
  const insert = await txn.prepare("INSERT INTO steps (action, result) VALUES (?, ?)");
  for (const step of steps) {
    await insert.run(step.action, step.result);
  }
});

await recordStep([{ action: "fetch_data", result: "success" }]);
```

Always use the `txn` handle passed into the callback for statements inside the transaction — never the outer `db`/`conn` instance. The older `transaction(fn)` method, which closes over the outer instance instead of taking an explicit transaction parameter, is now **deprecated**: once more than one transaction can be in flight at a time (the normal case for a multi-agent or multi-worker setup sharing a connection), statements scheduled through the closed-over instance can be interleaved out of order, producing unsound results. `transactionAsync()` fixes this by threading a dedicated transaction handle through the callback — migrate any agent code that opens transactions to the new signature, especially under concurrent access.

## Interactive Transactions

Turso now documents interactive transactions for multi-step read/write invariants.

- Use them for short, stateful critical sections such as balance/lease updates or compare-and-swap style orchestration.
- Do not keep them open across slow tool calls, human approval steps, or long LLM turns.
- Current docs note a 5-second transaction window and write locking until commit/rollback, so they are not a fit for long-running coordination flows.

## Python Agent Backends

For Python services, prefer the official `sqlalchemy-libsql` integration instead of custom DBAPI glue. That keeps local-only, remote-only, and embedded-replica setups on the documented path and aligns well with async web backends that still want ORM ergonomics.

## Useful SQL Surface for Agents

The SQL surface has a few features that matter for agent workflows:

- `CREATE TABLE AS SELECT` is useful for checkpointing, materializing intermediate search results, or creating review snapshots.
- Temporary tables are useful for short-lived planning/output staging without polluting durable schema.
- `CREATE DOMAIN` / `DROP DOMAIN` and STRICT composite types (`STRUCT`, `UNION`) let you encode stronger contracts when agents write semi-structured state.

Prefer these features when they simplify state transitions, but keep production schemas intentionally small and reviewable.

## Database-Per-Agent (Platform API)

```javascript
import { createClient } from "@tursodatabase/api";

const turso = createClient({
  token: process.env.TURSO_PLATFORM_API_TOKEN,
  org: process.env.TURSO_ORG_NAME,
});

const database = await turso.databases.create(`agent-${agentId}`, {
  group: "default",
});
```

**Benefits:** Complete isolation, independent scaling, easy cleanup.
