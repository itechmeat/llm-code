# Cloudflare Workers Skill

Agent skill for building serverless applications on Cloudflare Workers.

## Overview

Cloudflare Workers is a serverless platform for running JavaScript/TypeScript code at the edge. Workers execute on Cloudflare's global network, providing low-latency responses worldwide.

## Skill Contents

### Core Documentation

- [SKILL.md](SKILL.md) — Main skill file with quick navigation and essential recipes

### References

| File                                    | Topic                                                   |
| --------------------------------------- | ------------------------------------------------------- |
| [runtime.md](references/runtime.md)     | Handlers (fetch, scheduled, queue, email), runtime APIs |
| [bindings.md](references/bindings.md)   | KV, R2, D1, Durable Objects, Queues, AI, Vectorize      |
| [wrangler.md](references/wrangler.md)   | wrangler.toml/jsonc configuration reference             |
| [local-dev.md](references/local-dev.md) | Local development with Miniflare, remote bindings       |
| [assets.md](references/assets.md)       | Static assets configuration and routing                 |
| [testing.md](references/testing.md)     | Testing with Vitest integration and Miniflare           |

## Key Features

- **Edge Execution** — Code runs on Cloudflare's global network
- **Multiple Handlers** — fetch, scheduled (cron), queue, email
- **Rich Bindings** — KV, R2, D1, Durable Objects, Queues, AI, Vectorize
- **Static Assets** — Serve files alongside serverless functions
- **Local Development** — Full simulation with Miniflare
- **TypeScript** — First-class support
- **Testing** — Vitest integration for Workers runtime

## Quick Start

```bash
# Create new Worker
npm create cloudflare@latest

# Or manually
mkdir my-worker && cd my-worker
npm init -y
npm install -D wrangler typescript @cloudflare/workers-types

# Create wrangler.toml
cat > wrangler.toml << EOF
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2025-03-07"
compatibility_flags = ["nodejs_compat"]
EOF

# Create entry point
mkdir src
cat > src/index.ts << EOF
export default {
  async fetch(request: Request): Promise<Response> {
    return new Response("Hello, World!");
  }
};
EOF

# Develop locally
npx wrangler dev

# Deploy
npx wrangler deploy
```

## Related Skills

This skill focuses exclusively on Cloudflare Workers. For other Cloudflare products:

- `cloudflare-pages` — Full-stack hosting with Git deployment
- `cloudflare-d1` — D1 SQL database
- `cloudflare-r2` — R2 object storage
- `cloudflare-kv` — KV key-value storage
- `cloudflare-durable-objects` — Stateful coordination

## Links

- [Workers Documentation](https://developers.cloudflare.com/workers/)
- [Runtime APIs](https://developers.cloudflare.com/workers/runtime-apis/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
- [Examples](https://developers.cloudflare.com/workers/examples/)
