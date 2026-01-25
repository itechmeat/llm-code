# Cloudflare Workflows Skill

This skill provides guidance for working with Cloudflare Workflows durable execution platform.

## Topics Covered

- WorkflowEntrypoint class structure
- Step creation and configuration
- State persistence patterns
- Sleep and scheduling (step.sleep, step.sleepUntil)
- Wait for external events (waitForEvent, sendEvent)
- Retry configuration and backoff
- Error handling (NonRetryableError)
- Workflow bindings (create, get, pause, resume, terminate)
- Batch instance creation
- Instance lifecycle management
- Limits and pricing

## When to Use

- Multi-step processes that need durability
- Long-running tasks (hours, days, weeks)
- Approval workflows with human-in-the-loop
- Saga pattern with compensating transactions
- Scheduled/delayed processing
- External event coordination

## When NOT to Use

- Simple request/response patterns (use Workers)
- Real-time processing without persistence needs
- Stateless transformations
- Tasks completing in milliseconds

## Related Skills

- [cloudflare-workers](../cloudflare-workers/SKILL.md) — Worker development
- [cloudflare-queues](../cloudflare-queues/SKILL.md) — Message queue triggers
- [cloudflare-r2](../cloudflare-r2/SKILL.md) — Store large state externally
- [cloudflare-kv](../cloudflare-kv/SKILL.md) — Store references
- [cloudflare-d1](../cloudflare-d1/SKILL.md) — Database queries in steps
