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

## Safeguards

- Keep explicit allowlists for high-risk system execution.
- Validate node foreground/permission constraints before media commands.
- Use dedicated node display names and stable IDs for repeatable routing.
- Treat node pairing and access like operator-level trust.
