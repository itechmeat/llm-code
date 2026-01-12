# Runtime & Handlers

Workers runtime APIs and handler types.

## Handler Types

### Fetch Handler

Primary handler for HTTP requests.

```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return new Response("Hello!");
  },
} satisfies ExportedHandler<Env>;
```

#### Parameters

| Parameter | Type               | Description                 |
| --------- | ------------------ | --------------------------- |
| `request` | `Request`          | Incoming HTTP request       |
| `env`     | `Env`              | Bindings (KV, R2, D1, etc.) |
| `ctx`     | `ExecutionContext` | Execution context           |

#### ExecutionContext Methods

```typescript
interface ExecutionContext {
  waitUntil(promise: Promise<any>): void; // Background work
  passThroughOnException(): void; // Fall through on error
}
```

---

### Scheduled Handler (Cron)

Triggered by cron expressions.

```typescript
export default {
  async scheduled(controller: ScheduledController, env: Env, ctx: ExecutionContext) {
    console.log(`Cron triggered at ${controller.scheduledTime}`);
    ctx.waitUntil(doWork(env));
  },
};
```

#### Configuration

```toml
# wrangler.toml
[triggers]
crons = [
  "0 * * * *",      # Every hour
  "0 0 * * *",      # Daily at midnight
  "*/5 * * * *"     # Every 5 minutes
]
```

#### ScheduledController

```typescript
interface ScheduledController {
  scheduledTime: number; // Unix timestamp (ms)
  cron: string; // Cron pattern that triggered
  noRetry(): void; // Prevent retry on failure
}
```

#### Local Testing

```bash
# Trigger via HTTP in dev mode
curl http://localhost:8787/__scheduled
```

---

### Queue Handler

Process messages from Cloudflare Queues.

```typescript
export default {
  async queue(batch: MessageBatch, env: Env, ctx: ExecutionContext) {
    for (const message of batch.messages) {
      try {
        await processMessage(message.body);
        message.ack();
      } catch (e) {
        message.retry();
      }
    }
  },
};
```

#### Message Methods

| Method              | Description                     |
| ------------------- | ------------------------------- |
| `message.ack()`     | Acknowledge (remove from queue) |
| `message.retry()`   | Retry later                     |
| `message.body`      | Message payload                 |
| `message.id`        | Message ID                      |
| `message.timestamp` | Enqueue timestamp               |

#### Configuration

```toml
# wrangler.toml
[[queues.consumers]]
queue = "my-queue"
max_batch_size = 10
max_batch_timeout = 30
max_retries = 3
dead_letter_queue = "my-dlq"
```

---

### Email Handler

Process inbound emails.

```typescript
export default {
  async email(message: EmailMessage, env: Env, ctx: ExecutionContext) {
    const { from, to, raw } = message;
    console.log(`Email from ${from} to ${to}`);

    // Forward email
    await message.forward("admin@example.com");
  },
};
```

---

## Runtime APIs

### Request

Standard Fetch API Request with Cloudflare extensions.

```typescript
const request = new Request("https://example.com", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ key: "value" }),
  cf: {
    cacheTtl: 300,
    cacheEverything: true,
  },
});
```

#### Cloudflare Request Properties

```typescript
interface CfProperties {
  colo: string; // Cloudflare colo (e.g., "SJC")
  country: string; // Country code
  city: string; // City name
  continent: string; // Continent code
  latitude: string; // Latitude
  longitude: string; // Longitude
  postalCode: string; // Postal code
  region: string; // Region name
  regionCode: string; // Region code
  timezone: string; // Timezone
  asn: number; // ASN
  asOrganization: string; // AS organization name
  httpProtocol: string; // HTTP protocol version
  tlsVersion: string; // TLS version
  tlsCipher: string; // TLS cipher
  botManagement?: object; // Bot Management data
}

// Access via request.cf
const country = request.cf?.country;
```

---

### Response

Standard Fetch API Response.

