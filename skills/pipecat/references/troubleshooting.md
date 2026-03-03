# Troubleshooting

## First steps

- Check agent logs for the specific session.
- Confirm your transport credentials and room/session creation.
- Verify secrets exist in the same region as the agent.

## Common Pipecat Cloud errors (from docs)

- Missing/invalid API key
- Billing not set
- Image not found / unauthorized to pull image / rate limited pulls
- Image too large
- Wrong image platform (docs say `linux/arm64`)
- Agent at capacity (HTTP 429)

## Logging

Docs mention an environment variable to control log verbosity (levels like TRACE/DEBUG/INFO/WARNING/ERROR/NONE).

## Pipelines that don’t terminate

Learn docs warn about a common bug:

- A custom frame processor that does not propagate frames can block termination frames.

If shutdown hangs, verify that every custom processor pushes frames onward (including end/cancel signals).

Also note the framework can use idle timeouts as a safety net; if your sessions are terminating unexpectedly, double-check idle timeout configuration.

## Capacity & cold starts

- If `min_agents = 0`, be ready for cold starts.
- Use `min_agents` to keep warm capacity for low-latency UX.
- Treat 429 “at capacity” as a normal operational response.
