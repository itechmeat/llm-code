# Consumer Configuration

## wrangler.jsonc Configuration

```jsonc
{
  "queues": {
    "consumers": [
      {
        "queue": "my-queue",
        "max_batch_size": 10,
        "max_batch_timeout": 5,
        "max_retries": 3,
        "max_concurrency": 10,
        "dead_letter_queue": "my-dlq",
        "retry_delay": 60
      }
    ]
  }
}
```

## Consumer Settings

| Setting             | Type   | Default  | Range   | Description                   |
| ------------------- | ------ | -------- | ------- | ----------------------------- |
| `queue`             | string | required | —       | Queue name                    |
| `max_batch_size`    | number | 10       | 1-100   | Messages per batch            |
| `max_batch_timeout` | number | 5        | 0-60    | Seconds to fill batch         |
| `max_retries`       | number | 3        | 0-100   | Retries before DLQ/delete     |
| `max_concurrency`   | number | auto     | 1-250   | Max concurrent invocations    |
| `dead_letter_queue` | string | none     | —       | DLQ name                      |
| `retry_delay`       | number | 0        | 0-43200 | Default retry delay (seconds) |

## Batching

Messages batch until:

- `max_batch_size` reached, OR
- `max_batch_timeout` elapsed

```jsonc
// Small batches, fast delivery
{ "max_batch_size": 1, "max_batch_timeout": 0 }

// Large batches, higher latency
{ "max_batch_size": 100, "max_batch_timeout": 30 }
```

## Concurrency

Auto-scales based on:

- Queue backlog size and growth rate
- Consumer success/failure ratio
- `max_concurrency` limit

```jsonc
// Sequential processing
{ "max_concurrency": 1 }

// High parallelism
{ "max_concurrency": 100 }
```

## Retry Behavior

1. Message fails (exception or no ack/retry call)
2. Message retried after `retry_delay`
3. After `max_retries`:
   - Sent to `dead_letter_queue` (if configured)
   - Otherwise deleted

## Dead Letter Queue

```jsonc
{
  "queues": {
    "consumers": [
      {
        "queue": "my-queue",
        "max_retries": 5,
        "dead_letter_queue": "my-dlq"
      }
    ]
  }
}
```

DLQ requires separate consumer to process failures.

## Multiple Consumers

A queue can have only ONE consumer. To fan-out:

```typescript
// Single consumer fans out to multiple queues
await Promise.all([env.QUEUE_A.send(message), env.QUEUE_B.send(message), env.QUEUE_C.send(message)]);
```

## Pause/Resume

```bash
wrangler queues pause-delivery my-queue
wrangler queues resume-delivery my-queue
```

Messages queue but don't deliver when paused.
