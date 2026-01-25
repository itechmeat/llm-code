# Durable Objects Pricing

## Overview

Durable Objects billing has two components:

1. **Compute**: Requests + Duration
2. **Storage**: Read/Write operations + Stored data

## Compute Pricing

### Requests

| Plan | Included        | Additional        |
| ---- | --------------- | ----------------- |
| Free | 100,000/day     | —                 |
| Paid | 1,000,000/month | $0.15 per million |

**Counting**:

- Each RPC method call = 1 request
- Each `fetch()` to DO = 1 request
- WebSocket messages: 20:1 ratio (1M messages = 50K requests for billing)

### Duration

| Plan | Included           | Additional              |
| ---- | ------------------ | ----------------------- |
| Free | 13,000 GB-s/day    | —                       |
| Paid | 400,000 GB-s/month | $12.50 per million GB-s |

**Calculation**: `(execution_time_seconds) × (memory_gb)`

## Storage Pricing

### SQLite-backed (from Jan 2026)

| Metric       | Free       | Paid                                 |
| ------------ | ---------- | ------------------------------------ |
| Rows read    | 5M/day     | 25B/month included, +$0.001/M        |
| Rows written | 100K/day   | 50M/month included, +$1.00/M         |
| Stored data  | 5 GB total | 5 GB-month included, +$0.20/GB-month |

**Notes**:

- `DELETE` counts as rows written
- `setAlarm()` counts as rows written
- Full table scans read all rows

### KV-backed (Paid only)

| Metric      | Included   | Additional         |
| ----------- | ---------- | ------------------ |
| Read units  | 1M/month   | $0.20 per million  |
| Write units | 1M/month   | $1.00 per million  |
| Stored data | 1 GB-month | $0.20 per GB-month |

## Cost Examples

### Example 1: Chat Application

**Usage**:

- 100,000 chat rooms (Durable Objects)
- 10M messages/month
- Average 100 KB storage per room

**Compute**:

- Requests: 10M messages ÷ 20 = 500K request-equivalent
- Under 1M included: **$0**

**Storage** (SQLite):

- Stored: 100K × 100 KB = 10 GB
- 10 GB - 5 GB included = 5 GB × $0.20 = **$1.00/month**

### Example 2: Rate Limiter

**Usage**:

- 50M requests/month
- Minimal storage (~1 KB per DO)

**Compute**:

- Requests: 50M - 1M = 49M × $0.15 = **$7.35**
- Duration: ~100ms per request, 128 MB
  - 50M × 0.1s × 0.128 GB = 640,000 GB-s
  - 640K - 400K = 240K × $12.50/M = **$3.00**

**Total**: ~$10.35/month

### Example 3: Game Session Manager

**Usage**:

- 1000 concurrent sessions
- 10 DB writes per session per minute
- 1 hour average session

**Compute**:

- Requests: 1000 × 60 × 10 = 600K/hour
- Duration: 1000 × 3600s × 0.128 GB = 460,800 GB-s/hour

**Storage** (SQLite):

- Writes: 600K × 24 hours = 14.4M/day
- Under 50M included: **$0**

## Cost Optimization

1. **Batch operations**: Reduce request count with batching
2. **Write coalescing**: Multiple `put()` without await = single transaction
3. **Efficient queries**: Use indexes, avoid full table scans
4. **Clean up storage**: Delete unused data
5. **Short-lived DOs**: Don't keep objects alive unnecessarily

## Free Plan Limits

| Resource   | Limit           |
| ---------- | --------------- |
| Requests   | 100,000/day     |
| Duration   | 13,000 GB-s/day |
| Storage    | 5 GB total      |
| DO classes | 100             |

## Paid Plan Defaults

| Resource       | Included           |
| -------------- | ------------------ |
| Requests       | 1,000,000/month    |
| Duration       | 400,000 GB-s/month |
| SQLite storage | 5 GB-month         |
| KV storage     | 1 GB-month         |
