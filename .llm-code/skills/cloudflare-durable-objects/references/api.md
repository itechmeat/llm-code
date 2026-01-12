# Durable Objects API Reference

## DurableObject Base Class

```typescript
import { DurableObject } from "cloudflare:workers";

export class MyDO extends DurableObject<Env> {
  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
  }

  // RPC methods
  async myMethod(): Promise<T> {}

  // HTTP handler (optional)
  async fetch(request: Request): Promise<Response> {}

  // Alarm handler (optional)
  async alarm(info?: AlarmInfo): Promise<void> {}

  // WebSocket handlers (optional, for hibernation)
  async webSocketMessage(ws: WebSocket, message: string | ArrayBuffer): Promise<void> {}
  async webSocketClose(ws: WebSocket, code: number, reason: string, wasClean: boolean): Promise<void> {}
  async webSocketError(ws: WebSocket, error: unknown): Promise<void> {}
}
```

## DurableObjectState

```typescript
interface DurableObjectState {
  readonly id: DurableObjectId;
  readonly storage: DurableObjectStorage;

  // Concurrency control
  blockConcurrencyWhile<T>(callback: () => Promise<T>): Promise<T>;

  // No effect in DO (compatibility only)
  waitUntil(promise: Promise<any>): void;

  // WebSocket Hibernation
  acceptWebSocket(ws: WebSocket, tags?: string[]): void;
  getWebSockets(tag?: string): WebSocket[];
  getTags(ws: WebSocket): string[];
  setWebSocketAutoResponse(pair?: WebSocketRequestResponsePair): void;
  getWebSocketAutoResponse(): WebSocketRequestResponsePair | null;
  getWebSocketAutoResponseTimestamp(ws: WebSocket): Date | null;
  setHibernatableWebSocketEventTimeout(timeoutMs?: number): void;
  getHibernatableWebSocketEventTimeout(): number | null;

  // Force reset
  abort(message?: string): void;
}
```

## DurableObjectId

```typescript
interface DurableObjectId {
  readonly name?: string; // Only if created with idFromName
  toString(): string;
  equals(other: DurableObjectId): boolean;
}
```

## DurableObjectNamespace (Binding)

```typescript
interface DurableObjectNamespace<T extends DurableObject> {
  // Get ID from name (deterministic)
  idFromName(name: string): DurableObjectId;

  // Create new unique ID
  newUniqueId(options?: { jurisdiction?: "eu" }): DurableObjectId;

  // Parse ID from string
  idFromString(hexId: string): DurableObjectId;

  // Get stub for DO instance
  get(id: DurableObjectId): DurableObjectStub<T>;
}
```

## DurableObjectStub

```typescript
interface DurableObjectStub<T extends DurableObject> {
  readonly id: DurableObjectId;
  readonly name?: string;

  // HTTP request (legacy)
  fetch(request: Request | string, init?: RequestInit): Promise<Response>;

  // RPC methods - call directly on stub
  // All public methods from T are callable
}
```

## AlarmInfo

```typescript
interface AlarmInfo {
  readonly isRetry: boolean;
  readonly retryCount: number;
}
```

## WebSocketRequestResponsePair

```typescript
class WebSocketRequestResponsePair {
  constructor(request: string, response: string);
  readonly request: string; // Max 2048 chars
  readonly response: string; // Max 2048 chars
}
```

## ID Creation Patterns

```typescript
// Deterministic ID from name
const id = env.MY_DO.idFromName("user:123");

// Random unique ID
const id = env.MY_DO.newUniqueId();

// EU jurisdiction (data stays in EU)
const id = env.MY_DO.newUniqueId({ jurisdiction: "eu" });

// Parse from string
const id = env.MY_DO.idFromString(hexIdString);

// Get stub
const stub = env.MY_DO.get(id);
```

## Calling Durable Objects

### RPC (Recommended)

```typescript
// Direct method calls
const result = await stub.myMethod(arg1, arg2);
const data = await stub.getData();
await stub.updateData(newData);
```

### HTTP (Legacy)

```typescript
const response = await stub.fetch("https://fake-host/path", {
  method: "POST",
  body: JSON.stringify(data),
});
```

## Wrangler Configuration

### wrangler.jsonc

```jsonc
{
  "durable_objects": {
    "bindings": [
      {
        "name": "MY_DO", // Binding name in env
        "class_name": "MyDO", // Exported class name
        "script_name": "other" // Optional: external Worker
      }
    ]
  },
  "migrations": [
    {
      "tag": "v1",
      "new_sqlite_classes": ["MyDO"]
    }
  ]
}
```

### wrangler.toml

```toml
[[durable_objects.bindings]]
name = "MY_DO"
class_name = "MyDO"

[[migrations]]
tag = "v1"
new_sqlite_classes = ["MyDO"]
```
