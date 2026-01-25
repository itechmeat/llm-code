# Headers and Redirects

Static configuration files for HTTP headers and URL redirects.

## \_headers File

Create `_headers` in build output directory (e.g., `public/_headers` or `dist/_headers`).

### Syntax

```txt
[url-pattern]
  [Header-Name]: [value]
```

### Examples

```txt
# Apply to all pages
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin

# Specific path
/secure/*
  Content-Security-Policy: default-src 'self'

# Cache static assets
/static/*
  Cache-Control: public, max-age=31536000, immutable

# API endpoints
/api/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE
```

### Placeholders and Splats

```txt
# Named placeholder
/users/:id
  X-User-Id: :id

# Splat (catch-all)
/files/*
  X-Path: :splat
```

### Detach Headers

Remove inherited headers with `! `:

```txt
# Remove header for specific path
/public/*
  ! Content-Security-Policy
```

### Limits

| Limit             | Value             |
| ----------------- | ----------------- |
| Max rules         | 100               |
| Max line length   | 2,000 characters  |
| Duplicate headers | Joined with comma |

---

## \_redirects File

Create `_redirects` in build output directory.

### Syntax

```txt
[source] [destination] [status-code]
```

Default status code: 302 (temporary redirect)

### Examples

```txt
# Permanent redirect
/old-page /new-page 301

# Temporary redirect (default)
/temp /other

# External redirect
/twitter https://twitter.com/myaccount 301

# Trailing slash normalization
/about/ /about 301
/contact /contact/ 301

# Fragment redirect
/section /page#anchor 301
```

### Splats and Placeholders

```txt
# Splat (catch-all)
/blog/* https://blog.example.com/:splat

# Named placeholder
/users/:id /profiles/:id 301

# Multiple placeholders
/products/:category/:id /shop/:category/:id 301
```

### Proxying (200 Status)

Proxy requests to different path (relative URLs only):

```txt
# Proxy /api to /backend
/api/* /backend/:splat 200

# SPA fallback
/* /index.html 200
```

> **Limitation:** Cannot proxy to absolute URLs.

### Limits

| Limit             | Value            |
| ----------------- | ---------------- |
| Static redirects  | 2,000            |
| Dynamic redirects | 100              |
| Total redirects   | 2,100            |
| Max line length   | 1,000 characters |

### Unsupported Features

- Query string matching
- Domain-level redirects
- Country/language redirects
- Cookie-based redirects
- Absolute URL proxying

---

## Execution Order

1. Redirects execute first
2. Headers applied after redirects

---

## Early Hints (103)

Automatic `Link` header generation for preloading resources.

### Automatic Generation

Pages automatically creates `Link` headers from HTML:

```html
<link rel="preload" href="/app.js" as="script" />
<link rel="preconnect" href="https://api.example.com" />
<link rel="modulepreload" href="/module.js" />
```

### Manual Link Headers

```txt
/*
  Link: </app.js>; rel=preload; as=script
  Link: </styles.css>; rel=preload; as=style
```

### Disable Automatic Links

```txt
/*
  ! Link
```

---

## Pages Functions Warning

> **Critical:** `_headers` and `_redirects` do NOT apply to responses from Pages Functions.

For Functions responses, attach headers in code:

```javascript
export function onRequest(context) {
  return new Response("Hello", {
    headers: {
      "X-Custom-Header": "value",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
```

For redirects in Functions:

```javascript
export function onRequest(context) {
  return Response.redirect("https://example.com/new-path", 301);
}
```

---

## Default Response Headers

Pages automatically adds:

| Header                        | Value                             |
| ----------------------------- | --------------------------------- |
| `Access-Control-Allow-Origin` | `*`                               |
| `Referrer-Policy`             | `strict-origin-when-cross-origin` |
| `X-Content-Type-Options`      | `nosniff`                         |
| `Server`                      | `cloudflare`                      |
| `Cf-Ray`                      | Request ID                        |
| `Etag`                        | Content hash                      |

Preview deployments also add:

| Header         | Value     |
| -------------- | --------- |
| `X-Robots-Tag` | `noindex` |

---

## Bulk Redirects

For exceeding `_redirects` limits, use account-level Bulk Redirects:

1. Rules > Bulk Redirects
2. Create redirect list
3. Enable list

> Bulk Redirects apply at account level, not project level.
