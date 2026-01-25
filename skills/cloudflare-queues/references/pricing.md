# Queues Pricing

## Plan Requirement

Queues requires **Workers Paid** plan ($5/month).

## Included

- 1 million operations/month

## Additional Usage

- **$0.40 per million operations** (after included)

## What Counts as an Operation

| Action                  | Operations        |
| ----------------------- | ----------------- |
| Write message to queue  | 1 per 64 KB       |
| Read message (consumer) | 1 per 64 KB       |
| Delete message (on ack) | 1 per 64 KB       |
| Retry (re-read)         | 1 additional read |
| DLQ write               | 1 write           |

**64 KB unit**: Messages larger than 64 KB count as multiple operations.

| Message Size | Write Ops | Read Ops | Delete Ops |
| ------------ | --------- | -------- | ---------- |
| ≤ 64 KB      | 1         | 1        | 1          |
| 65 KB        | 2         | 2        | 2          |
| 128 KB       | 2         | 2        | 2          |

## Cost Examples

### Light usage

- 500K messages/month × 3 ops = 1.5M ops
- Within included: **$0**

### Medium usage

- 5M messages/month × 3 ops = 15M ops
- Billable: 15M - 1M = 14M ops
- Cost: 14 × $0.40 = **$5.60**

### With retries

- 1M messages, 10% retry once
- Ops: 1M writes + 1.1M reads + 1M deletes = 3.1M
- Billable: 2.1M ops
- Cost: 2.1 × $0.40 = **$0.84**

### Large messages

- 1M messages at 100KB each
- Each = 2 ops per action
- Ops: 1M × 2 × 3 = 6M ops
- Billable: 5M ops
- Cost: 5 × $0.40 = **$2.00**

## No Additional Charges

- ✓ No egress fees
- ✓ No storage fees
- ✓ No per-queue fees
- ✓ No API request fees

## DLQ Consideration

DLQ messages incur:

1. Original queue retries (reads)
2. DLQ write (1 op)
3. DLQ read when processed (1 op)
4. DLQ delete when acked (1 op)

## Cost Optimization

1. Keep messages small (≤ 64 KB)
2. Minimize retries with proper error handling
3. Process DLQ regularly
4. Use batch operations efficiently
