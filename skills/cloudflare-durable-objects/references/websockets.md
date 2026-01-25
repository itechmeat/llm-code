# WebSocket Hibernation

## Overview

WebSocket Hibernation allows Durable Objects to hibernate (be evicted from memory) while keeping WebSocket connections alive at the Cloudflare edge.

## Accept WebSocket

```typescript
export class ChatRoom extends DurableObject<Env> {
  async fetch(request: Request): Promise<Response> {
    if (request.headers.get("Upgrade") === "websocket") {
      const pair = new WebSocketPair();
      const [client, server] = Object.values(pair);

      // Accept with hibernation support
      this.ctx.acceptWebSocket(server);

      return new Response(null, { status: 101, webSocket: client });
    }
    return new Response("Expected WebSocket", { status: 400 });
  }
}
```

## WebSocket Handlers

```typescript
export class ChatRoom extends DurableObject<Env> {
  async webSocketMessage(ws: WebSocket, message: string | ArrayBuffer): Promise<void> {
    // Called when message received (DO wakes if hibernated)
    const data = JSON.parse(message as string);
    this.broadcast(data);
  }

  async webSocketClose(ws: WebSocket, code: number, reason: string, wasClean: boolean): Promise<void> {
    // Called on disconnect
  }

  async webSocketError(ws: WebSocket, error: unknown): Promise<void> {
    // Called on error
  }
}
```

## Tags

Associate tags with WebSockets for filtering:

```typescript
// Accept with tags (max 10 tags, 256 chars each)
this.ctx.acceptWebSocket(server, ["room:123", "user:456"]);

// Get WebSockets by tag
const roomSockets = this.ctx.getWebSockets("room:123");

// Get tags for WebSocket
const tags = this.ctx.getTags(ws);
```

## Per-Connection State

Store state that survives hibernation:

```typescript
// Save attachment (max 2048 bytes, structured clone)
ws.serializeAttachment({
  userId: "123",
  username: "Alice",
  joinedAt: Date.now()
});

// Retrieve in message handler
async webSocketMessage(ws: WebSocket, message: string | ArrayBuffer) {
  const state = ws.deserializeAttachment();
  console.log(`Message from ${state.username}`);
}
```

## Auto-Response

Respond to messages without waking DO:

```typescript
// Set auto-response for ping/pong
this.ctx.setWebSocketAutoResponse(new WebSocketRequestResponsePair("ping", "pong"));

// Clear auto-response
this.ctx.setWebSocketAutoResponse(null);

// Get current auto-response
const pair = this.ctx.getWebSocketAutoResponse();

// Get last auto-response time for socket
const timestamp = this.ctx.getWebSocketAutoResponseTimestamp(ws);
```

## Broadcast Pattern

```typescript
export class ChatRoom extends DurableObject<Env> {
  private broadcast(message: string, exclude?: WebSocket) {
    for (const ws of this.ctx.getWebSockets()) {
      if (ws !== exclude) {
        ws.send(message);
      }
    }
  }

  async webSocketMessage(ws: WebSocket, message: string | ArrayBuffer) {
    this.broadcast(message as string, ws); // Send to all except sender
  }
}
```

## Hibernation Lifecycle

1. **Active**: Processing messages
2. **Idle**: No activity for ~10 seconds
3. **Hibernate**: DO evicted, WebSockets stay connected at edge
4. **Wake**: On message, constructor runs, handler called

## Hibernation Conditions

All must be true:

- No pending `setTimeout`/`setInterval`
- No in-progress `await fetch()`
- Using `ctx.acceptWebSocket()` (not standard WebSocket)
- No active request being processed

## Event Timeout

```typescript
// Set max time for WebSocket event (max 7 days)
this.ctx.setHibernatableWebSocketEventTimeout(300_000); // 5 minutes

// Get current timeout
const timeout = this.ctx.getHibernatableWebSocketEventTimeout();
```

## Limits

| Limit                          | Value           |
| ------------------------------ | --------------- |
| WebSocket connections per DO   | 32,768          |
| Message size (received)        | 32 MiB          |
| Tags per WebSocket             | 10              |
| Tag length                     | 256 chars       |
| Attachment size                | 2048 bytes      |
| Auto-response request/response | 2048 chars each |
| Event timeout                  | 7 days max      |

## Important Notes

- Hibernation only works for WebSocket servers (not outgoing connections)
- In-memory state is lost on hibernation
- Code deployments disconnect all WebSockets
- Standard WebSocket API prevents hibernation
