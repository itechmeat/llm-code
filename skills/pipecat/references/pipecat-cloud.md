# Pipecat Cloud (deploy, scaling, secrets)

Pipecat Cloud is the managed service described in the docs for deploying and operating bot images.

## Core objects

- **Agent image**: container image for your bot.
- **Agent pool**: a pool of instances used to serve sessions.
- **Session**: a running instance handling a user interaction.

## CLI (high-level)

See: `references/cli.md`.

## Accounts, orgs, and API keys

- Pipecat Cloud has personal workspaces (not suitable for collaboration) and **organizations** for team workflows.
- Many operations depend on the selected organization in your local config (or an explicit `--org` / `--organization` flag).

API keys:

- **Private API keys**: administrative/server-to-server use; should not be shared.
- **Public API keys**: suitable for starting sessions (still treat as sensitive; keep server-side in production).

## Base image and image constraints

The docs describe an official base image:

- `dailyco/pipecat-base` (multi-modal base image)
- Multiple Python tags; docs state default Python version changed to 3.12 starting at base image version 0.1.0.

Important constraints:

- Pipecat Cloud requires images built for `linux/arm64`.
- Avoid copying files to `/app` (reserved by the base image).

Reserved routes (base image):

- `POST /bot` (main session start entry point)
- `GET|WS /ws` (WebSocket endpoint)
- `POST /api/offer` + `PATCH /api/offer` (SmallWebRTC offer/ICE)

Useful env vars (selection):

- `PORT` (default 8080)
- `PIPECAT_LOG_LEVEL` (TRACE/DEBUG/INFO/WARNING/ERROR/NONE)
- `PCC_LOG_FEATURES_SUMMARY=true` (logs enabled features at startup)

## Deploy configuration

Pipecat Cloud deploys are typically driven by:

- CLI: `pipecat cloud deploy <agent-name> <image>`
- Config file: `pcc-deploy.toml` (CLI args override file values)

Agent profiles (resource sizing):

- `agent-1x`: 0.5 vCPU / 1GB (docs: best for voice agents)
- `agent-2x`: 1 vCPU / 2GB
- `agent-3x`: 1.5 vCPU / 3GB

## Scaling model

- `min_agents`: warm pool (reduces cold starts, increases reserved cost)
- `max_agents`: hard cap; at-capacity start requests can return HTTP 429
- Docs mention idle instances (when `min_agents=0`) are kept briefly (example: ~5 minutes) before scale-to-zero.

## Secrets (fundamentals)

- Secrets are stored in **secret sets** (key/value).
- Secret keys are mounted into the agent as environment variables.
- Secret sets are **region-specific** and must match the deployed agent region.
- Updating a secret set requires redeploying agents that use it to pick up the new values.

Image pull secrets:

- Needed for private registries; region-specific; typically created via `pipecat cloud secrets image-pull-secret`.
- Docs note image-pull secrets cannot be updated in-place (delete + recreate to rotate).

## Starting sessions (active sessions)

The docs describe three common ways to start sessions:

- REST (public start): `POST https://api.pipecat.daily.co/v1/public/{agent_name}/start` with `Authorization: Bearer PUBLIC_API_KEY`
- CLI: `pipecat cloud agent start <agent-name> --api-key pk_...` (can pass JSON data)
- Python SDK (`pipecatcloud`): `Session(...).start()` with `SessionParams(use_daily=..., data=..., daily_room_properties=...)`

Your agent receives arguments (examples in docs):

- `DailyRunnerArguments` (room_url, token, body, session_id)
- `WebSocketRunnerArguments` (websocket, body, session_id)

## Logging / observability (fundamentals)

- Docs note the logging/observability section is WIP, but call out:
  - `PIPECAT_LOG_LEVEL` to control verbosity
  - View logs via CLI: `pipecat cloud agent logs <agent>` (filter by level)
  - Session CPU/memory metrics available via dashboard and `pipecat cloud agent sessions --id <session-id>`
  - Use `loguru` so logs are associated to session IDs.

## Managed API keys

- A deployment can enable “managed keys” (`enable_managed_keys=true`).
- Docs show usage pattern where you pass the magic string `PIPECATCLOUD` as the API key (service-specific), and Pipecat Cloud supplies the managed key at runtime when no local env var is set.

## Error codes (selected)

Docs list error codes you should handle in automation and UIs:

- `PCC-1002`: start without public API key
- `PCC-1004`: billing not configured
- `PCC_INVALID_IMAGE_PLATFORM`: image not `linux/arm64`
- `PCC_IMAGE_PULL_UNAUTHORIZED`: private registry auth missing/invalid
- `PCC-AGENT-AT-CAPACITY`: pool at capacity (429)

## Deployment config file

Docs mention a `pcc-deploy.toml` with fields such as:

- Required: `agent_name`, `image`
- Optional: `region`, secret set and image credentials, agent profile
- Scaling: `min_agents`, `max_agents`

## Scaling model

- `min_agents`: warm reserved instances (lower latency, higher cost)
- `max_agents`: hard cap
- Expect short “idle instance creation delay”; design for bursts.

## Capacity handling

- Start API can return HTTP 429 when at capacity.
- Client code should treat capacity errors as a normal failure mode and retry/backoff or show UI.

## Secrets & regions

- Secret sets and image-pull secrets are region-specific.
- Keep secrets, image credentials, and the deployed agent in the same region.

## Image constraints

Docs explicitly mention building for `linux/arm64`.
