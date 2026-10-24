# Serverless Drivers and Language Bindings

Turso Cloud is reachable over the SQL-over-HTTP protocol. A *serverless driver* speaks that protocol directly: no persistent connection, no WebSocket, no native library — one HTTP request per operation. Since 0.8.0 the family is multi-language: JavaScript/TypeScript, Python, Rust, Go and .NET, each covered by conformance tests against a live database.

Embedded (local-file) drivers are a separate family (`@tursodatabase/database`, the `turso` Python package, the `turso` Rust crate, `turso.tech/database/tursogo`, `Turso.Data.Sqlite`). Every serverless driver mirrors the API of its embedded counterpart, so the same application code can run against a local file or Turso Cloud.

## Driver Matrix

| Language           | Package                                    | Install                                                 | Entry point                                                          |
| ------------------ | ------------------------------------------ | ------------------------------------------------------- | -------------------------------------------------------------------- |
| JavaScript / TS    | `@tursodatabase/serverless`                | `npm install @tursodatabase/serverless`                  | `connect()`; libSQL-compatible `createClient()` from `/compat`        |
| Python             | `turso-serverless` (module `turso_serverless`) | `pip install turso-serverless`                         | `turso_serverless.connect()` (DB-API 2.0)                             |
| Rust               | `turso_serverless`                          | `cargo add turso_serverless`                             | `turso_serverless::Builder`                                           |
| Go                 | `turso.tech/database/tursogo-serverless`    | `go get turso.tech/database/tursogo-serverless`         | `database/sql` driver `turso-serverless`                              |
| .NET               | `Turso.Serverless.Client`                   | `dotnet add package Turso.Serverless.Client`             | `TursoServerlessConnection` over `HttpClient`                         |

New in 0.8.0: the Rust, Go and Python serverless drivers, the .NET serverless client package, and a shared differential test suite that replays random operation sequences against both an embedded driver and the serverless driver.

