# R2 Lifecycle Policies

Automate object expiration and storage class transitions.

## Overview

- Delete objects after N days
- Transition to Infrequent Access storage class
- Abort incomplete multipart uploads
- Filter by prefix/suffix

---

## Wrangler Commands

### Add Lifecycle Rule

```bash
# Delete objects after 90 days
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "delete-old" \
  --expire-days 90

# Transition to Infrequent Access after 30 days
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "ia-transition" \
  --transition-days 30 \
  --transition-class STANDARD_IA

# Expire on specific date
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "expire-2025" \
  --expire-date "2025-01-01"

# With prefix filter
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "cleanup-logs" \
  --prefix "logs/" \
  --expire-days 7

# Abort incomplete multipart uploads
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "abort-mpu" \
  --abort-incomplete-days 1
```

### List Rules

```bash
npx wrangler r2 bucket lifecycle list my-bucket
```

### Remove Rule

```bash
npx wrangler r2 bucket lifecycle remove my-bucket --id "cleanup-logs"
```

---

## S3 API

```typescript
import { S3Client, PutBucketLifecycleConfigurationCommand } from "@aws-sdk/client-s3";

const S3 = new S3Client({
  region: "auto",
  endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: { accessKeyId: ACCESS_KEY_ID, secretAccessKey: SECRET_ACCESS_KEY },
});

await S3.send(
  new PutBucketLifecycleConfigurationCommand({
    Bucket: "my-bucket",
    LifecycleConfiguration: {
      Rules: [
        {
          ID: "delete-temp",
          Status: "Enabled",
          Filter: { Prefix: "temp/" },
          Expiration: { Days: 1 },
        },
        {
          ID: "archive-old",
          Status: "Enabled",
          Filter: { Prefix: "" }, // All objects
          Transitions: [{ Days: 30, StorageClass: "STANDARD_IA" }],
        },
        {
          ID: "cleanup-2024",
          Status: "Enabled",
          Filter: { Prefix: "2024/" },
          Expiration: { Date: new Date("2025-06-01") },
        },
        {
          ID: "abort-mpu",
          Status: "Enabled",
          AbortIncompleteMultipartUpload: { DaysAfterInitiation: 7 },
        },
      ],
    },
  })
);
```

---

## Rule Examples

### Delete logs after 7 days

```bash
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "cleanup-logs" \
  --prefix "logs/" \
  --expire-days 7
```

### Archive to Infrequent Access after 30 days

```bash
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "archive-30d" \
  --transition-days 30 \
  --transition-class STANDARD_IA
```

### Delete user uploads after 1 year

```bash
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "delete-old-uploads" \
  --prefix "uploads/" \
  --expire-days 365
```

### Cleanup cache daily

```bash
npx wrangler r2 bucket lifecycle add my-bucket \
  --id "cache-cleanup" \
  --prefix "cache/" \
  --expire-days 1
```

---

## Behavior Notes

### Timing

- Objects typically removed within 24 hours of expiration
- Newly uploaded objects reflect lifecycle immediately
- Existing objects may take up to 24 hours to reflect new rules

### Conflicts

When multiple rules apply:

- Delete (Expiration) takes precedence over Transition
- Rules with shorter durations win

### Infrequent Access considerations

- Minimum 30-day storage (charged even if deleted earlier)
- Retrieval fee: $0.01/GB
- Transition counts as Class A operation

---

## Filter Options

### Prefix

```json
{
  "Filter": { "Prefix": "logs/" }
}
```

### Tag (S3 API)

```json
{
  "Filter": {
    "Tag": { "Key": "environment", "Value": "dev" }
  }
}
```

### And (multiple conditions)

```json
{
  "Filter": {
    "And": {
      "Prefix": "logs/",
      "Tags": [{ "Key": "type", "Value": "debug" }]
    }
  }
}
```

---

## Dashboard Configuration

1. Go to R2 → Your Bucket
2. Settings → Object Lifecycle Rules
3. Add rule → Configure:
   - Rule name
   - Scope (all objects or prefix)
   - Action (expire, transition, abort MPU)
   - Timeline (days or date)

---

## Limits

| Parameter                  | Limit            |
| -------------------------- | ---------------- |
| Lifecycle rules per bucket | 1,000            |
| Prefix length              | 1,024 characters |
| Minimum transition days    | 0                |
| Minimum expiration days    | 1                |

---

## Disable/Enable Rule

Via S3 API, set `Status`:

```json
{
  "ID": "my-rule",
  "Status": "Disabled",  // or "Enabled"
  ...
}
```

Rules cannot be disabled via Wrangler — remove and re-add.
