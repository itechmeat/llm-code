# Local Development

Develop and test Workers locally using Miniflare.

## Dev Servers

### Wrangler

```bash
npx wrangler dev
```

Default: `http://localhost:8787`

### Vite Plugin

```bash
npx vite dev
```

Uses `@cloudflare/vite-plugin` for Vite integration.

---

## Wrangler Dev Options

| Flag                     | Description                        |
| ------------------------ | ---------------------------------- |
| `--port`                 | Custom port                        |
| `--local-protocol=https` | Use HTTPS                          |
| `--remote`               | Run code on Cloudflare (not local) |
| `--persist-to <dir>`     | Custom state directory             |
| `--test-scheduled`       | Enable cron testing                |

### Examples

```bash
# Custom port
npx wrangler dev --port 3000

# HTTPS
npx wrangler dev --local-protocol=https

# Remote execution
npx wrangler dev --remote

# Custom state directory
npx wrangler dev --persist-to ./my-state
```

---

## Keyboard Shortcuts

| Key | Action        |
| --- | ------------- |
| `b` | Open browser  |
| `d` | Open DevTools |
| `c` | Clear console |
| `x` | Exit          |

---

## Bindings Behavior

### Default (Local Simulation)

All bindings simulated locally by Miniflare:

| Binding         | Local Behavior         |
| --------------- | ---------------------- |
| KV              | In-memory or persisted |
| R2              | Local file system      |
| D1              | Local SQLite           |
| Durable Objects | Local simulation       |
| Queues          | Local simulation       |
| Static Assets   | Local files            |

### Remote Bindings

Connect to deployed resources:

```toml
# wrangler.toml
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "prod-bucket"
remote = true

[ai]
binding = "AI"
remote = true  # Required for AI
```

### Always Remote

These bindings always connect remotely:

- Workers AI
- Vectorize
- Browser Rendering

### Cannot Be Remote

These bindings cannot use `remote: true`:

- Durable Objects
- Workflows
- Environment variables
- Secrets
- Static assets
- Analytics Engine
- Hyperdrive

---

## State Persistence

### Default Directory

```
.wrangler/state/
```

### Custom Directory

```bash
npx wrangler dev --persist-to ./my-state
```

### Vite Plugin

```typescript
// vite.config.ts
import { cloudflare } from "@cloudflare/vite-plugin";

export default {
  plugins: [
    cloudflare({
      persistState: "./my-state",
    }),
  ],
};
```

---

## Adding Local Data

Populate simulated bindings with test data.

### KV

```bash
# Single key
npx wrangler kv key put "user:1" '{"name":"Alice"}' \
  --binding=MY_KV --local

# Bulk import
npx wrangler kv bulk put ./data.json --binding=MY_KV --local
```

data.json:

```json
[
  { "key": "user:1", "value": "{\"name\":\"Alice\"}" },
  { "key": "user:2", "value": "{\"name\":\"Bob\"}" }
]
```

### R2

```bash
npx wrangler r2 object put my-bucket/file.txt \
  --file=./local-file.txt --local
```

### D1

```bash
# Execute SQL file
npx wrangler d1 execute MY_DB --file=./schema.sql --local

# Execute command
npx wrangler d1 execute MY_DB \
  --command="INSERT INTO users (name) VALUES ('Alice')" --local
```

---

## Testing Scheduled Handlers

### Enable Testing

```bash
npx wrangler dev --test-scheduled
```

### Trigger Cron

```bash
curl http://localhost:8787/__scheduled
```

Or visit `http://localhost:8787/__scheduled` in browser.

---

## Remote Development

Run code on Cloudflare's network (not locally):

```bash
npx wrangler dev --remote
```

Behavior:

- Code executes on Cloudflare edge
- All bindings connect to deployed resources
- Useful for testing production-like behavior

> **Note:** Vite plugin does not support `--remote`.

---

## Environment Variables (Local)

### .dev.vars File

```bash
# .dev.vars (do not commit!)
API_KEY=secret123
DATABASE_URL=postgres://localhost/db
```

Loaded automatically during `wrangler dev`.

### Command Line

```bash
API_KEY=secret npx wrangler dev
```

---

## Debugging

### Console Logs

```typescript
console.log("Debug info:", data);
console.error("Error:", error);
```

Visible in terminal running `wrangler dev`.

### Source Maps

Enabled by default for TypeScript.

### DevTools

Press `d` during `wrangler dev` to open Chrome DevTools.

---

## Common Issues

| Issue                | Solution                          |
| -------------------- | --------------------------------- |
| Port in use          | Use `--port` flag                 |
| Bindings not working | Check wrangler.toml config        |
| State not persisting | Check `--persist-to` flag         |
| AI not working       | Add `remote = true` to ai binding |
| Types missing        | Run `npx wrangler types`          |
