# OpenClaw Nodes

## Node role and boundary

- Nodes are companion executors connected to gateway WebSocket with role `node`.
- Nodes do not host channels or gateway state; they expose command capabilities only.
- Gateway remains the orchestration authority and routes node invocations.

## Pairing and lifecycle

- Node devices require explicit pairing approval for trusted operation.
- Use device/node status and describe commands to validate capability visibility.
- Distinguish transport pairing/trust from node-specific approval stores.

## Execution model

- Gateway model loop decides when node commands are invoked.
- Node host executes system commands locally when `host=node` execution is selected.
- Exec approvals are enforced on node host and should be managed as per-host policy.

## Capability families

- Canvas/A2UI interaction and rendering commands.
- Camera, screen recording, and location capture commands.
- System execution and notification commands.
- Optional platform-specific capabilities (for example SMS on Android nodes).

## Android node surface expansion (v2026.3.1)

Recent Android nodes expose additional command families commonly used in automation runs:

- `device.permissions`, `device.health`
- `notifications.actions` (`open` / `dismiss` / `reply`)
- `system.notify`
- `photos.latest`
- `contacts.search`, `contacts.add`
- `calendar.events`, `calendar.add`
- `motion.activity`, `motion.pedometer`

## Pending work queue primitives (v2026.3.11)

- Gateway exposes `node.pending.enqueue` and `node.pending.drain` as narrow in-memory primitives for pending work delivery to dormant or waking nodes.
- Treat them as gateway-coordinated queue helpers, not as durable job storage.
- If node wake/reconnect flows are flaky, inspect pending-work behavior alongside APNs/push signaling before blaming the node executor itself.

## Safeguards

- Keep explicit allowlists for high-risk system execution.
- Validate node foreground/permission constraints before media commands.
- Use dedicated node display names and stable IDs for repeatable routing.
- Treat node pairing and access like operator-level trust.
