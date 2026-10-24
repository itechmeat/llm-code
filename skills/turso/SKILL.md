---
name: turso
description: "Turso SQLite database. Covers encryption, sync, serverless drivers, agent patterns. Use when working with Turso/libSQL embedded databases, configuring encryption-at-rest, setting up sync replication, choosing a Turso serverless driver for JS/Python/Rust/Go/.NET, or building agent-friendly database patterns. Keywords: Turso, libSQL, embedded, SQLite, encryption, sync, serverless driver."
metadata:
  version: "0.8.0"
  release_date: "2026-09-28"
---

# Turso Database

SQLite-compatible embedded database for modern applications, AI agents, and edge computing.

## Links

- [Documentation](https://docs.turso.tech/)
- [Changelog](https://github.com/tursodatabase/turso/blob/main/CHANGELOG.md)
- [GitHub](https://github.com/tursodatabase/turso)

## Quick Navigation

| Topic         | Reference                                     |
| ------------- | --------------------------------------------- |
| Installation  | [installation.md](references/installation.md) |
| Quickstart    | [quickstart.md](references/quickstart.md)       |
| Encryption    | [encryption.md](references/encryption.md)     |
| Authorization | [auth.md](references/auth.md)                 |
| Sync          | [sync.md](references/sync.md)                 |
| Drivers       | [serverless-drivers.md](references/serverless-drivers.md) |
| Agent DBs     | [agents.md](references/agents.md)             |

## When to Use

- Embedded SQLite database with cloud sync
- Serverless and edge runtimes in JavaScript/TypeScript, Python, Rust, Go or .NET
- AI agent state management and multi-agent coordination
- Offline-first applications
- Encrypted databases (AEGIS, AES-GCM)
- Edge computing and IoT devices

## Core Concepts

### libSQL

Turso is built on libSQL, an open-source fork of SQLite with:

- Native encryption (AEGIS-256, AES-GCM)
- Async I/O (Linux io_uring)
- Cloud sync capabilities

### Deployment Options

1. **Embedded** — runs locally in your app
2. **Turso Cloud** — managed platform with branching, backups
3. **Hybrid** — local with cloud sync (push/pull)
4. **Serverless / edge** — Turso Cloud over the SQL-over-HTTP protocol, no persistent connections (see `references/serverless-drivers.md`)

### Concurrency

MVCC journal mode is selected per database with `PRAGMA journal_mode = 'mvcc'`. It is what allows several write transactions to run in parallel (`BEGIN CONCURRENT`, exposed as `TransactionBehavior::Concurrent` in Rust and the `concurrent` transaction mode in JavaScript).

## Common Patterns

### Encrypted Database

```bash
openssl rand -hex 32  # Generate key
tursodb --experimental-encryption "file:db.db?cipher=aegis256&hexkey=YOUR_KEY"
```

### Serverless Connection (SQL over HTTP)

```javascript
// JavaScript / TypeScript
import { connect } from "@tursodatabase/serverless";
const conn = connect({ url: process.env.TURSO_DATABASE_URL, authToken: process.env.TURSO_AUTH_TOKEN });
```

```python
# Python
import turso_serverless
conn = turso_serverless.connect("libsql://my-db.turso.io", auth_token="...")
```

```rust
// Rust
let db = turso_serverless::Builder::new_remote(url)
    .with_auth_token(token)
    .build()
    .await?;
```

```go
// Go
db, _ := sql.Open("turso-serverless", url+"?auth_token="+token)
```

The Rust, Go and Python drivers are new in 0.8.0; the .NET equivalent is `Turso.Serverless.Client`. Full matrix in `references/serverless-drivers.md`.

### Cloud Sync

```typescript
import { connect } from "@tursodatabase/sync";

const db = await connect({
  path: "./local.db",
  url: "turso://...", // also accepts "libsql://..." — both schemes work
  authToken: process.env.TURSO_AUTH_TOKEN,
});

await db.push(); // local → cloud
await db.pull(); // cloud → local
```

### Agent Database

```javascript
import { connect } from "@tursodatabase/database";

// Local-first
const db = await connect("agent.db");

// Or with sync
const db = await connect({
  path: "agent.db",
  url: "https://db.turso.io",
  authToken: "...",
  sync: "full",
});
```

## Query Plans

`EXPLAIN QUERY PLAN` returns the classic four-column rows. `EXPLAIN QUERY PLAN FORMAT=JSON` (the clause is case-insensitive) returns one row with a single TEXT column named `plan_json`:

```sql
EXPLAIN QUERY PLAN FORMAT=JSON SELECT * FROM users WHERE age > 21;
```

The JSON document carries `version`, `sql`, `result_columns`, `nodes` and `cte_materializations`. `nodes` lists the same rows the text form prints, in the same order, with `id`/`parent` encoding the tree (`parent: null` marks a root) and `detail` holding the exact display string. Each node also has a structured `op` discriminated by `op.type`: `scan`, `search`, `multi_index`, `index_method`, `hash_join`, `hash_build`, `distinct`, `distinct_aggregate`, `order_by`, `group_by`, `compound`, `compound_arm`, `list_subquery`, `scalar_subquery`, `recursive_setup`, `recursive_step` and `constant_row`.

Table-access nodes may include an `estimate` object with the values that selected the join plan: `input_rows`, `rows_per_input`, `output_rows`, `access_cost` and `total_cost`. Those are planner estimates, not execution counters. The JSON format is not stable across minor versions — pin the client version if you parse it in production.

## Version

Based on product version: 0.8.0

## Release Highlights (0.8.0)

- **Multi-language serverless drivers**: the SQL-over-HTTP driver family now spans JavaScript, Python, Rust, Go and .NET. The Rust (`turso_serverless`), Go (`turso.tech/database/tursogo-serverless`) and Python (`turso-serverless`) drivers are new in 0.8.0, each with conformance tests; the .NET serverless client ships as its own package (`Turso.Serverless.Client`). See `references/serverless-drivers.md` for the full matrix.
- **.NET bindings**: batches on embedded replicas, connection-string embedded replicas (`Replica Path`), a managed pull-replica API (`TursoSyncDatabase.PullAsync`), advanced sync database options, and separate HTTP client packages.
- **Rust serverless**: `Builder::with_auth_token_fn` runs an async callback before every HTTP request, so short-lived auth tokens can be rotated without rebuilding the database handle.
- **Rust bindings**: `TransactionBehavior::Concurrent` (`BEGIN CONCURRENT`) lets several write transactions run in parallel with conflicts detected at commit time; it requires `PRAGMA journal_mode = 'mvcc'`.
- **Query plans**: `EXPLAIN QUERY PLAN FORMAT=JSON` emits machine-readable plans (see [Query Plans](#query-plans)).
- **SQL surface**: the window-function set grows to `rank()`, `dense_rank()`, `first_value()`, `last_value()`, `nth_value()`, `cume_dist()` and `percent_rank()`; indexes support `NULLS FIRST` / `NULLS LAST` ordering; `PRAGMA count_changes` reports row-change counts.
- **Experimental PostgreSQL layer**: an experimental `tursopg` surface exposes Postgres-compatible access to Turso databases — treat it as experimental, not as the stable driver path.
- **Python bindings**: SQLAlchemy reflection is now supported by Turso, with a minimum SQLAlchemy version of 2.0.45.
- **Serverless compatibility**: the JS libSQL-compatible layer (`@tursodatabase/serverless/compat`) implements `reconnect()`.
- **Core/MVCC**: group commit is enabled by default and FULL waiters share the group-commit log; connect-time and post-`ANALYZE` stats refresh is resumable, refreshed `ANALYZE` stats are published to the shared schema, the optimizer costs repeated index seeks and required grouping sorts, and `core/connection` supports passive mode in the checkpoint API.
- **FTS**: search accepts null and non-text inputs and rejects non-finite field weights; rowid readers are reused across queries, tombstones are keyed by document identity so deletes and merges commute, and segments are merged on the write path past a threshold.
- **Fixes**: upsert conflict targets now match generated-column indexes and `REPLACE` defaults are applied before virtual generated columns are computed; binding fixes across Python, JS, Rust, Go and .NET.

## Release Notes

### 0.7.1 – 0.7.2

- **JS/serverless SDK**: `transactionAsync()` is the new closure-safe transaction API. `transaction()` is now deprecated — its closure semantics are unsound once transactions can run concurrently, because statements captured over the outer `db`/`conn` instance can be scheduled out of order. Migrate transaction callbacks to use the `txn` handle passed into `transactionAsync()` instead of closing over the outer instance (see `references/agents.md`).
- **Breaking**: `Connection.execute()` was removed from the serverless driver's native-mirroring surface (`connect()`), which now matches `@tursodatabase/database` and exposes `run`/`get`/`all`/`iterate`/`exec`/`batch`/`transaction(Async)` instead. The libsql-compatible `createClient()` layer keeps its own `execute()` and is unaffected (see `references/auth.md`).
- Fixed a stale `inTransaction` flag after `execute()`/`batch()` that could leave a server-side write transaction open past a constraint error.
- Per-query `requestHeaders`, passed through the trailing query-options argument, let you attach custom headers (e.g. a request-identity header) to a single call instead of only at the connection level.
- **Sync engine**: the remote pull protocol (page-based WAL vs. MVCC logical-log) is now auto-detected on first contact, so the old `logical_mvcc_pull` flag becomes an optional manual override instead of a requirement. A WAL-mode local replica is automatically converted to MVCC journal mode in place when it syncs against an MVCC remote.
- Sync bindings (Rust, Python, JavaScript, Go, React Native) accept both `turso://` and `libsql://` remote URLs interchangeably.
- **Core fixes**: an `IN (...)` list query-cost regression that degraded `InSeek` to a full scan, a missing index left behind after `UPSERT` due to a pre-constraint-check index mutation, a change-count leak from sequences under MVCC, and DELETE/upsert replay bugs for tables with composite or non-rowid primary keys.

### 0.7.0

- **SQL surface**: SQL-standard scalar functions with PostgreSQL-compatible aliases, PostgreSQL-style sequences, MVCC-safe `AUTOINCREMENT`, window-function work (`row_number()` on VDBE aggregate machinery, `FILTER` in window clauses), and `WITHIN GROUP` ordered-set aggregates.
- **MVCC/durability**: passive checkpoint for MVCC, portable logical-log metadata for Turso sync, and Aristo WAL verification.
- **Collations**: core custom collation support and locale-backed collations.
- **.NET / platforms**: NativeAOT static linking, remote transactions and batches, a Turso EF Core SQLite provider, NuGet native targets, and Windows ARM64 CLI releases.

### Earlier (0.6.0)

JS/serverless timeouts, interactive transactions, Python SQLAlchemy improvements (`sqlalchemy-libsql`), npm-based CLI distribution, and a broader SQL surface for local-first/agent workloads — still in effect, see `references/agents.md` and `references/installation.md`.
