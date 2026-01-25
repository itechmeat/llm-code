# Cloudflare Workers KV Skill

This skill provides guidance for working with Cloudflare Workers KV key-value storage.

## Topics Covered

- Namespace creation and management
- Workers Binding API (get/put/delete/list)
- Metadata storage
- Key expiration (TTL)
- Cache TTL optimization
- Bulk operations (Wrangler/REST API)
- Consistency model and limitations
- Pricing and limits

## When to Use

- Caching API responses
- Storing user configurations/preferences
- Session storage
- Feature flags
- Static data with high read volume

## When NOT to Use

- Need strong consistency (use Durable Objects)
- Need atomic operations (use Durable Objects)
- Need > 1 write/sec to same key (use Durable Objects)
- Need relational data (use D1)

## Related Skills

- [cloudflare-workers](../cloudflare-workers/SKILL.md) — Worker development
- [cloudflare-durable-objects](../cloudflare-durable-objects/SKILL.md) — Strong consistency
- [cloudflare-d1](../cloudflare-d1/SKILL.md) — SQL database
- [cloudflare-r2](../cloudflare-r2/SKILL.md) — Object storage
