# R2 Binding Configuration

## wrangler.jsonc

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2024-01-01",
  "r2_buckets": [
    {
      "binding": "MY_BUCKET",
      "bucket_name": "my-bucket"
    }
  ]
}
```

## wrangler.toml (alternative)

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[[r2_buckets]]
binding = "MY_BUCKET"
bucket_name = "my-bucket"
```

## Configuration Fields

| Field                 | Required | Description                                    |
| --------------------- | -------- | ---------------------------------------------- |
| `binding`             | Yes      | Variable name in `env` (e.g., `env.MY_BUCKET`) |
| `bucket_name`         | Yes      | Bucket name in Cloudflare                      |
| `preview_bucket_name` | No       | Bucket for local dev/preview                   |
| `jurisdiction`        | No       | Data location restriction (`eu`)               |

## TypeScript Interface

```typescript
export interface Env {
  MY_BUCKET: R2Bucket;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const object = await env.MY_BUCKET.get("file.txt");
    if (!object) return new Response("Not Found", { status: 404 });
    return new Response(object.body);
  },
};
```

## Multiple Buckets

```jsonc
{
  "r2_buckets": [
    {
      "binding": "UPLOADS",
      "bucket_name": "user-uploads"
    },
    {
      "binding": "ASSETS",
      "bucket_name": "static-assets"
    }
  ]
}
```

## Preview Bucket (local development)

```jsonc
{
  "r2_buckets": [
    {
      "binding": "MY_BUCKET",
      "bucket_name": "production-bucket",
      "preview_bucket_name": "dev-bucket"
    }
  ]
}
```

`preview_bucket_name` is used during:

- `wrangler dev` without `--remote`
- `wrangler pages dev`

## Jurisdiction (GDPR compliance)

```jsonc
{
  "r2_buckets": [
    {
      "binding": "EU_BUCKET",
      "bucket_name": "eu-data",
      "jurisdiction": "eu"
    }
  ]
}
```

Restricts data storage to EU region.

## Pages Functions Binding

In Cloudflare Dashboard:

1. Workers & Pages → Your Project
2. Settings → Functions
3. R2 bucket bindings → Add binding

Or via `wrangler pages dev`:

```bash
wrangler pages dev --r2 MY_BUCKET=bucket-name
```

## Bucket Name Rules

- Lowercase letters (a-z), numbers (0-9), hyphens (-)
- Cannot start or end with hyphen
- Length: 3-63 characters

## Get Bucket Info

```bash
npx wrangler r2 bucket info my-bucket
```

Output:

```
Name: my-bucket
Created: 2024-01-15T10:30:00.000Z
Location: auto
```
