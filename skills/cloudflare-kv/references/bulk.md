# KV Bulk Operations

Bulk operations via Wrangler CLI or REST API (not Workers binding).

## Wrangler Bulk Commands

### Bulk Write

```bash
# Create JSON file with key-value pairs
cat > data.json << 'EOF'
[
  { "key": "user:1", "value": "Alice" },
  { "key": "user:2", "value": "Bob" },
  { "key": "config:theme", "value": "{\"mode\":\"dark\"}" }
]
EOF

# Write using binding
npx wrangler kv bulk put data.json --binding MY_KV

# Or using namespace ID
npx wrangler kv bulk put data.json --namespace-id 06779da6...
```

**With expiration**:

```json
[
  { "key": "session:abc", "value": "token123", "expiration_ttl": 3600 },
  { "key": "promo:2025", "value": "active", "expiration": 1735689600 }
]
```

**With metadata**:

```json
[
  {
    "key": "file:123",
    "value": "base64content",
    "metadata": { "filename": "doc.pdf", "size": 1024 }
  }
]
```

**With base64 encoding**:

```json
[{ "key": "binary:1", "value": "SGVsbG8gV29ybGQ=", "base64": true }]
```

### Bulk Read

```bash
# Create file with keys to read
cat > keys.json << 'EOF'
["user:1", "user:2", "config:theme"]
EOF

npx wrangler kv bulk get keys.json --binding MY_KV
```

### Bulk Delete

```bash
# Create file with keys to delete
cat > keys.json << 'EOF'
["user:1", "user:2", "old:key"]
EOF

npx wrangler kv bulk delete keys.json --binding MY_KV

# Skip confirmation
npx wrangler kv bulk delete keys.json --binding MY_KV --force
```

---

## REST API Bulk Operations

### Bulk Write

```bash
curl "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/storage/kv/namespaces/$NAMESPACE_ID/bulk" \
  -X PUT \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    { "key": "user:1", "value": "Alice" },
    { "key": "user:2", "value": "Bob", "expiration_ttl": 3600 }
  ]'
```

### Bulk Delete

```bash
curl "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/storage/kv/namespaces/$NAMESPACE_ID/bulk" \
  -X DELETE \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["user:1", "user:2", "old:key"]'
```

---

## TypeScript SDK

```typescript
import Cloudflare from "cloudflare";

const client = new Cloudflare({
  apiToken: process.env.CLOUDFLARE_API_TOKEN,
});

// Bulk write
await client.kv.namespaces.bulk.update(NAMESPACE_ID, {
  account_id: ACCOUNT_ID,
  body: [
    { key: "user:1", value: "Alice" },
    { key: "user:2", value: "Bob", expiration_ttl: 3600 },
  ],
});

// Bulk delete
await client.kv.namespaces.bulk.delete(NAMESPACE_ID, {
  account_id: ACCOUNT_ID,
  body: ["user:1", "user:2"],
});
```

---

## Limits

| Parameter         | Limit      |
| ----------------- | ---------- |
| Keys per request  | 10,000     |
| Request body size | 100 MB     |
| Key size          | 512 bytes  |
| Value size        | 25 MiB     |
| Metadata size     | 1024 bytes |

---

## Response Format

Successful bulk write:

```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "successful_key_count": 3,
    "unsuccessful_keys": []
  }
}
```

Partial failure:

```json
{
  "success": true,
  "result": {
    "successful_key_count": 2,
    "unsuccessful_keys": ["invalid:key"]
  }
}
```

---

## Patterns

### Migration from JSON file

```bash
# Export from source
curl "https://api.example.com/export" > export.json

# Transform to KV format
jq '[.[] | {key: .id, value: (. | @json)}]' export.json > kv-data.json

# Import to KV
npx wrangler kv bulk put kv-data.json --binding MY_KV
```

### Backup namespace

```bash
# List all keys
npx wrangler kv key list --binding MY_KV > keys.json

# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
mkdir -p backup
for key in $(jq -r '.[].name' keys.json); do
  npx wrangler kv key get "$key" --binding MY_KV > "backup/$key"
done
EOF
```

### Seed data for development

```typescript
// seed.ts
import { readFileSync } from "fs";

const data = JSON.parse(readFileSync("seed-data.json", "utf8"));
const kvFormat = data.map((item) => ({
  key: `user:${item.id}`,
  value: JSON.stringify(item),
  metadata: { createdAt: new Date().toISOString() },
}));

console.log(JSON.stringify(kvFormat, null, 2));
```

```bash
npx ts-node seed.ts > kv-seed.json
npx wrangler kv bulk put kv-seed.json --binding MY_KV
```

---

## Best Practices

### Batch writes efficiently

```typescript
// Instead of individual puts in a loop
for (const item of items) {
  await env.MY_KV.put(item.key, item.value); // Slow, hits rate limits
}

// Use bulk API via REST
await fetch(`https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/storage/kv/namespaces/${NAMESPACE_ID}/bulk`, {
  method: "PUT",
  headers: {
    Authorization: `Bearer ${API_TOKEN}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(items),
});
```

### Handle partial failures

```typescript
const response = await bulkWrite(items);
if (response.result.unsuccessful_keys.length > 0) {
  console.error("Failed keys:", response.result.unsuccessful_keys);
  // Retry failed keys
}
```
