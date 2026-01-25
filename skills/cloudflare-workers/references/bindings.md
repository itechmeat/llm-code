# Bindings

Connect Workers to Cloudflare resources via `env` object.

## Binding Types

| Binding           | Type                     | Description           |
| ----------------- | ------------------------ | --------------------- |
| KV                | `KVNamespace`            | Key-value storage     |
| R2                | `R2Bucket`               | Object storage        |
| D1                | `D1Database`             | SQL database          |
| Durable Objects   | `DurableObjectNamespace` | Stateful coordination |
| Queues            | `Queue`                  | Message queues        |
| Workers AI        | `Ai`                     | ML inference          |
| Vectorize         | `VectorizeIndex`         | Vector database       |
| Service Binding   | `Fetcher`                | Call other Workers    |
| Static Assets     | `Fetcher`                | Serve static files    |
| Hyperdrive        | `Hyperdrive`             | DB connection pooling |
| Browser Rendering | `Fetcher`                | Headless browser      |
| Analytics Engine  | `AnalyticsEngineDataset` | Analytics             |

---

## KV Namespace

Low-latency key-value storage.

### Configuration

```toml
# wrangler.toml
[[kv_namespaces]]
binding = "MY_KV"
id = "abc123def456"
```

### Usage

```typescript
// Get value
const value = await env.MY_KV.get("key");
const json = await env.MY_KV.get("key", { type: "json" });
const buffer = await env.MY_KV.get("key", { type: "arrayBuffer" });

// Put value
await env.MY_KV.put("key", "value", {
  expirationTtl: 3600, // Seconds
  metadata: { created: Date.now() },
});

// Delete
await env.MY_KV.delete("key");

// List keys
const { keys, cursor, list_complete } = await env.MY_KV.list({
  prefix: "user:",
  limit: 100,
});
```

> For complete KV API, see: `cloudflare-kv` skill

---

## R2 Bucket

Object storage with S3-compatible API.

### Configuration

```toml
# wrangler.toml
[[r2_buckets]]
binding = "MY_BUCKET"
bucket_name = "my-bucket"
```

### Usage

```typescript
// Upload
await env.MY_BUCKET.put("file.txt", "content", {
  httpMetadata: { contentType: "text/plain" },
});

// Download
const object = await env.MY_BUCKET.get("file.txt");
if (object) {
  const text = await object.text();
  const contentType = object.httpMetadata?.contentType;
}

// Delete
await env.MY_BUCKET.delete("file.txt");

// List objects
const { objects, truncated, cursor } = await env.MY_BUCKET.list({
  prefix: "images/",
  limit: 100,
});
```

> For complete R2 API, see: `cloudflare-r2` skill

---

## D1 Database

Serverless SQL database.

### Configuration

```toml
# wrangler.toml
[[d1_databases]]
binding = "MY_DB"
database_name = "my-database"
database_id = "xyz789"
```

### Usage

```typescript
// Query
const { results } = await env.MY_DB.prepare("SELECT * FROM users WHERE id = ?").bind(userId).all();

// Insert
const result = await env.MY_DB.prepare("INSERT INTO users (name, email) VALUES (?, ?)").bind(name, email).run();

// Batch queries
const results = await env.MY_DB.batch([env.MY_DB.prepare("INSERT INTO logs (msg) VALUES (?)").bind("log1"), env.MY_DB.prepare("INSERT INTO logs (msg) VALUES (?)").bind("log2")]);
```

> For complete D1 API, see: `cloudflare-d1` skill

---

## Durable Objects

Stateful coordination and storage.

### Configuration

```toml
# wrangler.toml
[[durable_objects.bindings]]
name = "MY_DO"
class_name = "Counter"

[[migrations]]
tag = "v1"
new_classes = ["Counter"]
```

### Durable Object Class

```typescript
export class Counter implements DurableObject {
  private count: number = 0;

  constructor(private state: DurableObjectState, private env: Env) {}

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/increment") {
      this.count++;
      await this.state.storage.put("count", this.count);
    }

    return new Response(String(this.count));
  }
}
```

### Usage

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const id = env.MY_DO.idFromName("global-counter");
    const stub = env.MY_DO.get(id);
    return stub.fetch(request);
  },
};
```

> For complete DO API, see: `cloudflare-durable-objects` skill

---

## Queues

Message queue for async processing.

### Configuration

```toml
# wrangler.toml

