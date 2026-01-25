# KV Pricing

## Free Plan (per day)

| Metric          | Limit   |
| --------------- | ------- |
| Reads           | 100,000 |
| Writes          | 1,000   |
| Deletes         | 1,000   |
| List operations | 1,000   |
| Storage         | 1 GB    |

## Paid Plan (per month)

| Metric          | Included   | Overage        |
| --------------- | ---------- | -------------- |
| Reads           | 10 million | $0.50/million  |
| Writes          | 1 million  | $5.00/million  |
| Deletes         | 1 million  | $5.00/million  |
| List operations | 1 million  | $5.00/million  |
| Storage         | 1 GB       | $0.50/GB-month |

---

## What's Billable

### Reads

- `get()` — 1 read per key
- `get(keys[])` — 1 read per key (not 1 per call)
- `getWithMetadata()` — same as get()
- Dashboard/Wrangler reads — billable

### Writes

- `put()` — 1 write per key
- Bulk write — 1 write per key
- Dashboard/Wrangler writes — billable

### Deletes

- `delete()` — 1 delete per key
- Bulk delete — 1 delete per key
- Key expiration — **NOT billed** (automatic cleanup)

### List

- `list()` — 1 list operation per call (not per key)
- Wrangler `kv key list` — billable

### Storage

- Measured by total stored data size
- Keys + values + metadata
- Expired keys not counted (cleaned up automatically)

---

## Cost Estimation Examples

### Cache for 10M monthly users

Assumptions:

- 50M reads/month
- 500K writes/month
- 100 MB storage

| Metric    | Usage  | Cost                    |
| --------- | ------ | ----------------------- | --- |
| Reads     | 50M    | (50-10)/1 × $0.50 = $20 |
| Writes    | 500K   | Included                | $0  |
| Storage   | 100 MB | Included                | $0  |
| **Total** |        | **$20/month**           |

### Configuration store

Assumptions:

- 100K reads/month
- 10K writes/month
- 10 MB storage

| Metric    | Usage | Cost                            |
| --------- | ----- | ------------------------------- | --- |
| Reads     | 100K  | Included                        | $0  |
| Writes    | 10K   | Included                        | $0  |
| Storage   | 10 MB | Included                        | $0  |
| **Total** |       | **$0/month** (within free tier) |

### High-write scenario

Assumptions:

- 5M reads/month
- 5M writes/month
- 1 GB storage

| Metric    | Usage | Cost                |
| --------- | ----- | ------------------- | --- |
| Reads     | 5M    | Included            | $0  |
| Writes    | 5M    | (5-1) × $5.00 = $20 |
| Storage   | 1 GB  | Included            | $0  |
| **Total** |       | **$20/month**       |

---

## Cost Optimization Tips

### Reduce reads

```typescript
// Cache locally within request
const cache = new Map<string, any>();

async function getCached(key: string): Promise<any> {
  if (cache.has(key)) return cache.get(key);
  const value = await env.MY_KV.get(key, "json");
  cache.set(key, value);
  return value;
}
```

### Use metadata for small values

```typescript
// Avoid list() + get() pattern
await env.MY_KV.put(key, "", { metadata: { value: smallData } });

// Read via list, no get needed
const { keys } = await env.MY_KV.list({ prefix: "config:" });
const config = keys.map((k) => ({ key: k.name, value: k.metadata?.value }));
```

### Coalesce related data

```typescript
// Instead of many small keys
await env.MY_KV.put("user:123", JSON.stringify({
  profile: { ... },
  settings: { ... },
  preferences: { ... }
}));

// 1 read instead of 3
const user = await env.MY_KV.get("user:123", "json");
```

### Use bulk operations

```bash
# 1 API call for 10,000 writes
npx wrangler kv bulk put data.json --binding MY_KV
```

### Set appropriate expiration

```typescript
// Auto-cleanup reduces storage costs
await env.MY_KV.put("cache:response", data, {
  expirationTtl: 86400, // 1 day
});
```

### Avoid unnecessary list() calls

```typescript
// Bad: list all keys frequently
const allKeys = await env.MY_KV.list();

// Good: use prefixes and cache list results
const cached = await env.CACHE.get("keys:user", "json");
if (!cached) {
  const result = await env.MY_KV.list({ prefix: "user:" });
  await env.CACHE.put("keys:user", JSON.stringify(result.keys), {
    expirationTtl: 60,
  });
}
```

---

## Billing Alerts

In Cloudflare Dashboard:

1. Account Home → Notifications
2. Add notification → Workers & Pages
3. Select usage alerts for KV

---

## Free Plan Limits Exceeded

When daily limits are exceeded:

- Operations fail with error
- Reset at midnight UTC
- Upgrade to Paid removes limits

Check usage:

```bash
# View namespace stats
npx wrangler kv namespace list
```

Or via Dashboard → Workers & Pages → KV → Metrics.
