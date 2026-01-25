# Cloudflare Pages Skill

Agent skill for deploying and managing full-stack applications on Cloudflare Pages.

## Overview

Cloudflare Pages is a platform for deploying static sites and full-stack applications to Cloudflare's global network. It supports Git-based deployments, Direct Upload, and serverless functions.

## Skill Contents

### Core Documentation

- [SKILL.md](SKILL.md) — Main skill file with quick navigation and essential recipes

### References

| File                                                    | Topic                                                      |
| ------------------------------------------------------- | ---------------------------------------------------------- |
| [deployment.md](references/deployment.md)               | Git integration, Direct Upload, C3 CLI, rollbacks          |
| [build.md](references/build.md)                         | Build commands, framework presets, env vars, caching       |
| [functions.md](references/functions.md)                 | Pages Functions, routing, handlers, middleware, TypeScript |
| [bindings.md](references/bindings.md)                   | KV, R2, D1, Workers AI, Durable Objects, Queues            |
| [headers-redirects.md](references/headers-redirects.md) | \_headers, \_redirects files, proxying, Early Hints        |
| [domains.md](references/domains.md)                     | Custom domains, DNS, SSL, caching                          |
| [wrangler.md](references/wrangler.md)                   | Wrangler CLI, local development, configuration             |

## Key Features

- **Git Integration** — Automatic deployments from GitHub/GitLab
- **Direct Upload** — Deploy prebuilt assets via CLI or dashboard
- **Preview Deployments** — Automatic preview URLs for branches/PRs
- **Pages Functions** — Serverless functions with file-based routing
- **Bindings** — Connect to KV, R2, D1, Workers AI, and more
- **Custom Domains** — Configure apex and subdomain routing
- **Headers/Redirects** — Static configuration files

## Quick Start

```bash
# Create and deploy a new project
npm create cloudflare@latest -- --platform=pages

# Or deploy existing build
npx wrangler pages project create my-app
npx wrangler pages deploy ./dist
```

## Related Skills

This skill focuses exclusively on Cloudflare Pages. For other Cloudflare products:

- `cloudflare-workers` — Worker runtime and APIs
- `cloudflare-d1` — D1 SQL database
- `cloudflare-r2` — R2 object storage
- `cloudflare-kv` — KV key-value storage

## Links

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Pages Functions](https://developers.cloudflare.com/pages/functions/)
- [Framework Guides](https://developers.cloudflare.com/pages/framework-guides/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