# Producer
[[queues.producers]]
binding = "MY_QUEUE"
queue = "my-queue"

# Consumer
[[queues.consumers]]
queue = "my-queue"
max_batch_size = 10
max_batch_timeout = 30
```

### Producer

```typescript
await env.MY_QUEUE.send({
  type: "process",
  data: { userId: 123 },
});

// Send batch
await env.MY_QUEUE.sendBatch([{ body: { type: "a" } }, { body: { type: "b" } }]);
```

### Consumer

```typescript
export default {
  async queue(batch: MessageBatch, env: Env) {
    for (const message of batch.messages) {
      await processMessage(message.body);
      message.ack();
    }
  },
};
```

---

## Workers AI

ML inference on Cloudflare's network.

### Configuration

```toml
# wrangler.toml
[ai]
binding = "AI"
```

### Usage

```typescript
// Text generation
const response = await env.AI.run("@cf/meta/llama-3-8b-instruct", {
  messages: [{ role: "user", content: "Hello!" }],
});

// Text embedding
const embeddings = await env.AI.run("@cf/baai/bge-base-en-v1.5", {
  text: ["Hello world", "Another text"],
});

// Image classification
const result = await env.AI.run("@cf/microsoft/resnet-50", {
  image: imageArrayBuffer,
});
```

> **Note:** Workers AI does not work locally — always uses remote API.

---

## Service Binding

Call other Workers directly.

### Configuration

```toml
# wrangler.toml
[[services]]
binding = "AUTH_SERVICE"
service = "auth-worker"
```

### Usage

```typescript
const response = await env.AUTH_SERVICE.fetch(
  new Request("https://auth/verify", {
    method: "POST",
    body: JSON.stringify({ token }),
  })
);
```

---

## Static Assets

Serve static files from Worker.

### Configuration

```toml
# wrangler.toml
[assets]
directory = "./public"
binding = "ASSETS"
not_found_handling = "single-page-application"
```

### Usage

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/api/")) {
      return handleApi(request, env);
    }

    return env.ASSETS.fetch(request);
  },
};
```

---

## Vectorize

Vector database for semantic search.

### Configuration

```toml
# wrangler.toml
[[vectorize]]
binding = "VECTORIZE"
index_name = "my-index"
```

### Usage

```typescript
// Insert vectors
await env.VECTORIZE.insert([
  { id: "1", values: [0.1, 0.2, ...], metadata: { title: "Doc 1" } }
]);

// Query
const results = await env.VECTORIZE.query(queryVector, {
  topK: 10,
  returnMetadata: true
});
```

---

## Hyperdrive

Connection pooling for external databases.

### Configuration

```toml
# wrangler.toml
[[hyperdrive]]
binding = "HYPERDRIVE"
id = "hyperdrive-id"
```

### Usage

```typescript
import { Client } from "pg";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const client = new Client({
      connectionString: env.HYPERDRIVE.connectionString,
    });

    await client.connect();
    const result = await client.query("SELECT * FROM users");
    await client.end();

    return Response.json(result.rows);
  },
};
```

> Requires `nodejs_compat` compatibility flag.

---

## Environment Variables & Secrets

### Configuration

```toml
# wrangler.toml
[vars]
API_URL = "https://api.example.com"
DEBUG = "false"
```

### Secrets (CLI)

```bash
npx wrangler secret put API_KEY
```

### Usage

```typescript
const apiUrl = env.API_URL;
const apiKey = env.API_KEY; // Secret
```

---

## Local Development

### Remote Bindings

Connect to deployed resources during local dev:

```toml
# wrangler.toml
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "prod-bucket"
remote = true
```

### Unsupported Remote Bindings

Cannot use `remote: true`:

- Durable Objects
- Workflows
- Environment variables
- Secrets
- Static assets
- Analytics Engine
- Hyperdrive

### Add Local Data

```bash
# KV
npx wrangler kv key put "key" "value" --binding=MY_KV --local

# R2
npx wrangler r2 object put bucket/file.txt --file=./local.txt --local

# D1
npx wrangler d1 execute MY_DB --file=./schema.sql --local
```
