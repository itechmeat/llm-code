---
name: turso
description: "Turso SQLite database. Covers encryption, sync, agent patterns. Use when working with Turso/libSQL embedded databases, configuring encryption-at-rest, setting up sync replication, or building agent-friendly database patterns. Keywords: Turso, libSQL, embedded, SQLite, encryption, sync."
metadata:
  version: "0.7.2"
  release_date: "2026-07-30"
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
| Encryption    | [encryption.md](references/encryption.md)     |
| Authorization | [auth.md](references/auth.md)                 |
| Sync          | [sync.md](references/sync.md)                 |
| Agent DBs     | [agents.md](references/agents.md)             |

## When to Use

- Embedded SQLite database with cloud sync
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

## Common Patterns

### Encrypted Database

```bash
openssl rand -hex 32  # Generate key
tursodb --experimental-encryption "file:db.db?cipher=aegis256&hexkey=YOUR_KEY"
```

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

## Version

Based on product version: 0.7.2

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
