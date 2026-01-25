# Workflows Pricing

## Plan Requirement

Workflows requires **Workers Paid** plan ($5/month).

## Billing Dimensions

| Metric                 | Free                           | Paid                            |
| ---------------------- | ------------------------------ | ------------------------------- |
| Requests (invocations) | 100K/day (shared with Workers) | 10M/mo included, +$0.30/M       |
| CPU time               | 10 ms/invocation               | 30M ms/mo included, +$0.02/M ms |
| Storage                | 1 GB                           | 1 GB included, +$0.20/GB-mo     |

## CPU Time

- Billed on total CPU milliseconds consumed
- Each step consumes CPU time independently
- Default limit: 30 seconds per step (configurable to 5 min)

**Example**: Workflow with 5 steps, each using 100ms CPU

- Total CPU: 500 ms per invocation
- 60K invocations = 30M ms (included in Paid)

## Requests (Invocations)

- Each `create()` call = 1 invocation
- Subrequests from within Workflow do NOT count extra
- `createBatch()` counts as N invocations (one per instance)

**Example**:

- 1M Workflow invocations/month
- Cost: (1M - 10M) = within included, **$0**
- 15M invocations: (15M - 10M) = 5M × $0.30/M = **$1.50**

## Storage

Billed as GB-months across all instances:

- Running instances
- Sleeping instances
- Waiting instances
- Completed instances (until retention expires)

**Storage per instance**:

- Step return values (up to 1 MiB each)
- Event payloads
- Instance metadata

**Retention periods**:
| Plan | Completed Instance Retention |
|------|------------------------------|
| Free | 3 days |
| Paid | 30 days |

**Example**:

- 10K instances, average 10 KB state each
- Total: 100 MB
- Monthly cost: 0.1 GB × $0.20 = **$0.02**

## Cost Optimization

1. **Minimize step return sizes** — return only what you need
2. **Delete completed instances** — reduces storage immediately
3. **Use external storage** — store large data in R2/KV, return only references
4. **Batch instance creation** — reduces API overhead

## Free Plan Limits

- CPU: 10 ms per step invocation
- Concurrent instances: 25
- Storage limit: 1 GB (errors if exceeded)
- Daily requests: 100K (shared with Workers)

## Paid Plan Defaults

- CPU: 30 sec per step (max 5 min with config)
- Concurrent instances: 10,000
- Storage: 1 GB included, expandable

## Storage Calculation

```
storage_gb_month = sum(instance_state_bytes) / (1024^3) × days_stored / 30
```

Deleting instances via API, Wrangler, or dashboard frees storage within minutes.

## No Additional Charges

- ✓ No fees for sleeping instances
- ✓ No fees for waiting instances
- ✓ No per-step fees
- ✓ No egress fees