The .NET provider family (`Turso.Data.Sqlite.Provider`, `Turso.Data.Common`, `Turso.Data.Native`) is not a serverless driver — it is the ADO.NET/EF Core surface, including embedded replicas. It is documented in [](#net-provider-embedded-replicas) below.

## JavaScript / TypeScript

```javascript
import { connect } from "@tursodatabase/serverless";

const conn = connect({
  url: process.env.TURSO_DATABASE_URL,
  authToken: process.env.TURSO_AUTH_TOKEN,
});

const stmt = conn.prepare("SELECT * FROM users WHERE id = ?");
await stmt.get([123]);
await stmt.all([123]);
for await (const row of stmt.iterate([123])) {
  // streamed rows
}
```

- Native surface exposes `run`/`get`/`all`/`iterate`/`exec`/`batch`/`transaction`/`transactionAsync`; `execute()` exists only on the `/compat` libSQL-compatible layer (`createClient()` from `@tursodatabase/serverless/compat`).
- `batch([...])` is one HTTP request; statements run in order and stop at the first failure. The thrown error carries `batchIndex` (index of the failing statement) and `batchResults` (the completed results).
- `transactionAsync(fn)` runs the whole `BEGIN`..`COMMIT` window on a dedicated server session, so it does not lock the connection and concurrent statements on the connection run outside the transaction. The callback must declare the transaction handle (`tx`) and route all transaction SQL through it.
- `transaction(fn)` is deprecated: it emits `BEGIN`/`COMMIT` around the callback on the connection's own stream, so concurrent statements can interleave into the transaction window.
- Transaction modes: the `transaction()` wrapper exposes `.deferred()`, `.immediate()`, `.exclusive()` and `.concurrent()` variants, and `batch(stmts, mode)` accepts the same mode strings (`"deferred"`, `"immediate"`, `"exclusive"`, `"concurrent"`).
- `requestHeaders` can be set per connection or per query (trailing query-options argument on `run`/`get`/`all`/`iterate`); per-query headers merge over connection-level ones.
- **New in 0.8.0**: the `/compat` client implements `reconnect()` — it drops the current session and starts a new one, which is how you recover after a network drop or a server-side session expiry.

## Python

```python
import turso_serverless

conn = turso_serverless.connect(
    "libsql://my-db.turso.io",
    auth_token="...",
)

conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
conn.commit()

for row in conn.execute("SELECT id, name FROM users"):
    print(row)

conn.close()
```

- Pure Python (standard library only), DB-API 2.0, mirroring the embedded `turso` driver.
- Pass `remote_encryption_key="..."` for a customer-managed-encryption database.
- Interactive transactions span several HTTP requests — the server keeps the connection state alive between them: `conn.execute("BEGIN")` → statements → `conn.commit()`.
- **SQLAlchemy** is a separate surface on the embedded `turso` package: dialects `sqlite.turso`, `sqlite.aioturso` and `sqlite.turso_sync`. As of 0.8.0 Turso supports **SQLAlchemy reflection**, and the minimum supported SQLAlchemy version is **2.0.45** (see [installation.md](installation.md)).

## Rust

```rust
use turso_serverless::Builder;

let db = Builder::new_remote(std::env::var("TURSO_DATABASE_URL").unwrap())
    .with_auth_token(std::env::var("TURSO_AUTH_TOKEN").unwrap())
    .build()
    .await?;
let conn = db.connect()?;

conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)", ()).await?;
let mut rows = conn.query("SELECT id, name FROM users", ()).await?;
while let Some(row) = rows.next().await? {
    println!("{} {}", row.get::<i64>(0)?, row.get::<String>(1)?);
}
```

- `Builder::with_remote_encryption_key` sends a customer-managed key on every request.
- **New in 0.8.0**: `Builder::with_auth_token_fn` takes an async callback that is invoked **before every HTTP request**, so short-lived tokens can be rotated (e.g. refreshed from a secrets manager) without rebuilding the database handle:

```rust
let db = turso_serverless::Builder::new_remote("libsql://my-db.turso.io")
    .with_auth_token_fn(|| async { fetch_fresh_token().await })
    .build()
    .await?;
```

- Interactive transactions: `conn.transaction().await?` → `tx.execute(...)` → `tx.commit().await?`. The server keeps the connection state alive between the requests.
- **New in 0.8.0** in the embedded Rust crate: `TransactionBehavior::Concurrent` (`BEGIN CONCURRENT`) lets several write transactions run in parallel, with conflicts detected at commit time. It requires the database in MVCC mode (`PRAGMA journal_mode = 'mvcc'`):

```rust
conn.set_transaction_behavior(TransactionBehavior::Concurrent);
```

## Go

```go
import (
    "database/sql"

    _ "turso.tech/database/tursogo-serverless"
)

dsn := os.Getenv("TURSO_DATABASE_URL") + "?auth_token=" + os.Getenv("TURSO_AUTH_TOKEN")
db, err := sql.Open("turso-serverless", dsn)
```

- Pure Go (no cgo), implements `database/sql`, mirrors the embedded `turso.tech/database/tursogo` driver.
- Keep the token out of the connection string with a connector: `sql.OpenDB(turso.NewConnector(url, authToken))`.
- Customer-managed keys: `turso.NewConnector(url, authToken).WithRemoteEncryptionKey(key)`. The key may also be passed as a `remote_encryption_key` query parameter, but base64 keys contain `+`, `/` and `=`, so the value must be URL-encoded, and the connection string is visible in logs and error messages — prefer the connector.
- Interactive transactions: `db.Begin()` → statements → `tx.Commit()`.

## .NET Serverless Client

```csharp
using Turso.Serverless.Client;

await using var connection = new TursoServerlessConnection(new TursoServerlessConnectionOptions
{
    Url = Environment.GetEnvironmentVariable("TURSO_DATABASE_URL")!,
    AuthToken = Environment.GetEnvironmentVariable("TURSO_AUTH_TOKEN"),
});

var users = await connection.ExecuteAsync("SELECT id, name FROM users WHERE active = ?", [1]);

await connection.BatchAsync(
    [
        new TursoBatchStatement("INSERT INTO logs (msg) VALUES (?)", ["a"]),
        new TursoBatchStatement("INSERT INTO logs (msg) VALUES (?)", ["b"]),
    ],
    TursoBatchMode.Immediate);

await using (var tx = await connection.BeginTransactionAsync(TursoBatchMode.Immediate))
{
    await tx.ExecuteAsync("UPDATE accounts SET balance = balance - 10 WHERE id = ?", [1]);
    await tx.CommitAsync();
}
```

- Pure managed HTTP client, no native component; the .NET counterpart of `@tursodatabase/serverless`. It speaks the same protocol: `POST /v3/pipeline` for request/response operations, `POST /v3/cursor` for streamed results.
- A connection is **single-stream** — one statement at a time, because each request carries the server baton from the previous response. Create several connections for parallelism; construction is free and `HttpClient` pools the transport.
- Also exposes `SequenceAsync` (semicolon-separated scripts, e.g. schema migrations), `DescribeAsync`, `InTransaction`, per-call query timeouts and `RemoteEncryptionKey` (sent as the `x-turso-encryption-key` header).

## .NET Provider (Embedded Replicas)

The ADO.NET provider family is `Turso.Data.Sqlite.Provider` (SQLite-compatible facade, migration path from `Microsoft.Data.Sqlite`), plus `Turso.Data.Common` (shared managed types) and `Turso.Data.Native` (native runtime). 0.8.0 added:

- **Connection-string embedded replicas** — add `Replica Path` to a remote connection string to run queries against a local replica that syncs in the background:

```csharp
await using var replica = new TursoConnection(
    "Data Source=turso://example-org.turso.io;"
    + "Auth Token=eyJ...;"
    + "Replica Path=./replica.db;"
    + "Pooling=True;"
    + "Sync Interval=30");
await replica.OpenAsync();
await replica.SyncAsync(); // pull now, in addition to the automatic schedule
```

  `Pooling=True` shares one file replica and one automatic-sync schedule among connections with the same path and options. `AutomaticSyncStatus` and `AutomaticSyncStatusChanged` report waiting / running / retrying / faulted / stopped states, the last pull result and the next attempt; transient transport, I/O and timeout failures are retried twice.

- **Managed pull-replica API** — `TursoSyncDatabase` gives explicit control over the replica and the sync configuration:

```csharp
var options = new TursoSyncDatabaseOptions("./replica.db", new Uri("turso://example-org.turso.io"))
{
    AuthToken = authToken,
    PartialSync = new TursoPartialSyncOptions { PrefixLength = 4 * 1024 * 1024, SegmentSize = 256 * 1024, Prefetch = true },
    PushOperationsThreshold = 1000,
    PullBytesThreshold = 1024 * 1024,
    ForceLogicalMvccPull = true,
    ExperimentalFeatures = "views",
};

await using var database = await TursoSyncDatabase.CreateAsync(options);
await using var local = await database.ConnectAsync();
var changed = await database.PullAsync();   // never pushes local writes
var stats = await database.GetStatsAsync();
await database.PushAsync();                  // explicit; last-write-wins conflict policy
await database.CheckpointAsync();
```

  Sync failures surface as `TursoSyncException` carrying the operation, native status, sanitized endpoint, HTTP method/status and the original exception.

- **Batches on embedded replicas** — ADO.NET `DbBatch` is supported. Direct remote batches are sent as one Hrana request; replica batches run each command sequentially against the local replica and expose each result through `NextResult`. Replica batches are **not implicitly atomic** — assign an explicit transaction when the commands must commit or roll back together (`batch.Transaction = transaction`).
- **Advanced sync database options** — connection-string keywords (`Sync Client Name`, `Sync Long Poll Timeout`, `Bootstrap If Empty`, `Partial Bootstrap Prefix`/`Query`, `Partial Sync Segment Size`/`Prefetch`, `Remote Encryption Cipher`/`Key`, `Push Operations Threshold`, `Pull Bytes Threshold`, `Force Logical MVCC Pull`, `Sync Experimental Features`) map onto `TursoSyncDatabaseOptions`. Local `Encryption Cipher`/`Encryption Key` configure the local file only, not remote replica encryption.
- **Separate HTTP client packages** — `Turso.Serverless.Client` (pure managed serverless driver) and `Turso.Platform.Client` (HTTP client for the Turso Platform API at `api.turso.tech`) are now distinct from the provider packages.
- EF Core: `Turso.EntityFrameworkCore.Sqlite` adds `UseTurso(...)` for local, direct-remote and embedded-replica backends.

## Shared Behaviors

- A batch is one HTTP request; statements execute in order and stop at the first failure.
- Interactive transactions span multiple HTTP requests — the server keeps the connection state alive between them, so the driver does not need a long-lived socket.
- Customer-managed encryption: every driver sends the base64 key with every request (`remote_encryption_key` in Python/Go, `with_remote_encryption_key` in Rust, `RemoteEncryptionKey` in .NET).
- Auth tokens can be static or per-request. Rust supports a rotating callback (`Builder::with_auth_token_fn`); the other drivers take the token at connection time.
- Conformance tests run against a live Turso Cloud instance and skip themselves when `TURSO_DATABASE_URL` / `TURSO_AUTH_TOKEN` are not set.

## Choosing a Driver

- **JavaScript/TypeScript** — `@tursodatabase/serverless`; add `@tursodatabase/serverless/compat` when migrating libSQL code that calls `execute()`.
- **Python** — `turso-serverless` for raw DB-API access; use the SQLAlchemy dialects (reflection supported, SQLAlchemy >= 2.0.45) for ORM work.
- **Rust** — `turso_serverless`; use `with_auth_token_fn` when the auth token is short-lived.
- **Go** — `tursogo-serverless` behind `database/sql`, with `turso.NewConnector(...)` to keep the token out of the DSN.
- **.NET** — `Turso.Serverless.Client` for a pure HTTP client; `Turso.Data.Sqlite.Provider` when you need ADO.NET, EF Core or an embedded replica.
- **Embedded replica** (local reads plus background sync) — .NET `TursoSyncDatabase`, or the JavaScript sync package `@tursodatabase/sync` (see [sync.md](sync.md)).

## Protocol

The wire protocol is specified upstream: `serverless/PROTOCOL.md` in the turso repository (<https://github.com/tursodatabase/turso/blob/main/serverless/PROTOCOL.md>). Driver behavior is also covered by the conformance suites under `serverless/<language>/conformance`.
