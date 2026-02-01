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
)`
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
