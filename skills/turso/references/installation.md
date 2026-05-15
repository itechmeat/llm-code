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

- `--experimental-encryption` — enable encryption
- `--experimental-mvcc` — multi-version concurrency
- `--experimental-strict` — strict mode

**Warning:** Not production ready.

## Python / SQLAlchemy (v0.6.0)

Turso documents SQLAlchemy via the `sqlalchemy-libsql` dialect. Prefer the official dialect over ad-hoc wrappers for Python services or agent backends, and treat the `0.6.0` line as the point where Python coverage became more practical for asyncio-heavy apps and named-parameter usage.

```bash
pip install sqlalchemy-libsql
```

Use standard SQLAlchemy engines for local, remote, memory-only, or embedded-replica setups, and keep Turso credentials in environment variables instead of hardcoding them.
