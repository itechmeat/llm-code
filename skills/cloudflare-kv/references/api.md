# KV Workers API Reference

## KVNamespace Methods

### put(key, value, options?)

Stores a key-value pair.

```typescript
// Basic usage
await env.MY_KV.put("key", "value");

// With expiration (TTL)
await env.MY_KV.put("session:abc", token, {
  expirationTtl: 3600, // 1 hour from now (seconds)
});

// With absolute expiration
await env.MY_KV.put("promo:2025", data, {
  expiration: 1735689600, // Unix timestamp (seconds)
});

// With metadata
await env.MY_KV.put("file:123", content, {
  metadata: {
    filename: "doc.pdf",
    contentType: "application/pdf",
  },
});

// All options
await env.MY_KV.put("key", value, {
  expirationTtl: 3600,
  metadata: { version: 1 },
});
```

**Parameters**:

| Parameter             | Type                                    | Description                                   |
| --------------------- | --------------------------------------- | --------------------------------------------- |
| key                   | string                                  | Max 512 bytes, cannot be empty or "." or ".." |
| value                 | string \| ArrayBuffer \| ReadableStream | Max 25 MiB                                    |
| options.expiration    | number                                  | Absolute Unix timestamp (seconds)             |
| options.expirationTtl | number                                  | Seconds from now (min 60)                     |
| options.metadata      | object                                  | JSON-serializable, max 1024 bytes             |

**Returns**: `Promise<void>`

---

### get(key, type?)

Retrieves a value.

```typescript
// Text (default)
const text = await env.MY_KV.get("key");
// string | null

// JSON
const obj = await env.MY_KV.get("key", "json");
// any | null

// ArrayBuffer
const buffer = await env.MY_KV.get("key", "arrayBuffer");
// ArrayBuffer | null

// Stream
const stream = await env.MY_KV.get("key", "stream");
// ReadableStream | null
```

**With options**:

```typescript
const data = await env.MY_KV.get("key", {
  type: "json",
  cacheTtl: 300, // Cache at edge for 5 minutes
});
```

**Parameters**:

| Parameter        | Type                                          | Description                          |
| ---------------- | --------------------------------------------- | ------------------------------------ |
| key              | string                                        | Key to retrieve                      |
| type             | "text" \| "json" \| "arrayBuffer" \| "stream" | Return type (default: "text")        |
| options.type     | string                                        | Same as type parameter               |
| options.cacheTtl | number                                        | Edge cache duration (min 60 seconds) |

**Returns**: `Promise<T | null>` where T depends on type.

---

### get(keys[], type?)

Multi-key read (up to 100 keys).

```typescript
const results = await env.MY_KV.get(["key1", "key2", "key3"], "json");
// Map<string, T | null>

for (const [key, value] of results) {
  if (value !== null) {
    console.log(key, value);
  }
}
```

**Limits**:

- Maximum 100 keys per call
- Only "text" and "json" types supported for multi-key
- Counts as 1 operation for external ops limit

---

### getWithMetadata(key, type?)

Retrieves value with metadata.

```typescript
const { value, metadata } = await env.MY_KV.getWithMetadata("key", "json");

if (value !== null) {
  console.log(value);
  console.log(metadata); // object | null
}
```

**Multi-key**:

```typescript
const results = await env.MY_KV.getWithMetadata(["key1", "key2"], "json");
// Map<string, { value: T | null, metadata: object | null }>

for (const [key, { value, metadata }] of results) {
  console.log(key, value, metadata);
}
```

---

### list(options?)

Lists keys in namespace.

```typescript
// Basic usage
const result = await env.MY_KV.list();
// { keys: [...], list_complete: boolean, cursor?: string }

// With prefix filter
const users = await env.MY_KV.list({ prefix: "user:" });

// With limit
const page = await env.MY_KV.list({ limit: 100 });

// Pagination
const next = await env.MY_KV.list({ cursor: result.cursor });
```

**Parameters**:

| Parameter      | Type   | Description                  |
| -------------- | ------ | ---------------------------- |
| options.prefix | string | Filter keys by prefix        |
| options.limit  | number | Max keys (default/max: 1000) |
| options.cursor | string | Pagination cursor            |

**Returns**:

```typescript
interface KVListResult {
  keys: Array<{
    name: string;
    expiration?: number; // Unix timestamp
    metadata?: object;
  }>;
  list_complete: boolean;
  cursor?: string;
}
```

**Pagination pattern**:

```typescript
async function listAllKeys(namespace: KVNamespace, prefix?: string) {
  const allKeys: string[] = [];
  let cursor: string | undefined;

  do {
    const result = await namespace.list({ prefix, cursor });
    allKeys.push(...result.keys.map((k) => k.name));
    cursor = result.list_complete ? undefined : result.cursor;
  } while (cursor);

  return allKeys;
}
```

---

### delete(key)

Deletes a key.

```typescript
await env.MY_KV.delete("key");
// Resolves successfully even if key doesn't exist
```

**Returns**: `Promise<void>`

---

## Type Definitions

```typescript
interface KVNamespace {
  put(key: string, value: string | ArrayBuffer | ReadableStream, options?: KVPutOptions): Promise<void>;
  get(key: string, type?: "text"): Promise<string | null>;
  get(key: string, type: "json"): Promise<any | null>;
  get(key: string, type: "arrayBuffer"): Promise<ArrayBuffer | null>;
  get(key: string, type: "stream"): Promise<ReadableStream | null>;
  get(key: string, options: KVGetOptions): Promise<string | any | ArrayBuffer | ReadableStream | null>;
  get(keys: string[], type?: "text" | "json"): Promise<Map<string, string | any | null>>;
  getWithMetadata(key: string, type?: KVType): Promise<{ value: any; metadata: any }>;
  getWithMetadata(keys: string[], type?: "text" | "json"): Promise<Map<string, { value: any; metadata: any }>>;
  list(options?: KVListOptions): Promise<KVListResult>;
  delete(key: string): Promise<void>;
}

interface KVPutOptions {
  expiration?: number;
  expirationTtl?: number;
  metadata?: object;
}

interface KVGetOptions {
  type?: "text" | "json" | "arrayBuffer" | "stream";
  cacheTtl?: number;
}

interface KVListOptions {
  prefix?: string;
  limit?: number;
  cursor?: string;
}
```

---

## Error Handling

```typescript
try {
  await env.MY_KV.put("key", value);
} catch (error) {
  if (error.message.includes("429")) {
    // Rate limited: too many writes to same key
    // Implement exponential backoff
  }
  throw error;
}
```

Common errors:

- 429: Write rate limit exceeded (> 1/sec to same key)
- 413: Value size exceeds 25 MiB
- Key validation errors (empty, too long, invalid chars)
