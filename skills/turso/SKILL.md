---
name: turso
description: "Turso SQLite database. Covers encryption, sync, agent patterns. Use when working with Turso/libSQL embedded databases, configuring encryption-at-rest, setting up sync replication, or building agent-friendly database patterns. Keywords: Turso, libSQL, embedded, SQLite, encryption, sync."
metadata:
  version: "0.5.3"
  release_date: "2026-04-02"
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
  url: "libsql://...",
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

Based on product version: 0.5.3

## Links

- [Documentation](https://docs.turso.tech/)
- [Changelog](https://github.com/tursodatabase/turso/blob/main/CHANGELOG.md)
- [GitHub](https://github.com/tursodatabase/turso)
