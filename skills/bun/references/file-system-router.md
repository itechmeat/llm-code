# File System Router

Fast file-based route resolution API (primarily for framework authors).

## Basic Usage

```typescript
const router = new Bun.FileSystemRouter({
  style: "nextjs",
  dir: "./pages",
  origin: "https://example.com",
  assetPrefix: "_next/static/",
});
```

## Directory Structure

```
pages/
├── index.tsx            → /
├── about.tsx            → /about
├── blog/
│   ├── index.tsx        → /blog
│   └── [slug].tsx       → /blog/:slug
└── [[...catchall]].tsx  → /*
```

## Match Routes

```typescript
// String path
router.match("/");
// → { filePath: "/pages/index.tsx", kind: "exact", name: "/" }

// With params
router.match("/blog/hello-world");
// → { params: { slug: "hello-world" }, kind: "dynamic" }

// With query
router.match("/settings?theme=dark");
// → { query: { theme: "dark" } }

// Request object
router.match(new Request("https://example.com/blog/post"));
```

## Match Result

```typescript
{
  filePath: string;      // Absolute file path
  kind: "exact" | "dynamic" | "catch-all" | "optional-catch-all";
  name: string;          // Route pattern
  pathname: string;      // Matched URL path
  src: string;           // Full URL with origin + assetPrefix
  params?: Record<string, string>;  // URL params
  query?: Record<string, string>;   // Query string
}
```

## Route Patterns

| Pattern           | Example       | Matches              |
| ----------------- | ------------- | -------------------- |
| `index.tsx`       | `/`           | Exact                |
| `about.tsx`       | `/about`      | Exact                |
| `[id].tsx`        | `/123`        | Dynamic segment      |
| `[...slug].tsx`   | `/a/b/c`      | Catch-all (required) |
| `[[...slug]].tsx` | `/` or `/a/b` | Optional catch-all   |

## Reload

Re-scan files when directory changes:

```typescript
router.reload();
```

## Constructor Options

```typescript
new Bun.FileSystemRouter({
  dir: string;              // Pages directory
  style: "nextjs";          // Only supported style
  origin?: string;          // Base URL for src
  assetPrefix?: string;     // Prefix for static assets
  fileExtensions?: string[]; // Allowed extensions
});
```

## Example: HTTP Server

```typescript
const router = new Bun.FileSystemRouter({
  style: "nextjs",
  dir: "./pages",
});

Bun.serve({
  async fetch(req) {
    const match = router.match(req);
    if (!match) {
      return new Response("Not Found", { status: 404 });
    }

    const module = await import(match.filePath);
    return module.default(req, match.params);
  },
});
```

## Notes

- Next.js 13 `app` directory not yet supported
- Only `"nextjs"` style available currently
- Reads directory on init, use `reload()` to refresh
