# R2 Pricing

R2 charges for storage and operations. **Zero egress fees**.

---

## Pricing Table

| Metric             | Standard        | Infrequent Access |
| ------------------ | --------------- | ----------------- |
| Storage            | $0.015/GB-month | $0.01/GB-month    |
| Class A Operations | $4.50/million   | $9.00/million     |
| Class B Operations | $0.36/million   | $0.90/million     |
| Data Retrieval     | Free            | $0.01/GB          |
| Egress             | **Free**        | **Free**          |

---

## Free Tier (Standard only)

| Metric             | Free Limit       |
| ------------------ | ---------------- |
| Storage            | 10 GB-month      |
| Class A Operations | 1 million/month  |
| Class B Operations | 10 million/month |
| Egress             | Unlimited        |

---

## Operation Classes

### Class A (mutate/write)

- `ListBuckets`
- `PutBucket`
- `ListObjects`
- `PutObject`
- `CopyObject`
- `CompleteMultipartUpload`
- `CreateMultipartUpload`
- `UploadPart`
- `UploadPartCopy`
- `ListParts`
- `ListMultipartUploads`
- `PutBucketCors`
- `PutBucketLifecycleConfiguration`
- `PutBucketEncryption`
- `LifecycleStorageTierTransition`

### Class B (read)

- `HeadBucket`
- `HeadObject`
- `GetObject`
- `GetBucketCors`
- `GetBucketLifecycleConfiguration`
- `GetBucketLocation`
- `GetBucketEncryption`
- `UsageSummary`

### Free Operations

- `DeleteObject`
- `DeleteBucket`
- `AbortMultipartUpload`

---

## Infrequent Access

### When to use

- Data accessed less than once per month
- Archival storage
- Backups

### Considerations

- **Minimum storage duration**: 30 days
  - Deleting before 30 days still charges for full 30 days
- **Retrieval fee**: $0.01/GB when reading data
- **Higher operation costs**: 2x Class A, 2.5x Class B

### Cost comparison (1 TB, 1 year)

| Storage Class | Storage | Retrieval (1x/month) | Total |
| ------------- | ------- | -------------------- | ----- |
| Standard      | $180    | $0                   | $180  |
| Infrequent    | $120    | $120                 | $240  |

**Conclusion**: Use IA only if accessing data very rarely (<2x/month).

---

## Cost Estimation Examples

### Static website (10 GB, 1M requests/month)

- Storage: 10 GB × $0.015 = $0.15
- Class B (GET): 1M × $0.36/M = $0.36
- Egress: Free
- **Total**: $0.51/month

### File storage (100 GB, 10K uploads, 100K downloads/month)

- Storage: 100 GB × $0.015 = $1.50
- Class A (PUT): 10K × $4.50/M = $0.045
- Class B (GET): 100K × $0.36/M = $0.036
- **Total**: $1.58/month

### Data lake (1 TB, mostly writes)

- Storage: 1,000 GB × $0.015 = $15
- Class A (100K writes): 100K × $4.50/M = $0.45
- **Total**: $15.45/month

---

## Migration Pricing

### Super Slurper

- Tool usage: **Free**
- You pay: Class A operations for uploaded objects
- Source cloud: May charge egress

### Sippy

- Tool usage: **Free**
- You pay: Class A operations for cached objects
- Source cloud: May charge egress

---

## Cost Optimization Tips

### Use Infrequent Access wisely

Only for data accessed < 2x/month and stored > 30 days.

### Clean up incomplete uploads

```bash
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "abort-mpu" \
  --abort-incomplete-days 1
```

### Delete unused objects

```bash
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "cleanup-temp" \
  --prefix "temp/" \
  --expire-days 1
```

### Batch deletes (free)

```typescript
await env.MY_BUCKET.delete(keysToDelete); // Up to 1000
```

### Optimize list operations

```typescript
// Use prefix to reduce scanned objects
const { objects } = await env.MY_BUCKET.list({
  prefix: "users/123/", // Only list this "folder"
});
```

---

## Billing Dashboard

Monitor usage in Cloudflare Dashboard:

1. R2 → Overview
2. View:
   - Storage used
   - Class A operations
   - Class B operations
   - Egress (always free)

---

## Comparison with AWS S3

| Metric        | R2        | S3 Standard |
| ------------- | --------- | ----------- |
| Storage       | $0.015/GB | $0.023/GB   |
| PUT (Class A) | $4.50/M   | $5.00/M     |
| GET (Class B) | $0.36/M   | $0.40/M     |
| Egress        | **Free**  | $0.09/GB    |

R2 is ~35% cheaper on storage and has zero egress fees.
