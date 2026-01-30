# HTTP Server

## Basic Server

```typescript
const server = Bun.serve({
  port: 3000,
  fetch(req) {
    return new Response("Hello!");
  },
});

console.log(`Server running at ${server.url}`);
```

## Routes (Bun 1.2.3+)

```typescript
Bun.serve({
  routes: {
    // Static response
    "/": new Response("Home"),

    // Dynamic handler
    "/users/:id": (req) => {
      return new Response(`User ${req.params.id}`);
    },

    // Per-method handlers
    "/api/posts": {
      GET: () => Response.json({ posts: [] }),
      POST: async (req) => {
        const body = await req.json();
        return Response.json({ created: true, ...body });
      },
    },

    // Wildcard
    "/api/*": Response.json({ error: "Not found" }, { status: 404 }),

    // Redirect
    "/old": Response.redirect("/new"),

    // Serve file
    "/favicon.ico": Bun.file("./favicon.ico"),
  },

  // Fallback for unmatched
  fetch(req) {
    return new Response("Not Found", { status: 404 });
  },
});
```

## HTML Imports

```typescript
import app from "./index.html";

Bun.serve({
  routes: {
    "/": app,
  },
});
```

- **Development** (`bun --hot`): On-demand bundling, HMR
- **Production** (`bun build`): Pre-built manifest

## Configuration

```typescript
Bun.serve({
  port: 8080,        // Default: $BUN_PORT, $PORT, 3000
  hostname: "0.0.0.0", // Default: "0.0.0.0"
  // port: 0,        // Random available port
});
```

## Server Methods

```typescript
// Stop server
await server.stop();       // Graceful (wait for requests)
await server.stop(true);   // Force close all connections

// Hot reload handlers
server.reload({
  routes: { "/": new Response("v2") },
  fetch(req) { return new Response("v2"); },
});

// Process lifecycle
server.unref();  // Don't keep process alive
server.ref();    // Keep process alive (default)
```

## Per-Request Controls

```typescript
Bun.serve({
  fetch(req, server) {
    // Set timeout (seconds)
    server.timeout(req, 60);

    // Get client IP
    const ip = server.requestIP(req);
    // { address: "127.0.0.1", port: 54321, family: "IPv4" }

    return new Response("OK");
  },
});
```

## Metrics

```typescript
server.pendingRequests;     // Active HTTP requests
server.pendingWebSockets;   // Active WebSocket connections
server.subscriberCount("topic"); // WebSocket subscribers
```

## Error Handler

```typescript
Bun.serve({
  fetch(req) { /* ... */ },
  error(error) {
    console.error(error);
    return new Response("Server Error", { status: 500 });
  },
});
```

## WebSocket Upgrade

```typescript
Bun.serve({
  fetch(req, server) {
    if (req.headers.get("upgrade") === "websocket") {
      const success = server.upgrade(req, {
        data: { userId: "123" },
      });
      return success
        ? undefined
        : new Response("Upgrade failed", { status: 400 });
    }
    return new Response("Hello");
  },
  websocket: {
    open(ws) { console.log("Connected"); },
    message(ws, msg) { ws.send(`Echo: ${msg}`); },
    close(ws) { console.log("Disconnected"); },
  },
});
```

## Export Default Syntax

```typescript
export default {
  port: 3000,
  fetch(req) {
    return new Response("Hello");
  },
} satisfies import("bun").Serve;
```

## REST API Example

```typescript
import { Database } from "bun:sqlite";

const db = new Database("app.db");

Bun.serve({
  routes: {
    "/api/users": {
      GET: () => Response.json(db.query("SELECT * FROM users").all()),
      POST: async (req) => {
        const { name } = await req.json();
        const id = crypto.randomUUID();
        db.run("INSERT INTO users (id, name) VALUES (?, ?)", [id, name]);
        return Response.json({ id, name }, { status: 201 });
      },
    },
    "/api/users/:id": (req) => {
      const user = db.query("SELECT * FROM users WHERE id = ?").get(req.params.id);
      return user
        ? Response.json(user)
        : new Response("Not Found", { status: 404 });
    },
  },
});
```

## Key Points

- Use `Bun.serve()` not `http.createServer()`
- Routes object for declarative routing
- `req.params` for URL parameters
- `Response.json()` for JSON responses
- WebSocket support built-in via `server.upgrade()`
