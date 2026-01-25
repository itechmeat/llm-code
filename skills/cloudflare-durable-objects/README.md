# Cloudflare Durable Objects Skill

This skill provides guidance for working with Cloudflare Durable Objects stateful serverless platform.

## Topics Covered

- DurableObject class structure
- DurableObjectState interface
- Storage API (SQLite and KV backends)
- SQL queries and transactions
- WebSocket hibernation
- Alarms for scheduled tasks
- RPC methods
- Bindings and migrations
- Initialization patterns
- Hibernation lifecycle
- Limits and pricing

## When to Use

- Stateful serverless applications
- Real-time collaborative apps
- WebSocket servers with many connections
- Coordination between clients
- Strong consistency requirements
- Session management
- Rate limiting per entity

## When NOT to Use

- Stateless request/response (use Workers)
- Global shared state (use KV or D1)
- Simple scheduled tasks (use Cron Triggers)
- Message queuing (use Queues)

## Related Skills

- [cloudflare-workers](../cloudflare-workers/SKILL.md) — Worker development
- [cloudflare-d1](../cloudflare-d1/SKILL.md) — D1 database
- [cloudflare-kv](../cloudflare-kv/SKILL.md) — Global KV store
- [cloudflare-workflows](../cloudflare-workflows/SKILL.md) — Durable execution
- [cloudflare-queues](../cloudflare-queues/SKILL.md) — Message queues
