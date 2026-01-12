# Wrangler Configuration

Configuration file reference for Cloudflare Workers.

## File Formats

| Format     | File                               |
| ---------- | ---------------------------------- |
| TOML       | `wrangler.toml`                    |
| JSON/JSONC | `wrangler.json` / `wrangler.jsonc` |

## Minimal Configuration

```jsonc
// wrangler.jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2025-03-07",
  "compatibility_flags": ["nodejs_compat"],
  "observability": {
    "enabled": true,
    "head_sampling_rate": 1
  }
}
```

```toml
# wrangler.toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2025-03-07"
compatibility_flags = ["nodejs_compat"]

[observability]
enabled = true
head_sampling_rate = 1
```

---

## Core Fields

| Field                 | Description                | Required |
| --------------------- | -------------------------- | -------- |
| `name`                | Worker name                | ✅       |
| `main`                | Entry point file           | ✅       |
| `compatibility_date`  | Runtime compatibility date | ✅       |
| `compatibility_flags` | Feature flags array        | Optional |
| `account_id`          | Cloudflare account ID      | Optional |

---

## Compatibility Settings

### Compatibility Date

Opt into runtime changes up to specified date:

```toml
compatibility_date = "2025-03-07"
```

> **Warning:** Omitting defaults to oldest date (2021-11-02).

### Compatibility Flags

```toml
compatibility_flags = [
  "nodejs_compat",
  "nodejs_compat_v2"
]
```

Key flags:

| Flag               | Description                            |
| ------------------ | -------------------------------------- |
| `nodejs_compat`    | Enable Node.js APIs                    |
| `nodejs_compat_v2` | Improved process implementation        |
| `rpc`              | Enable RPC for DO and Service Bindings |

---

## Bindings Configuration

### KV Namespaces

```toml
[[kv_namespaces]]
binding = "MY_KV"
id = "abc123def456"

# Preview namespace (optional)
[[kv_namespaces]]
binding = "MY_KV"
id = "abc123def456"
preview_id = "preview123"
```

### R2 Buckets

```toml
[[r2_buckets]]
binding = "MY_BUCKET"
bucket_name = "my-bucket"

# Remote during local dev
[[r2_buckets]]
binding = "PROD_BUCKET"
bucket_name = "prod-bucket"
remote = true
```

### D1 Databases

```toml
[[d1_databases]]
binding = "MY_DB"
database_name = "my-database"
database_id = "xyz789"
```

### Durable Objects

```toml
[[durable_objects.bindings]]
name = "MY_DO"
class_name = "Counter"

# External Durable Object
[[durable_objects.bindings]]
name = "EXTERNAL_DO"
class_name = "ExternalClass"
script_name = "other-worker"
```

### Migrations

```toml
[[migrations]]
tag = "v1"
new_classes = ["Counter"]

[[migrations]]
tag = "v2"
new_sqlite_classes = ["Agent"]
```

### Queues

```toml
# Producer
[[queues.producers]]
binding = "MY_QUEUE"
queue = "my-queue"

# Consumer
[[queues.consumers]]
queue = "my-queue"
max_batch_size = 10
max_batch_timeout = 30
max_retries = 3
dead_letter_queue = "my-dlq"
```

### Workers AI

```toml
[ai]
binding = "AI"
```

### Vectorize

```toml
[[vectorize]]
binding = "VECTORIZE"
index_name = "my-index"
```

### Service Bindings

```toml
[[services]]
binding = "AUTH"
service = "auth-worker"
environment = "production"
```

### Hyperdrive

```toml
[[hyperdrive]]
binding = "HYPERDRIVE"
id = "hyperdrive-config-id"
```

### Analytics Engine

```toml
[[analytics_engine_datasets]]
binding = "ANALYTICS"
dataset = "my-dataset"
```

---

## Static Assets

```toml
[assets]
directory = "./public"
binding = "ASSETS"
not_found_handling = "single-page-application"
```

### Options

| Option               | Values                                     | Description                      |
| -------------------- | ------------------------------------------ | -------------------------------- |
| `directory`          | Path                                       | Static files directory           |
| `binding`            | String                                     | Binding name in code             |
| `not_found_handling` | `"single-page-application"` / `"404-page"` | 404 behavior                     |
| `run_worker_first`   | `true` / patterns                          | When to run Worker before assets |

### Run Worker First Patterns

```toml
[assets]
directory = "./dist"
run_worker_first = ["/api/*", "!/api/docs/*"]
```

---

## Environment Variables

```toml
[vars]
API_URL = "https://api.example.com"
DEBUG = "false"
```

---

## Triggers (Cron)

```toml
[triggers]
crons = [
  "0 * * * *",      # Every hour
  "0 0 * * *",      # Daily at midnight
  "*/15 * * * *"    # Every 15 minutes
]
```

---

## Observability

```toml
[observability]
enabled = true
head_sampling_rate = 1
```

---

## Preview URLs

```toml
preview_urls = true
```

---

## Placement (Smart Placement)

```toml
[placement]
mode = "smart"
```

Routes requests to optimal locations based on backend latency.

---

## Environments

Override settings per environment:

```toml
# Default (production)
[vars]
API_URL = "https://api.example.com"

[[kv_namespaces]]
binding = "KV"
id = "prod-kv-id"

# Staging environment
[env.staging.vars]
API_URL = "https://staging-api.example.com"

[[env.staging.kv_namespaces]]
binding = "KV"
id = "staging-kv-id"
```

Deploy to environment:

```bash
npx wrangler deploy --env staging
```

---

## Full Example

```toml
name = "my-app"
main = "src/index.ts"
compatibility_date = "2025-03-07"
compatibility_flags = ["nodejs_compat"]

[observability]
enabled = true
head_sampling_rate = 1

[vars]
API_URL = "https://api.example.com"

[assets]
directory = "./public"
binding = "ASSETS"
not_found_handling = "single-page-application"

[[kv_namespaces]]
binding = "KV"
id = "abc123"

[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xyz789"

[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"

[[migrations]]
tag = "v1"
new_classes = ["Counter"]

[ai]
binding = "AI"

[[services]]
binding = "AUTH"
service = "auth-worker"

[triggers]
crons = ["0 * * * *"]

[placement]
mode = "smart"
```
