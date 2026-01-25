# KV Binding Configuration

## wrangler.jsonc

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2024-01-01",
  "kv_namespaces": [
    {
      "binding": "MY_KV",
      "id": "06779da6940b431db6e566b4846d64db"
    }
  ]
}
```

## wrangler.toml (alternative)

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[[kv_namespaces]]
binding = "MY_KV"
id = "06779da6940b431db6e566b4846d64db"
```

## Configuration Fields

| Field        | Required | Description                                          |
| ------------ | -------- | ---------------------------------------------------- |
| `binding`    | Yes      | Variable name in `env` (e.g., `env.MY_KV`)           |
| `id`         | Yes      | Namespace UUID (from `wrangler kv namespace create`) |
| `preview_id` | No       | Namespace UUID for local dev/preview                 |

## TypeScript Interface

```typescript
export interface Env {
  MY_KV: KVNamespace;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const value = await env.MY_KV.get("key");
    return new Response(value);
  },
};
```

## Get Namespace ID

```bash
# During creation
npx wrangler kv namespace create MY_KV
# Output: Created namespace "MY_KV" with ID "06779da6..."

# List existing namespaces
npx wrangler kv namespace list
```

## Multiple Namespaces

```jsonc
{
  "kv_namespaces": [
    {
      "binding": "USERS",
      "id": "users-namespace-uuid"
    },
    {
      "binding": "CACHE",
      "id": "cache-namespace-uuid"
    }
  ]
}
```

## Preview Namespace (for local dev)

```jsonc
{
  "kv_namespaces": [
    {
      "binding": "MY_KV",
      "id": "production-uuid",
      "preview_id": "preview-uuid"
    }
  ]
}
```

`preview_id` is used during:

- `wrangler dev` without `--remote`
- `wrangler pages dev`

Create preview namespace:

```bash
npx wrangler kv namespace create MY_KV --preview
```

## Remote Binding (use prod in local dev)

```jsonc
{
  "kv_namespaces": [
    {
      "binding": "MY_KV",
      "id": "production-uuid",
      "remote": true
    }
  ]
}
```

Or via CLI:

```bash
wrangler dev --remote
```

**Caution**: `remote: true` works with production data.

## Pages Functions Binding

In Cloudflare Dashboard:

1. Workers & Pages → Your Project
2. Settings → Functions
3. KV namespace bindings → Add binding

Or via `wrangler pages dev`:

```bash
wrangler pages dev --kv MY_KV=namespace-uuid
```

## Durable Objects Access

KV is accessible from Durable Objects:

```typescript
import { DurableObject } from "cloudflare:workers";

export class MyDO extends DurableObject {
  async fetch(request: Request): Promise<Response> {
    const value = await this.env.MY_KV.get("key");
    return new Response(value);
  }
}
```

## Naming Rules

Binding names must be valid JavaScript identifiers:

- Start with letter or underscore
- Contain only letters, numbers, underscores
- Cannot be JavaScript reserved words

```jsonc
// Good
"binding": "MY_KV"
"binding": "userCache"
"binding": "_private"

// Bad
"binding": "my-kv"      // Hyphens not allowed
"binding": "123abc"     // Cannot start with number
"binding": "class"      // Reserved word
```
