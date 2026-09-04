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
  port: 8080, // Default: $BUN_PORT, $PORT, 3000
  hostname: "0.0.0.0", // Default: "0.0.0.0"
  // port: 0,        // Random available port
});
```

## Server Methods

```typescript
// Stop server
await server.stop(); // Graceful (wait for requests)
await server.stop(true); // Force close all connections

// Hot reload handlers
server.reload({
  routes: { "/": new Response("v2") },
  fetch(req) {
    return new Response("v2");
  },
});

// Process lifecycle
server.unref(); // Don't keep process alive
server.ref(); // Keep process alive (default)
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
server.pendingRequests; // Active HTTP requests
server.pendingWebSockets; // Active WebSocket connections
server.subscriberCount("topic"); // WebSocket subscribers
```

## Error Handler

```typescript
Bun.serve({
  fetch(req) {
    /* ... */
  },
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
      return success ? undefined : new Response("Upgrade failed", { status: 400 });
    }
    return new Response("Hello");
  },
  websocket: {
    open(ws) {
      console.log("Connected");
    },
    message(ws, msg) {
      ws.send(`Echo: ${msg}`);
    },
    close(ws) {
      console.log("Disconnected");
    },
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
      return user ? Response.json(user) : new Response("Not Found", { status: 404 });
    },
  },
});
```

## HTTP/2 & HTTP/3 (v1.4)

`Bun.serve()` serves HTTP/1.1 and HTTP/2 on the same port, negotiated via ALPN over TLS. WebSockets and trailers are not supported over HTTP/2 yet.

HTTP/3 is experimental; enable with `http3: true` alongside `tls`:

```typescript
Bun.serve({
  tls: { cert: Bun.file("cert.pem"), key: Bun.file("key.pem") },
  http3: true,
  fetch(req) {
    return new Response("Hello over HTTP/3");
  },
});
```

Do not ship `http3: true` to production yet: `server.upgrade()` returns `false` over HTTP/3 and 0-RTT is disabled.

### Serve Static Directories

```typescript
Bun.serve({
  routes: {
    "/static/*": { dir: "./public" },
  },
});
```

Static directory routes use sendfile with ETag, Range, conditional requests, and `index.html`; path traversal is blocked (`openat2 O_RESOLVE_BENEATH`). HTML-route sourcemaps are no longer served in production (opt back in via `[serve.static] sourcemap` in `bunfig.toml`).

Backpressure: `Bun.serve()` and `fetch()` pause streams when the socket buffer fills.

## Key Points

- Use `Bun.serve()` not `http.createServer()`
- Routes object for declarative routing
- `req.params` for URL parameters
- `Response.json()` for JSON responses
- WebSocket support built-in via `server.upgrade()`

## Runtime notes (v1.3.12)

- Linux `Bun.serve()` now enables `TCP_DEFER_ACCEPT`, which can reduce latency on busy HTTP listeners.
- Async handlers that resume after `await` no longer hit the same write-batching performance cliff under concurrency.
