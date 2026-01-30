# Bun Skill

Agent skill for Bun — the all-in-one JavaScript/TypeScript runtime and toolkit.

## Coverage

This skill covers:

- **Runtime** — TypeScript/JSX execution, module resolution, plugins
- **Package Manager** — `bun install`, `bun add`, lockfiles
- **HTTP Server** — `Bun.serve()`, routing, WebSockets, TLS
- **File System** — `Bun.file()`, `Bun.write()`, streaming
- **Database** — `bun:sqlite`, S3, Redis
- **Shell** — `Bun.$` cross-platform scripting
- **Process** — `Bun.spawn()`, workers, environment
- **Testing** — `bun:test`, mocking, coverage
- **Bundler** — `bun build`, tree-shaking, minification
- **FFI** — Native library calls, C compiler integration
- **Node.js Compatibility** — Module support, global APIs

## Structure

```
bun/
├── SKILL.md           # Main entry point
├── README.md          # This file
├── plan.md            # Ingestion progress (temp)
└── references/
    ├── installation.md
    ├── quickstart.md
    ├── typescript.md
    ├── bun-init.md
    ├── bun-create.md
    ├── runtime.md
    ├── watch-mode.md
    ├── debugging.md
    ├── bunfig.md
    ├── file-types.md
    ├── module-resolution.md
    ├── jsx.md
    ├── auto-install.md
    ├── plugins.md
    ├── file-system-router.md
    ├── http-server.md
    ├── fetch.md
    ├── websockets.md
    ├── tcp.md
    ├── udp.md
    ├── file-io.md
    ├── sqlite.md
    ├── s3.md
    ├── redis.md
    ├── workers.md
    ├── env.md
    ├── shell.md
    ├── spawn.md
    ├── native-interop.md
    ├── cc.md
    ├── transpiler.md
    ├── utilities.md
    └── nodejs-compat.md
```

## Quick Examples

### HTTP Server

```ts
Bun.serve({
  port: 3000,
  fetch(req) {
    return Response.json({ hello: "world" });
  },
});
```

### SQLite

```ts
import { Database } from "bun:sqlite";
const db = new Database("app.db");
const users = db.query("SELECT * FROM users").all();
```

### Shell

```ts
import { $ } from "bun";
await $`echo "Hello" | wc -c`;
```

### WebSocket

```ts
Bun.serve({
  fetch(req, server) {
    server.upgrade(req);
  },
  websocket: {
    message(ws, msg) {
      ws.send(`Echo: ${msg}`);
    },
  },
});
```

## Source

- Documentation: https://bun.sh/docs
- GitHub: https://github.com/oven-sh/bun

## Version

Skill created from Bun documentation as of 2025.
