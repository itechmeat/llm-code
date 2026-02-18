# OpenClaw Architecture

## Operator summary

- OpenClaw centers around one long-lived Gateway process per host.
- The Gateway owns external messaging surfaces and provider connections.
- Clients and nodes connect to the Gateway via typed WebSocket protocol.
- The Gateway also serves HTTP endpoints for canvas/A2UI web surfaces.

## Core components

- Gateway: control plane, channel ownership, provider multiplexing, event source.
- Clients: macOS app, CLI, web/admin automations using request/response/event WS API.
- Nodes: role-specific workers advertising explicit capabilities and commands.
- Web surfaces: canvas and A2UI hosted under Gateway HTTP routes.

## Connection and protocol model

- Transport uses JSON text WebSocket frames.
- First frame must be `connect`; invalid first frame causes hard close.
- Requests use `req/res` correlation IDs and typed methods.
- Server pushes typed events (`agent`, `presence`, `health`, etc.).
- Side-effecting methods require idempotency keys for safe retries.

## Routing and execution model

- Messaging ingress is centralized in Gateway (single host authority).
- Agent and send operations are request-driven; updates stream by events.
- Nodes expose executable command namespaces (for example, canvas/media/device actions).
- Clients must handle non-replayed event streams and refresh state on sequence gaps.

## Security and trust constraints

- Optional gateway token auth applies to every connection.
- Device identity + pairing trust is required for new device IDs.
- Local endpoints may be auto-approved, remote endpoints require explicit trust flow.
- Remote setups should use VPN/Tailscale or SSH tunnel; enable TLS when exposed.

## Deployment notes

- Run exactly one Gateway per host to avoid channel/session conflicts.
- Keep Gateway supervised (launchd/systemd) and logs observable from stdout.
- Separate concerns: Gateway as orchestrator, nodes as capability executors.

## Do / Don’t

- Do treat Gateway as single source of truth for channel sessions.
- Do implement reconnect and dedupe behavior in client integrations.
- Don’t assume event replay exists.
- Don’t run multiple gateways for the same host-bound messaging sessions.

## Capability map (feature-level)

- Channel layer supports major messaging platforms through one gateway abstraction.
- Routing layer supports isolated multi-agent session handling.
- Interaction layer supports media I/O and long-response streaming.
- Surface layer includes Web Control UI, desktop companion, and mobile nodes with canvas workflows.
- Extension model allows additional channel/plugins beyond built-ins.

## Multi-agent routing rules

- Agents are isolated by workspace, state directory, credentials, and session store.
- Binding resolution is deterministic and prioritizes most-specific peer matches before broader channel/account rules.
- Peer-targeted rules override channel-wide defaults.
- Avoid shared agent directories across agents to prevent session/auth collisions.
