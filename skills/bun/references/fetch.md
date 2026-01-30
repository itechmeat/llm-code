# Fetch

WHATWG fetch implementation with Bun-specific extensions.

## Basic Usage

```typescript
const response = await fetch("https://example.com");
console.log(response.status);
const data = await response.json();
```

## Request Methods

```typescript
// GET (default)
await fetch("https://api.example.com/users");

// POST with body
await fetch("https://api.example.com/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "John" }),
});

// Using Request object
const req = new Request("https://api.example.com", {
  method: "POST",
  body: "Hello",
});
await fetch(req);
```

## Response Body

```typescript
response.text();        // Promise<string>
response.json();        // Promise<any>
response.formData();    // Promise<FormData>
response.bytes();       // Promise<Uint8Array>
response.arrayBuffer(); // Promise<ArrayBuffer>
response.blob();        // Promise<Blob>
```

## Streaming

### Response Streaming

```typescript
for await (const chunk of response.body) {
  console.log(chunk);
}

// Or with reader
const reader = response.body.getReader();
const { value, done } = await reader.read();
```

### Request Streaming

```typescript
const stream = new ReadableStream({
  start(controller) {
    controller.enqueue("Hello");
    controller.close();
  },
});

await fetch(url, { method: "POST", body: stream });
```

## Timeout & Cancellation

```typescript
// Timeout
await fetch(url, {
  signal: AbortSignal.timeout(5000),
});

// Manual cancellation
const controller = new AbortController();
fetch(url, { signal: controller.signal });
controller.abort();
```

## Proxy

```typescript
await fetch(url, {
  proxy: "http://proxy.com:8080",
});

// With auth headers
await fetch(url, {
  proxy: {
    url: "http://proxy.com",
    headers: { "Proxy-Authorization": "Bearer token" },
  },
});
```

## TLS Options

```typescript
// Client certificate
await fetch("https://example.com", {
  tls: {
    key: Bun.file("/path/to/key.pem"),
    cert: Bun.file("/path/to/cert.pem"),
  },
});

// Disable TLS validation (dev only!)
await fetch("https://localhost:3000", {
  tls: { rejectUnauthorized: false },
});
```

## Unix Domain Sockets

```typescript
await fetch("http://localhost/api", {
  unix: "/var/run/docker.sock",
});
```

## Protocol Support

```typescript
// File URLs
await fetch("file:///path/to/file.txt");

// Data URLs
await fetch("data:text/plain;base64,SGVsbG8=");

// Blob URLs
const blob = new Blob(["Hello"]);
await fetch(URL.createObjectURL(blob));

// S3 URLs
await fetch("s3://bucket/key", {
  s3: {
    accessKeyId: "...",
    secretAccessKey: "...",
    region: "us-east-1",
  },
});
```

## Debugging

```typescript
await fetch(url, { verbose: true });
// Prints request/response headers

// Or as curl commands
await fetch(url, { verbose: "curl" });
```

Environment variable:

```bash
BUN_CONFIG_VERBOSE_FETCH=true bun script.ts
```

## Performance

### DNS Prefetch

```typescript
import { dns } from "bun";
dns.prefetch("api.example.com");
```

### Preconnect

```typescript
fetch.preconnect("https://api.example.com");
```

Or at startup:

```bash
bun --fetch-preconnect https://api.example.com script.ts
```

### Connection Limit

```bash
BUN_CONFIG_MAX_HTTP_REQUESTS=512 bun script.ts
```

Default: 256, Max: 65,336

## Bun-Specific Options

```typescript
await fetch(url, {
  decompress: true,     // Auto decompress gzip/br/zstd
  keepalive: false,     // Disable connection reuse
  verbose: true,        // Debug logging
  proxy: "...",         // HTTP proxy
  unix: "...",          // Unix socket
  tls: { ... },         // TLS options
  s3: { ... },          // S3 credentials
});
```

## Write Response to File

```typescript
await Bun.write("output.txt", response);
```
