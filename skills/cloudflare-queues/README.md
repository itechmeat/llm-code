# Cloudflare Queues Skill

This skill provides guidance for working with Cloudflare Queues message queue service.

## Topics Covered

- Queue creation and management
- Producer API (send, sendBatch)
- Consumer API (queue handler, ack, retry)
- Message batching and timeouts
- Dead Letter Queues (DLQ)
- Delivery delay and backoff
- Consumer concurrency
- Pull consumers (HTTP API)
- Pricing and limits

## When to Use

- Decoupling Workers for async processing
- Background job processing
- Event-driven architectures
- Rate limiting / throttling workloads
- R2 event processing
- Fan-out patterns

## When NOT to Use

- Need exactly-once delivery (implement idempotency)
- Need real-time pub/sub (consider WebSockets)
- Need message ordering guarantees

## Related Skills

- [cloudflare-workers](../cloudflare-workers/SKILL.md) — Worker development
- [cloudflare-r2](../cloudflare-r2/SKILL.md) — R2 event notifications
- [cloudflare-durable-objects](../cloudflare-durable-objects/SKILL.md) — State management
- [cloudflare-kv](../cloudflare-kv/SKILL.md) — Idempotency keys
