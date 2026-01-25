# Static Assets

Serve static files from Workers using Assets binding.

## Configuration

```toml
# wrangler.toml
[assets]
directory = "./public"
binding = "ASSETS"
not_found_handling = "single-page-application"
```

```jsonc
// wrangler.jsonc
{
  "assets": {
    "directory": "./dist",
    "binding": "ASSETS",
    "not_found_handling": "single-page-application"
  }
}
```

---

## Options

| Option               | Type          | Description                      |
| -------------------- | ------------- | -------------------------------- |
| `directory`          | String        | Path to static files             |
| `binding`            | String        | Binding name in code             |
| `not_found_handling` | String        | 404 behavior                     |
| `run_worker_first`   | Boolean/Array | When to run Worker before assets |

### not_found_handling Values

| Value                       | Behavior                           |
| --------------------------- | ---------------------------------- |
| `"single-page-application"` | Serve index.html for unknown paths |
| `"404-page"`                | Return 404 for unknown paths       |

---

## Basic Usage

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Serve static assets
    return env.ASSETS.fetch(request);
  },
};
```

---

## API Routes + Static Assets

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // API routes
    if (url.pathname.startsWith("/api/")) {
      return handleApi(request, env);
    }

    // Static assets for everything else
    return env.ASSETS.fetch(request);
  },
};

async function handleApi(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);

  if (url.pathname === "/api/hello") {
    return Response.json({ message: "Hello!" });
  }

  return new Response("Not Found", { status: 404 });
}
```

---

## Run Worker First

Control when Worker executes before serving assets.

### Always Run Worker

```toml
[assets]
directory = "./dist"
run_worker_first = true
```

### Pattern-Based

```toml
[assets]
directory = "./dist"
run_worker_first = ["/api/*", "!/api/docs/*"]
```

Patterns:

- `/api/*` — Run Worker for all /api/ paths
- `!/api/docs/*` — Except /api/docs/ paths

---

## Default Routing Behavior

Without `run_worker_first`:

1. Request comes in
2. Check if URL matches static asset
3. If match → serve asset (Worker not invoked)
4. If no match → invoke Worker

With `run_worker_first = true`:

1. Request comes in
2. Invoke Worker
3. Worker can call `env.ASSETS.fetch()` to serve assets

---

## SPA Configuration

For single-page applications:

```toml
[assets]
directory = "./dist"
binding = "ASSETS"
not_found_handling = "single-page-application"
```

All unknown paths serve `index.html`, allowing client-side routing.

---

## Headers for Static Assets

Add custom headers in Worker:

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const response = await env.ASSETS.fetch(request);

    // Clone response to modify headers
    const newResponse = new Response(response.body, response);
    newResponse.headers.set("X-Custom-Header", "value");

    return newResponse;
  },
};
```

### Cache Headers

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const response = await env.ASSETS.fetch(request);

    // Add cache headers for static assets
    if (url.pathname.startsWith("/static/")) {
      const newResponse = new Response(response.body, response);
      newResponse.headers.set("Cache-Control", "public, max-age=31536000, immutable");
      return newResponse;
    }

    return response;
  },
};
```

---

## Directory Structure

```
my-worker/
├── src/
│   └── index.ts
├── public/              # or dist/
│   ├── index.html
│   ├── favicon.ico
│   └── static/
│       ├── app.js
│       └── styles.css
├── wrangler.toml
└── package.json
```

---

## Build Integration

### Vite

```typescript
// vite.config.ts
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "dist",
  },
});
```

```toml
# wrangler.toml
[assets]
directory = "./dist"
```

### Custom Build

```json
// package.json
{
  "scripts": {
    "build": "your-build-command",
    "deploy": "npm run build && wrangler deploy"
  }
}
```

---

## Migration from Workers Sites

Workers Sites (legacy) uses `@cloudflare/kv-asset-handler`.

Modern approach uses Assets binding:

```diff
- import { getAssetFromKV } from "@cloudflare/kv-asset-handler";
-
- export default {
-   async fetch(request, env, ctx) {
-     return getAssetFromKV(request, env, ctx);
-   }
- };
+ export default {
+   async fetch(request: Request, env: Env): Promise<Response> {
+     return env.ASSETS.fetch(request);
+   }
+ };
```

Update wrangler.toml:

```diff
- [site]
- bucket = "./public"
+ [assets]
+ directory = "./public"
+ binding = "ASSETS"
```

---

## Limitations

- Assets are read-only
- No server-side includes
- Binary files supported
- Max file size: 25 MiB (same as Workers bundle)
