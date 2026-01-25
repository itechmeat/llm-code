# Pages Functions Bindings

Connect Functions to Cloudflare resources via `context.env`.

## Supported Bindings

| Binding               | Type                     | Local Dev Support |
| --------------------- | ------------------------ | ----------------- |
| KV Namespace          | `KVNamespace`            | ✅                |
| R2 Bucket             | `R2Bucket`               | ✅                |
| D1 Database           | `D1Database`             | ✅                |
| Durable Objects       | `DurableObjectNamespace` | ✅                |
| Service Binding       | `Fetcher`                | ✅                |
| Queues Producer       | `Queue`                  | ✅                |
| Workers AI            | `Ai`                     | ❌ Remote only    |
| Vectorize             | `VectorizeIndex`         | ❌ Remote only    |
| Analytics Engine      | `AnalyticsEngineDataset` | ❌                |
| Hyperdrive            | `Hyperdrive`             | ❌                |
| Environment Variables | `string`                 | ✅                |
| Secrets               | `string`                 | ✅                |

---

## Configuration Methods

### Dashboard

1. Workers & Pages > Project > Settings > Bindings
2. Add binding (select type, provide name/ID)
3. Redeploy for changes to take effect

### Wrangler Configuration

```jsonc
// wrangler.jsonc
{
  "name": "my-pages-app",
  "pages_build_output_dir": "./dist",
  "compatibility_date": "2024-01-01",

  "kv_namespaces": [{ "binding": "MY_KV", "id": "abc123" }],

  "r2_buckets": [{ "binding": "MY_BUCKET", "bucket_name": "my-bucket" }],

  "d1_databases": [{ "binding": "MY_DB", "database_name": "my-db", "database_id": "xyz789" }],

  "services": [{ "binding": "AUTH_SERVICE", "service": "auth-worker" }],

  "ai": { "binding": "AI" },

  "vars": {
    "API_URL": "https://api.example.com",
    "DEBUG": "false"
  }
}
```

---

## Local Development

### Wrangler CLI Flags

```bash
npx wrangler pages dev ./dist \
  --kv=MY_KV \
  --r2=MY_BUCKET \
  --d1=MY_DB=<database-id> \
  --service=AUTH_SERVICE=auth-worker \
  --ai=AI \
  --binding=API_URL=https://api.example.com
```

### Local Secrets (.dev.vars)

```bash
# .dev.vars (do not commit!)
API_SECRET=secret123
DATABASE_URL=postgres://localhost/db
```

---

## Usage Examples

### KV Namespace

```javascript
export async function onRequestGet(context) {
  // Read
  const value = await context.env.MY_KV.get("key");
  const json = await context.env.MY_KV.get("key", { type: "json" });

  // Write
  await context.env.MY_KV.put("key", "value", {
    expirationTtl: 3600,
    metadata: { created: Date.now() },
  });

  // Delete
  await context.env.MY_KV.delete("key");

  // List
  const { keys } = await context.env.MY_KV.list({ prefix: "user:" });

  return new Response(JSON.stringify(keys));
}
```

> For complete KV API, see: `cloudflare-kv` skill

### R2 Bucket

```javascript
export async function onRequest(context) {
  // Upload
  await context.env.MY_BUCKET.put("file.txt", "content", {
    httpMetadata: { contentType: "text/plain" },
  });

  // Download
  const object = await context.env.MY_BUCKET.get("file.txt");
  if (!object) {
    return new Response("Not found", { status: 404 });
  }

  return new Response(object.body, {
    headers: {
      "Content-Type": object.httpMetadata?.contentType || "application/octet-stream",
    },
  });
}
```

> For complete R2 API, see: `cloudflare-r2` skill

### D1 Database

```javascript
export async function onRequestGet(context) {
  const { results } = await context.env.MY_DB.prepare("SELECT * FROM users WHERE id = ?").bind(context.params.id).all();

  return Response.json(results);
}

export async function onRequestPost(context) {
  const body = await context.request.json();

  const result = await context.env.MY_DB.prepare("INSERT INTO users (name, email) VALUES (?, ?)").bind(body.name, body.email).run();

  return Response.json({ id: result.meta.last_row_id });
}
```

> For complete D1 API, see: `cloudflare-d1` skill

### Workers AI

```javascript
export async function onRequestPost(context) {
  const body = await context.request.json();

  const response = await context.env.AI.run("@cf/meta/llama-3-8b-instruct", {
    messages: [{ role: "user", content: body.prompt }],
  });

  return Response.json(response);
}
```

> **Note:** Workers AI does not work locally — always uses remote API (incurs charges).

### Service Binding

```javascript
export async function onRequest(context) {
  // Call another Worker
  const authResponse = await context.env.AUTH_SERVICE.fetch(
    new Request("https://auth/verify", {
      headers: { Authorization: context.request.headers.get("Authorization") },
    })
  );

  if (!authResponse.ok) {
    return new Response("Unauthorized", { status: 401 });
  }

  return new Response("Protected content");
}
```

### Durable Objects

```javascript
export async function onRequest(context) {
  const id = context.env.COUNTER.idFromName("global");
  const stub = context.env.COUNTER.get(id);

  const response = await stub.fetch(context.request);
  return response;
}
```

> Durable Objects must be defined in a separate Worker and bound to Pages project.

### Queues Producer

```javascript
export async function onRequestPost(context) {
  const body = await context.request.json();

  await context.env.MY_QUEUE.send({
    type: "process",
    data: body,
  });

  return new Response("Queued", { status: 202 });
}
```

### Vectorize

```javascript
export async function onRequestPost(context) {
  const body = await context.request.json();

  // Query similar vectors
  const results = await context.env.VECTORIZE_INDEX.query(body.vector, {
    topK: 5,
    returnMetadata: true,
  });

  return Response.json(results);
}
```

### Environment Variables

```javascript
export function onRequest(context) {
  const apiUrl = context.env.API_URL;
  const debug = context.env.DEBUG === "true";

  return new Response(`API: ${apiUrl}, Debug: ${debug}`);
}
```

---

## Binding Environments

Configure different bindings for preview vs production:

```jsonc
// wrangler.jsonc
{
  "name": "my-app",
  "pages_build_output_dir": "./dist",

  "d1_databases": [{ "binding": "DB", "database_name": "prod-db", "database_id": "prod-id" }],

  "env": {
    "preview": {
      "d1_databases": [{ "binding": "DB", "database_name": "dev-db", "database_id": "dev-id" }]
    }
  }
}
```

> **Important:** When overriding any non-inheritable key in `env.preview` or `env.production`, you must specify ALL non-inheritable keys in that block.
