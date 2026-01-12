# Pages Functions

Server-side code running on Cloudflare Workers runtime.

## Getting Started

Create a `/functions` directory at project root:

```
my-project/
├── public/          # Static assets
├── functions/       # Server-side code
│   ├── index.js
│   └── api/
│       └── hello.js
└── package.json
```

## File-Based Routing

| File Path                 | URL          |
| ------------------------- | ------------ |
| `/functions/index.js`     | `/`          |
| `/functions/about.js`     | `/about`     |
| `/functions/api/users.js` | `/api/users` |

### Dynamic Routes

**Single segment** (`[param]`):

```
/functions/users/[id].js → /users/123
```

```javascript
export function onRequest(context) {
  const { id } = context.params; // "123"
  return new Response(`User: ${id}`);
}
```

**Catch-all** (`[[catchall]]`):

```
/functions/files/[[path]].js → /files/a/b/c
```

```javascript
export function onRequest(context) {
  const segments = context.params.path; // ["a", "b", "c"]
  return new Response(`Path: ${segments.join("/")}`);
}
```

---

## Handlers

### Generic Handler

```javascript
export function onRequest(context) {
  return new Response("Handles all methods");
}
```

### Method-Specific Handlers

```javascript
export function onRequestGet(context) {
  return new Response("GET only");
}

export function onRequestPost(context) {
  return new Response("POST only");
}

export function onRequestPut(context) {
  /* ... */
}
export function onRequestDelete(context) {
  /* ... */
}
export function onRequestPatch(context) {
  /* ... */
}
export function onRequestHead(context) {
  /* ... */
}
export function onRequestOptions(context) {
  /* ... */
}
```

---

## Event Context

```typescript
interface EventContext<Env, Params, Data> {
  request: Request; // Incoming request
  functionPath: string; // Matched function path
  env: Env; // Bindings (KV, R2, D1, etc.)
  params: Params; // Route parameters
  data: Data; // Shared data from middleware
  waitUntil(promise: Promise<any>): void; // Background work
  passThroughOnException(): void; // Fall through on error
  next(input?: Request | string, init?: RequestInit): Promise<Response>;
}
```

---

## Middleware

Create `_middleware.js` in any functions directory:

```javascript
// functions/_middleware.js
export async function onRequest(context) {
  // Before handler
  console.log("Request:", context.request.url);

  // Call next handler
  const response = await context.next();

  // After handler
  response.headers.set("X-Custom-Header", "value");
  return response;
}
```

### Middleware Chain

Export array for multiple middleware:

```javascript
async function auth(context) {
  // Check auth
  return context.next();
}

async function logging(context) {
  console.log(context.request.url);
  return context.next();
}

export const onRequest = [auth, logging];
```

### Middleware Scope

- `functions/_middleware.js` — Applies to all routes
- `functions/api/_middleware.js` — Applies to `/api/*` routes

---

## TypeScript

### Setup

```bash
npx wrangler types
```

Creates `worker-configuration.d.ts` with Env types.

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2021",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "types": ["@cloudflare/workers-types"]
  },
  "include": ["functions/**/*"]
}
```

### Typed Handler

```typescript
// functions/api/users.ts
interface Env {
  MY_KV: KVNamespace;
  MY_DB: D1Database;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const data = await context.env.MY_KV.get("key");
  return new Response(data);
};
```

---

## Invocation Control (\_routes.json)

Control when Functions are invoked to reduce charges:

```json
{
  "version": 1,
  "include": ["/api/*", "/admin/*"],
  "exclude": ["/static/*", "/*.ico"]
}
```

Place in build output directory (e.g., `dist/_routes.json`).

### Evaluation Order

1. Check excludes first
2. Then check includes
3. If matched → invoke Function
4. If not matched → serve static asset (no Function charge)

---

## Advanced Mode (\_worker.js)

Take full control with single Worker file:

```javascript
// dist/_worker.js
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/api/")) {
      return new Response(JSON.stringify({ ok: true }), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // Serve static assets
    return env.ASSETS.fetch(request);
  },
};
```

> Advanced mode disables file-based routing.

---

## Module Support

### ES Modules

```javascript
import { helper } from "./utils.js";
```

### WebAssembly

```javascript
import wasm from "./module.wasm";
const instance = await WebAssembly.instantiate(wasm);
```

### Text/Binary

```javascript
import text from "./data.txt";
import binary from "./file.bin";
```

---

## Debugging

### Wrangler Tail

```bash
wrangler pages deployment tail
```

### Console Logging

```javascript
export function onRequest(context) {
  console.log("Request URL:", context.request.url);
  console.log("Headers:", Object.fromEntries(context.request.headers));
  return new Response("OK");
}
```

### Source Maps

```bash
npx wrangler pages deploy --upload-source-maps
```

Or in `wrangler.toml`:

```toml
upload_source_maps = true
```

---

## Pricing

- Functions requests billed as Workers requests
- Static asset requests (not invoking Functions) are free
- Use `_routes.json` to optimize costs