```typescript
// Text response
new Response("Hello");

// JSON response
Response.json({ message: "Hello" });

// Redirect
Response.redirect("https://example.com", 301);

// With headers
new Response("Hello", {
  status: 200,
  headers: {
    "Content-Type": "text/plain",
    "Cache-Control": "max-age=3600",
  },
});
```

---

### Fetch API

Make outbound HTTP requests.

```typescript
const response = await fetch("https://api.example.com/data", {
  method: "GET",
  headers: { Authorization: "Bearer token" },
  cf: {
    cacheTtl: 300,
    cacheEverything: true,
  },
});

const data = await response.json();
```

#### Cloudflare Fetch Options

```typescript
interface CfFetchOptions {
  cacheTtl?: number; // Cache TTL in seconds
  cacheTtlByStatus?: Record<string, number>;
  cacheEverything?: boolean; // Cache all content types
  cacheKey?: string; // Custom cache key
  scrapeShield?: boolean; // Enable Scrape Shield
  minify?: { javascript?: boolean; css?: boolean; html?: boolean };
  mirage?: boolean; // Enable Mirage
  polish?: "lossy" | "lossless" | "off";
  resolveOverride?: string; // Override resolved hostname
}
```

---

### Cache API

Control Cloudflare cache.

```typescript
const cache = caches.default;

// Check cache
const cachedResponse = await cache.match(request);
if (cachedResponse) {
  return cachedResponse;
}

// Store in cache
const response = await fetch(request);
ctx.waitUntil(cache.put(request, response.clone()));
return response;
```

#### Cache Methods

| Method                         | Description         |
| ------------------------------ | ------------------- |
| `cache.match(request)`         | Get cached response |
| `cache.put(request, response)` | Store response      |
| `cache.delete(request)`        | Purge from cache    |

---

### HTMLRewriter

Transform HTML responses on the fly.

```typescript
const response = await fetch(request);

return new HTMLRewriter()
  .on("h1", {
    element(element) {
      element.setInnerContent("Modified Title");
    },
  })
  .on("a[href]", {
    element(element) {
      const href = element.getAttribute("href");
      element.setAttribute("href", href.replace("http://", "https://"));
    },
  })
  .transform(response);
```

---

### Streams

Web Streams API for streaming data.

```typescript
// ReadableStream
const stream = new ReadableStream({
  start(controller) {
    controller.enqueue("Hello ");
    controller.enqueue("World");
    controller.close();
  },
});

// TransformStream
const { readable, writable } = new TransformStream({
  transform(chunk, controller) {
    controller.enqueue(chunk.toUpperCase());
  },
});
```

---

### Web Crypto

Cryptographic operations.

```typescript
// Generate random bytes
const randomBytes = crypto.getRandomValues(new Uint8Array(16));

// Generate UUID
const uuid = crypto.randomUUID();

// Hash data
const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("data"));

// HMAC sign
const key = await crypto.subtle.importKey("raw", new TextEncoder().encode("secret"), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
const signature = await crypto.subtle.sign("HMAC", key, data);
```

---

### WebSockets

Real-time bidirectional communication.

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const upgradeHeader = request.headers.get("Upgrade");
    if (upgradeHeader !== "websocket") {
      return new Response("Expected WebSocket", { status: 400 });
    }

    const [client, server] = Object.values(new WebSocketPair());

    server.accept();
    server.addEventListener("message", (event) => {
      server.send(`Echo: ${event.data}`);
    });

    return new Response(null, {
      status: 101,
      webSocket: client,
    });
  },
};
```

---

## Node.js Compatibility

Enable Node.js APIs with compatibility flag:

```toml
# wrangler.toml
compatibility_flags = ["nodejs_compat"]
```

Supported modules:

- `node:buffer`
- `node:crypto`
- `node:events`
- `node:path`
- `node:stream`
- `node:util`
- `node:url`
- And more (partial support)

```typescript
import { Buffer } from "node:buffer";
import { createHash } from "node:crypto";

const hash = createHash("sha256").update("data").digest("hex");
```
