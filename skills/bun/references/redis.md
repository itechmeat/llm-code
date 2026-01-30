# Bun Redis Client

Native Redis client with Promise-based API. Supports Redis 7.2+.

## Connection

```ts
import { redis, RedisClient } from "bun";

// Global singleton (reads REDIS_URL or VALKEY_URL env var)
await redis.set("key", "value");

// Custom client
const client = new RedisClient("redis://localhost:6379");

// With auth
const client = new RedisClient("redis://user:pass@localhost:6379/0");

// TLS
const client = new RedisClient("rediss://localhost:6379");
// or
const client = new RedisClient("redis+tls://localhost:6379");

// Unix socket
const client = new RedisClient("redis+unix:///path/to/socket");
```

## Environment Variables

Checked in order:

1. `REDIS_URL`
2. `VALKEY_URL`
3. Default: `redis://localhost:6379`

## Connection Lifecycle

```ts
const client = new RedisClient();

// Auto-connect on first command
await client.set("key", "value");

// Or explicit connect
await client.connect();

// Check status
console.log(client.connected);      // boolean
console.log(client.bufferedAmount); // bytes buffered

// Close when done
client.close();
```

## Connection Events

```ts
client.onconnect = () => {
  console.log("Connected");
};

client.onclose = (error) => {
  console.error("Disconnected:", error);
};
```

## Connection Options

```ts
const client = new RedisClient("redis://localhost:6379", {
  connectionTimeout: 5000,      // ms (default: 10000)
  idleTimeout: 30000,           // ms (default: 0 = no timeout)
  autoReconnect: true,          // default: true
  maxRetries: 10,               // default: 10
  enableOfflineQueue: true,     // queue commands when disconnected
  enableAutoPipelining: true,   // batch commands automatically
  tls: true,                    // or { ca, cert, key, rejectUnauthorized }
});
```

## String Operations

```ts
// Set/Get
await redis.set("key", "value");
const value = await redis.get("key");

// Get as Uint8Array
const buffer = await redis.getBuffer("key");

// Delete
await redis.del("key");

// Check existence
const exists = await redis.exists("key"); // boolean

// Expiration
await redis.expire("key", 3600);  // seconds
const ttl = await redis.ttl("key");
```

## Numeric Operations

```ts
await redis.set("counter", "0");
await redis.incr("counter");  // +1
await redis.decr("counter");  // -1
```

## Hash Operations

```ts
// Set multiple fields
await redis.hmset("user:123", [
  "name", "Alice",
  "email", "[email protected]",
]);

// Get multiple fields
const [name, email] = await redis.hmget("user:123", ["name", "email"]);

// Get single field
const name = await redis.hget("user:123", "name");

// Increment numeric field
await redis.hincrby("user:123", "visits", 1);
await redis.hincrbyfloat("user:123", "score", 1.5);
```

## Set Operations

```ts
// Add member
await redis.sadd("tags", "javascript");

// Remove member
await redis.srem("tags", "javascript");

// Check membership
const isMember = await redis.sismember("tags", "js"); // boolean

// Get all members
const all = await redis.smembers("tags");

// Random member
const random = await redis.srandmember("tags");

// Pop random
const popped = await redis.spop("tags");
```

## Raw Commands

```ts
// Any Redis command
const info = await redis.send("INFO", []);

await redis.send("LPUSH", ["mylist", "v1", "v2"]);
const list = await redis.send("LRANGE", ["mylist", "0", "-1"]);
```

## Pub/Sub

**Note**: Subscription mode takes over the connection. Use `.duplicate()` for commands.

```ts
const redis = new RedisClient("redis://localhost:6379");
await redis.connect();

// Duplicate for commands while subscribed
const subscriber = await redis.duplicate();

// Subscribe
await subscriber.subscribe("channel", (message, channel) => {
  console.log(`${channel}: ${message}`);
});

// Publish (from non-subscribed client)
await redis.publish("channel", "Hello!");

// Unsubscribe
await subscriber.unsubscribe();           // all channels
await subscriber.unsubscribe("channel");  // specific channel
```

## Pipelining

Commands are automatically pipelined:

```ts
// These run concurrently
const [a, b] = await Promise.all([
  redis.get("key1"),
  redis.get("key2"),
]);
```

Disable if needed:

```ts
const client = new RedisClient(url, {
  enableAutoPipelining: false,
});
```

## Type Conversion

| Redis Type      | JavaScript Type |
| --------------- | --------------- |
| Integer         | `number`        |
| Bulk string     | `string`        |
| Null            | `null`          |
| Array           | `Array`         |
| Boolean (RESP3) | `boolean`       |
| Map (RESP3)     | `Object`        |
| Set (RESP3)     | `Array`         |

Special cases:

- `EXISTS` → `boolean`
- `SISMEMBER` → `boolean`

## Error Handling

```ts
try {
  await redis.get("key");
} catch (error) {
  switch (error.code) {
    case "ERR_REDIS_CONNECTION_CLOSED":
      // Connection lost
      break;
    case "ERR_REDIS_AUTHENTICATION_FAILED":
      // Auth failed
      break;
    case "ERR_REDIS_INVALID_RESPONSE":
      // Invalid response
      break;
  }
}
```

## Reconnection

Automatic exponential backoff:

- Starts at 50ms, doubles each attempt
- Capped at 2000ms
- Up to `maxRetries` attempts (default: 10)
- Commands queued if `enableOfflineQueue: true`

## Practical Patterns

### Caching

```ts
async function getUserCached(userId: string) {
  const key = `user:${userId}`;

  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const user = await db.getUser(userId);
  await redis.set(key, JSON.stringify(user));
  await redis.expire(key, 3600);

  return user;
}
```

### Rate Limiting

```ts
async function rateLimit(ip: string, limit = 100, windowSecs = 3600) {
  const key = `ratelimit:${ip}`;

  const count = await redis.incr(key);
  if (count === 1) {
    await redis.expire(key, windowSecs);
  }

  return {
    limited: count > limit,
    remaining: Math.max(0, limit - count),
  };
}
```

### Session Storage

```ts
async function createSession(userId: number, data: object) {
  const sessionId = crypto.randomUUID();
  const key = `session:${sessionId}`;

  await redis.hmset(key, [
    "userId", String(userId),
    "created", String(Date.now()),
    "data", JSON.stringify(data),
  ]);
  await redis.expire(key, 86400); // 24h

  return sessionId;
}

async function getSession(sessionId: string) {
  const key = `session:${sessionId}`;

  if (!await redis.exists(key)) return null;

  const [userId, created, data] = await redis.hmget(key, [
    "userId", "created", "data",
  ]);

  return {
    userId: Number(userId),
    created: Number(created),
    data: JSON.parse(data!),
  };
}
```

## Limitations

Current:

- Transactions (MULTI/EXEC) via raw commands only

Unsupported:

- Redis Sentinel
- Redis Cluster
