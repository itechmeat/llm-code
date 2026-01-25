# PostgreSQL Wire Protocol Reference

Overview of PostgreSQL frontend/backend protocol (version 3.2).

## Protocol Overview

| Property | Value |
|----------|-------|
| Version | 3.2 (PostgreSQL 18+), backward compatible to 3.0 |
| Transport | TCP/IP, Unix domain sockets |
| Default Port | 5432 |
| Byte Order | Big-endian (network order) |

## Message Format

```
┌──────────┬────────────────┬─────────────────────────────────┐
│  Type    │    Length      │           Payload               │
│  (1B)    │    (4B)        │         (Length - 4)            │
└──────────┴────────────────┴─────────────────────────────────┘
```

Length includes itself (4 bytes) but NOT the type byte.

## Connection Startup

```
Client                              Server
   │── StartupMessage ─────────────────►│
   │◄── Authentication* ────────────────│
   │── Password/SASL* ─────────────────►│
   │◄── AuthenticationOk ───────────────│
   │◄── ParameterStatus* ───────────────│
   │◄── BackendKeyData ─────────────────│
   │◄── ReadyForQuery ──────────────────│
```

### ReadyForQuery Status

| Status | Meaning |
|--------|---------|
| `I` | Idle (not in transaction) |
| `T` | In transaction block |
| `E` | Failed transaction |

## Simple Query Protocol

```
Client                              Server
   │── Query ('Q') ─────────────────────►│
   │◄── RowDescription ('T') ───────────│
   │◄── DataRow ('D') × N ──────────────│
   │◄── CommandComplete ('C') ──────────│
   │◄── ReadyForQuery ('Z') ────────────│
```

## Extended Query Protocol

Supports prepared statements and pipelining:

```
Client                              Server
   │── Parse ('P') ─────────────────────►│  (prepare)
   │◄── ParseComplete ('1') ────────────│
   │── Bind ('B') ──────────────────────►│  (bind params)
   │◄── BindComplete ('2') ─────────────│
   │── Execute ('E') ───────────────────►│  (run)
   │◄── DataRow ('D')... ───────────────│
   │◄── CommandComplete ('C') ──────────│
   │── Sync ('S') ──────────────────────►│  (end pipeline)
   │◄── ReadyForQuery ('Z') ────────────│
```

## Authentication Methods

| Subtype | Method |
|---------|--------|
| 0 | AuthenticationOk |
| 3 | CleartextPassword |
| 5 | MD5Password |
| 10 | SASL (SCRAM-SHA-256) |
| 11 | SASLContinue |
| 12 | SASLFinal |

## COPY Protocol

**COPY TO (Server → Client):**
```
CopyOutResponse → CopyData × N → CopyDone → CommandComplete
```

**COPY FROM (Client → Server):**
```
CopyInResponse → CopyData × N → CopyDone/CopyFail → CommandComplete
```

## Cancellation

Cancel requests use a **new connection**:
1. Client opens new connection
2. Sends CancelRequest with PID + secret key (from BackendKeyData)
3. Connection closed immediately (no response)

## SSL/TLS

```
Client                              Server
   │── SSLRequest ──────────────────────►│
   │◄── 'S' or 'N' ─────────────────────│
   │   [TLS handshake if 'S'] ──────────│
   │── StartupMessage ──────────────────►│
```

## Error Response Fields

| Field | Meaning |
|-------|---------|
| `S` | Severity (ERROR, FATAL, WARNING) |
| `C` | SQLSTATE code |
| `M` | Message |
| `D` | Detail |
| `H` | Hint |
| `P` | Position in query |

## Common Message Types

### Frontend → Backend

| Type | Name | Purpose |
|------|------|---------|
| `Q` | Query | Simple query |
| `P` | Parse | Prepare statement |
| `B` | Bind | Bind parameters |
| `E` | Execute | Execute portal |
| `S` | Sync | End pipeline |
| `X` | Terminate | Close connection |

### Backend → Frontend

| Type | Name | Purpose |
|------|------|---------|
| `R` | Authentication | Auth request/response |
| `T` | RowDescription | Column metadata |
| `D` | DataRow | Row data |
| `C` | CommandComplete | Query done |
| `Z` | ReadyForQuery | Ready for command |
| `E` | ErrorResponse | Error |

## See Also

- [internals.md](internals.md) — Query processing overview
- [authentication.md](authentication.md) — pg_hba.conf
- [PostgreSQL Protocol Docs](https://www.postgresql.org/docs/current/protocol.html)
