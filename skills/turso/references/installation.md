# Installation

## macOS / Linux

```bash
brew install tursodatabase/tap/turso
```

Or use the official install script:

```bash
curl -sSfL https://get.tur.so/install.sh | bash
```

## Windows

Windows installation is documented via WSL. Start a WSL shell from PowerShell:

```powershell
wsl
```

Then run the standard installer inside WSL:

```bash
curl -sSfL https://get.tur.so/install.sh | bash
```

## Launch

```bash
turso             # Verify CLI installation
tursodb           # In-memory database
tursodb mydata.db # File database
```

For ephemeral CI/dev usage, Turso `0.6.0` also ships an npm package, so `npx turso <command>` is a reasonable no-global-install path when your environment is already Node-based.

## Basic SQL

```sql
CREATE TABLE users (id INT, username TEXT);
INSERT INTO users VALUES (1, 'alice');
SELECT * FROM users;
```

## Experimental Flags

`tursodb` gates newer SQL features behind flags:

- `--experimental-encryption` — enable encryption
- `--experimental-views` — materialized views
- `--experimental-custom-types` — `CREATE TYPE` / `DROP TYPE`
- `--experimental-generated-columns` — generated columns
- `--experimental-attach` — `ATTACH DATABASE`
- `--experimental-vacuum` / `--experimental-autovacuum` — vacuum and autovacuum
- `--experimental-index-method` — pluggable index methods
- `--experimental-without-rowid` — `WITHOUT ROWID` tables
- `--experimental-multiprocess-wal` — multiprocess WAL coordination
- `--experimental-mvcc-passive-checkpoint` — passive checkpointing (requires `journal_mode=mvcc`)

**Warning:** Not production ready.

MVCC itself is no longer behind a flag — enable it per database with `PRAGMA journal_mode = 'mvcc'` instead of a CLI switch.

## Python / SQLAlchemy

Turso documents SQLAlchemy via the `sqlalchemy-libsql` dialect, and the embedded `turso` Python package ships the dialects `sqlite.turso`, `sqlite.aioturso` and `sqlite.turso_sync`.

```bash
pip install sqlalchemy-libsql
```

Use standard SQLAlchemy engines for local, remote, memory-only, or embedded-replica setups, and keep Turso credentials in environment variables instead of hardcoding them.

As of 0.8.0 Turso supports **SQLAlchemy reflection**, so `MetaData.reflect()` and ORM autogeneration work against a Turso database. This requires **SQLAlchemy 2.0.45 or newer** — pin the minimum version in your dependency set.

For raw DB-API access to Turso Cloud over HTTP, use the separate serverless driver instead of the ORM path (see [serverless-drivers.md](serverless-drivers.md)).
