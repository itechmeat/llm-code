# R2 Workers Binding API

## R2Bucket Methods

### head(key)

Returns object metadata without body.

```typescript
const metadata = await env.MY_BUCKET.head("image.png");
// R2Object | null

if (metadata) {
  console.log(metadata.key, metadata.size, metadata.etag);
}
```

### get(key, options?)

Returns object with body.

```typescript
const object = await env.MY_BUCKET.get("file.txt");
// R2ObjectBody | R2Object | null

if (!object) {
  return new Response("Not Found", { status: 404 });
}

// Read body
const text = await object.text();
const json = await object.json();
const buffer = await object.arrayBuffer();
const blob = await object.blob();
// or stream: object.body
```

### put(key, value, options?)

Stores object.

```typescript
await env.MY_BUCKET.put("file.txt", "Hello, World!");

// With options
await env.MY_BUCKET.put("image.png", imageBuffer, {
  httpMetadata: {
    contentType: "image/png",
    cacheControl: "public, max-age=31536000",
  },
  customMetadata: {
    uploadedBy: "user-123",
  },
});
```

**Value types**: `ReadableStream | ArrayBuffer | ArrayBufferView | string | Blob | null`

### delete(key | keys[])

Deletes objects.

```typescript
// Single
await env.MY_BUCKET.delete("old-file.txt");

// Batch (up to 1000)
await env.MY_BUCKET.delete(["file1.txt", "file2.txt", "file3.txt"]);
```

### list(options?)

Lists objects with pagination.

```typescript
const listed = await env.MY_BUCKET.list({
  prefix: "images/",
  limit: 100,
  cursor: previousCursor,
  delimiter: "/",
  include: ["httpMetadata", "customMetadata"],
});

for (const object of listed.objects) {
  console.log(object.key, object.size);
}

// Pagination
if (listed.truncated) {
  const nextPage = await env.MY_BUCKET.list({
    prefix: "images/",
    cursor: listed.cursor,
  });
}

// Common prefixes (for "folder" simulation)
for (const prefix of listed.delimitedPrefixes) {
  console.log("Folder:", prefix);
}
```

---

## R2GetOptions

```typescript
interface R2GetOptions {
  onlyIf?: R2Conditional | Headers;
  range?: R2Range;
  ssecKey?: ArrayBuffer | string;
}
```

### Range Reads

```typescript
// First 1KB
const partial = await env.MY_BUCKET.get("large.bin", {
  range: { offset: 0, length: 1024 },
});

// Last 1KB
const tail = await env.MY_BUCKET.get("large.bin", {
  range: { suffix: 1024 },
});
```

### Conditional Operations

```typescript
// ETag conditions
const object = await env.MY_BUCKET.get("file.txt", {
  onlyIf: {
    etagMatches: "abc123",
    // etagDoesNotMatch: "abc123",
    // uploadedBefore: new Date("2024-01-01"),
    // uploadedAfter: new Date("2023-01-01")
  },
});

// From HTTP headers
const object = await env.MY_BUCKET.get("file.txt", {
  onlyIf: request.headers, // Reads If-Match, If-None-Match, etc.
});
```

---

## R2PutOptions

```typescript
interface R2PutOptions {
  onlyIf?: R2Conditional | Headers;
  httpMetadata?: R2HTTPMetadata;
  customMetadata?: Record<string, string>;
  md5?: ArrayBuffer | string;
  sha1?: ArrayBuffer | string;
  sha256?: ArrayBuffer | string;
  sha384?: ArrayBuffer | string;
  sha512?: ArrayBuffer | string;
  storageClass?: "Standard" | "InfrequentAccess";
  ssecKey?: ArrayBuffer | string;
}
```

### HTTP Metadata

```typescript
await env.MY_BUCKET.put("file.pdf", data, {
  httpMetadata: {
    contentType: "application/pdf",
    contentDisposition: 'attachment; filename="document.pdf"',
    contentEncoding: "gzip",
    contentLanguage: "en",
    cacheControl: "public, max-age=3600",
    cacheExpiry: new Date("2025-01-01"),
  },
});
```

### Storage Class

```typescript
await env.MY_BUCKET.put("archive.zip", data, {
  storageClass: "InfrequentAccess",
});
```

---

## R2ListOptions

```typescript
interface R2ListOptions {
  limit?: number; // Max 1000, default 1000
  prefix?: string; // Filter by prefix
  cursor?: string; // Pagination cursor
  delimiter?: string; // Folder delimiter (usually "/")
  startAfter?: string; // Start listing after this key
  include?: ("httpMetadata" | "customMetadata")[];
}
```

---

## R2Object

```typescript
interface R2Object {
  key: string; // Object key
  version: string; // Version ID
  size: number; // Size in bytes
  etag: string; // ETag (unquoted)
  httpEtag: string; // ETag (quoted for HTTP)
  uploaded: Date; // Upload timestamp
  httpMetadata: R2HTTPMetadata; // Content-Type, etc.
  customMetadata: Record<string, string>;
  storageClass: "Standard" | "InfrequentAccess";
  checksums: R2Checksums;

  writeHttpMetadata(headers: Headers): void;
}
```

### writeHttpMetadata

Copies HTTP metadata to response headers.

```typescript
const object = await env.MY_BUCKET.get("file.pdf");
if (!object) return new Response("Not Found", { status: 404 });

const headers = new Headers();
object.writeHttpMetadata(headers);
headers.set("etag", object.httpEtag);

return new Response(object.body, { headers });
```

---

## R2ObjectBody

Extends R2Object with body.

```typescript
interface R2ObjectBody extends R2Object {
  body: ReadableStream;
  bodyUsed: boolean;

  arrayBuffer(): Promise<ArrayBuffer>;
  text(): Promise<string>;
  json<T>(): Promise<T>;
  blob(): Promise<Blob>;
}
```

---

## R2Objects (list result)

```typescript
interface R2Objects {
  objects: R2Object[];
  truncated: boolean;
  cursor?: string;
  delimitedPrefixes: string[];
}
```

---

## Multipart Upload Methods

### createMultipartUpload(key, options?)

```typescript
const mpu = await env.MY_BUCKET.createMultipartUpload("large.zip", {
  httpMetadata: { contentType: "application/zip" },
  customMetadata: { uploader: "user-123" },
});
// mpu.uploadId — save for resuming
```

### resumeMultipartUpload(key, uploadId)

```typescript
const mpu = env.MY_BUCKET.resumeMultipartUpload("large.zip", uploadId);
```

### R2MultipartUpload methods

```typescript
// Upload part (minimum 5 MiB except last)
const part = await mpu.uploadPart(partNumber, data);
// part: { partNumber, etag }

// Complete upload
const object = await mpu.complete(uploadedParts);
// object: R2Object

// Abort upload
await mpu.abort();
```

---

## Error Handling

```typescript
try {
  await env.MY_BUCKET.put("file.txt", data);
} catch (error) {
  if (error instanceof Error) {
    console.error("R2 error:", error.message);
  }
}
```

Common errors:

- Object not found (get/head returns null)
- Precondition failed (conditional operations)
- Part too small (multipart < 5 MiB)
