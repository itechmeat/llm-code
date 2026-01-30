# WebSockets

## Server-Side WebSockets

### Basic Server

```typescript
Bun.serve({
  fetch(req, server) {
    if (server.upgrade(req)) {
      return; // Upgraded, no Response needed
    }
    return new Response("Not a WebSocket request", { status: 400 });
  },
  websocket: {
    open(ws) {
      console.log("Connected");
    },
    message(ws, message) {
      ws.send(`Echo: ${message}`);
    },
    close(ws, code, reason) {
      console.log("Disconnected");
    },
    drain(ws) {
      // Ready to receive more data
    },
  },
});
```

### Upgrade with Headers/Data

```typescript
Bun.serve({
  fetch(req, server) {
    const url = new URL(req.url);
    const userId = url.searchParams.get("user");

    server.upgrade(req, {
      headers: {
        "Set-Cookie": "session=abc123",
      },
      data: {
        userId,
        connectedAt: Date.now(),
      },
    });
  },
  websocket: {
    message(ws, message) {
      console.log(`User ${ws.data.userId}: ${message}`);
    },
  },
});
```

### TypeScript Data Typing

```typescript
type WsData = {
  userId: string;
  room: string;
};

Bun.serve<WsData>({
  websocket: {
    message(ws, message) {
      // ws.data is typed as WsData
      console.log(ws.data.userId);
    },
  },
});
```

## Pub/Sub

Built-in topic-based broadcasting:

```typescript
const server = Bun.serve({
  websocket: {
    open(ws) {
      ws.subscribe("chat-room");
      ws.publish("chat-room", "New user joined!");
    },
    message(ws, message) {
      // Broadcast to all subscribers (except sender)
      ws.publish("chat-room", message);
    },
    close(ws) {
      ws.unsubscribe("chat-room");
    },
  },
});

// Server-level publish (to all subscribers)
server.publish("chat-room", "Server announcement!");
```

### Subscription Methods

```typescript
ws.subscribe("topic");           // Join topic
ws.unsubscribe("topic");         // Leave topic
ws.publish("topic", message);    // Send to others
ws.isSubscribed("topic");        // Check subscription
ws.subscriptions;                // Get all topics
server.subscriberCount("topic"); // Count subscribers
```

## Compression

```typescript
Bun.serve({
  websocket: {
    perMessageDeflate: true,
  },
});

// Per-message compression
ws.send("Hello", true); // Compress this message
```

## Configuration

```typescript
Bun.serve({
  websocket: {
    idleTimeout: 120,              // Seconds (default: 120)
    maxPayloadLength: 16 * 1024 * 1024, // Bytes (default: 16MB)
    backpressureLimit: 1024 * 1024,     // Bytes (default: 1MB)
    closeOnBackpressureLimit: false,
    sendPings: true,
    publishToSelf: false,
  },
});
```

## Backpressure Handling

```typescript
const result = ws.send(message);
// -1: Enqueued but backpressure
//  0: Dropped (connection issue)
// 1+: Bytes sent
```

## Client-Side WebSocket

```typescript
const socket = new WebSocket("ws://localhost:3000");

// Bun extension: custom headers
const socket = new WebSocket("ws://localhost:3000", {
  headers: {
    "Authorization": "Bearer token",
  },
});

socket.addEventListener("open", () => {
  socket.send("Hello");
});

socket.addEventListener("message", (event) => {
  console.log(event.data);
});

socket.addEventListener("close", (event) => {
  console.log(event.code, event.reason);
});
```

## Chat Example

```typescript
const server = Bun.serve({
  fetch(req, server) {
    const url = new URL(req.url);
    const username = url.searchParams.get("name") || "Anonymous";

    if (server.upgrade(req, { data: { username } })) {
      return;
    }
    return new Response("Expected WebSocket", { status: 400 });
  },
  websocket: {
    open(ws) {
      ws.subscribe("chat");
      server.publish("chat", `${ws.data.username} joined`);
    },
    message(ws, message) {
      server.publish("chat", `${ws.data.username}: ${message}`);
    },
    close(ws) {
      server.publish("chat", `${ws.data.username} left`);
    },
  },
});
```

## Key Points

- Handlers declared once per server (not per socket) — more efficient
- Native pub/sub — no Redis needed for simple cases
- `ws.data` for per-connection state
- `server.upgrade()` returns boolean (true = success)
- Return `undefined` after successful upgrade, not `Response`
