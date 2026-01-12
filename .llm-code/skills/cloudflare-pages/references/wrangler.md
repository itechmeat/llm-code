# Wrangler CLI for Pages

Command-line interface for Pages development and deployment.

## Installation

```bash
npm install -g wrangler
# or
npm install --save-dev wrangler
```

## Project Commands

### Create Project

```bash
npx wrangler pages project create <project-name>
```

### List Projects

```bash
npx wrangler pages project list
```

### Delete Project

```bash
npx wrangler pages project delete <project-name>
```

---

## Deployment Commands

### Deploy

```bash
# Deploy to production
npx wrangler pages deploy <build-output-dir>

# Deploy to branch (preview)
npx wrangler pages deploy <build-output-dir> --branch=staging

# With commit message
npx wrangler pages deploy <build-output-dir> --commit-message="Deploy v1.2.3"
```

### List Deployments

```bash
npx wrangler pages deployment list
```

### Tail Logs

```bash
npx wrangler pages deployment tail
```

---

## Local Development

### Start Dev Server

```bash
npx wrangler pages dev <build-output-dir>
```

Default: `http://localhost:8788`

### Options

| Flag                     | Description             |
| ------------------------ | ----------------------- |
| `--port`                 | Custom port             |
| `--local-protocol=https` | Use HTTPS               |
| `--compatibility-date`   | Set compatibility date  |
| `--compatibility-flags`  | Set compatibility flags |

### With Bindings

```bash
npx wrangler pages dev ./dist \
  --kv=MY_KV \
  --r2=MY_BUCKET \
  --d1=MY_DB=<database-id> \
  --service=AUTH=auth-worker \
  --ai=AI \
  --do=COUNTER=CounterClass@counter-worker \
  --binding=API_URL=https://api.example.com
```

### Keyboard Shortcuts

| Key | Action        |
| --- | ------------- |
| `b` | Open browser  |
| `d` | Open DevTools |
| `c` | Clear console |
| `x` | Exit          |

---

## Wrangler Configuration

### Minimal wrangler.jsonc

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-pages-app",
  "pages_build_output_dir": "./dist",
  "compatibility_date": "2024-01-01"
}
```

### Full Configuration

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-pages-app",
  "pages_build_output_dir": "./dist",
  "compatibility_date": "2024-01-01",
  "compatibility_flags": ["nodejs_compat"],

  "kv_namespaces": [{ "binding": "KV", "id": "abc123" }],

  "r2_buckets": [{ "binding": "BUCKET", "bucket_name": "my-bucket" }],

  "d1_databases": [{ "binding": "DB", "database_name": "my-db", "database_id": "xyz789" }],

  "services": [{ "binding": "AUTH", "service": "auth-worker" }],

  "durable_objects": {
    "bindings": [{ "name": "COUNTER", "class_name": "Counter", "script_name": "counter-worker" }]
  },

  "queues": {
    "producers": [{ "binding": "QUEUE", "queue": "my-queue" }]
  },

  "ai": { "binding": "AI" },

  "vectorize": [{ "binding": "VECTORIZE", "index_name": "my-index" }],

  "analytics_engine_datasets": [{ "binding": "ANALYTICS", "dataset": "my-dataset" }],

  "vars": {
    "API_URL": "https://api.example.com",
    "DEBUG": "false"
  },

  "upload_source_maps": true
}
```

### Environment Overrides

```jsonc
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

---

## Download Existing Config

Generate `wrangler.toml` from existing dashboard configuration:

```bash
npx wrangler pages download config <project-name>
```

---

## Type Generation

Generate TypeScript types for bindings:

```bash
npx wrangler types
```

Creates `worker-configuration.d.ts`:

```typescript
interface Env {
  MY_KV: KVNamespace;
  MY_BUCKET: R2Bucket;
  MY_DB: D1Database;
  AI: Ai;
  API_URL: string;
}
```

---

## Source Maps

Upload source maps for debugging:

```bash
npx wrangler pages deploy --upload-source-maps
```

Or in configuration:

```jsonc
{
  "upload_source_maps": true
}
```

Requires Wrangler >= 3.60.0

---

## Requirements

| Feature              | Requirement         |
| -------------------- | ------------------- |
| Wrangler config file | Wrangler >= 3.45.0  |
| V2 build system      | For Wrangler config |
| Source maps          | Wrangler >= 3.60.0  |

---

## Wrangler vs Dashboard

When using Wrangler configuration:

| Setting               | Source of Truth |
| --------------------- | --------------- |
| Bindings              | Wrangler file   |
| Environment variables | Wrangler file   |
| Build settings        | Dashboard       |
| Git integration       | Dashboard       |
| Custom domains        | Dashboard       |

> **Important:** Do not edit bindings in dashboard when using Wrangler file — changes may be overwritten.

---

## Common Issues

| Issue                      | Solution                                         |
| -------------------------- | ------------------------------------------------ |
| "Project not found"        | Create project first with `pages project create` |
| Local bindings not working | Add binding flags to `pages dev`                 |
| Types not generated        | Run `wrangler types` after adding bindings       |
| Deploy fails               | Check build output directory exists              |
