# Installation

## macOS / Linux

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/tursodatabase/turso/releases/latest/download/turso_cli-installer.sh | sh
```

## Windows (PowerShell)

```powershell
irm https://github.com/tursodatabase/turso/releases/latest/download/turso_cli-installer.ps1 | iex
```

## Launch

```bash
tursodb           # In-memory database
tursodb mydata.db # File database
```

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
