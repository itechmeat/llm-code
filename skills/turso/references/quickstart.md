# Quickstart

## Install

### macOS / Linux

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/tursodatabase/turso/releases/latest/download/turso_cli-installer.sh | sh
```

### Windows (PowerShell)

```powershell
irm https://github.com/tursodatabase/turso/releases/latest/download/turso_cli-installer.ps1 | iex
```

## Launch

```bash
tursodb
```

Output:

```text
Turso
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database
turso>
```

## Basic SQL

```sql
-- Create table
CREATE TABLE users (id INT, username TEXT);

-- Insert data
INSERT INTO users VALUES (1, 'alice');
INSERT INTO users VALUES (2, 'bob');

-- Query
SELECT * FROM users;
-- Returns: 1|alice, 2|bob
```

## Experimental Features

Enable with flags:

- `--experimental-encryption`
- `--experimental-mvcc`
- `--experimental-strict`
- `--experimental-views`

**Warning:** Not production ready.
