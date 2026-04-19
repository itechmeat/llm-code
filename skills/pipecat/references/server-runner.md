# Server Utilities: runner (development runner + transport utils)

## What a runner is

Server docs describe a “bot runner” as an HTTP gateway that:

- creates transport sessions (rooms/tokens)
- spawns a bot process per user session
- passes connection details to the bot
- manages lifecycle and cleanup

## Development runner: why it matters

- Lets you run the same bot logic across multiple transports.
- Handles setup for WebRTC (local), Daily rooms/tokens, and telephony webhooks.
- Encourages a pattern: keep core bot logic transport-agnostic, create the transport in the entry point based on runner args.
- `1.0.0` exports a module-level FastAPI `app` from the development runner, so you can register custom routes/middleware before calling `main()`.

## Installation (extras)

Runner support is provided via the `pipecat-ai[runner]` extra.
See: `references/installation.md`.

## CLI patterns

Docs show a single entry point you run with transport selection flags:

- WebRTC local: `-t webrtc`
- Daily rooms: `-t daily`
- Telephony: `-t twilio|telnyx|plivo|exotel` (requires a public proxy hostname)

The runner also documents extra switches for direct Daily testing and dial-in webhook handling.

## Runner arguments (what your bot receives)

The runner passes transport-specific data to the bot entry point, e.g.:

- Daily room URL and token
- WebRTC connection object
- WebSocket stream for telephony

Implementation note: some signal-handling args are development-only and not available on Pipecat Cloud.

## Built-in endpoints and RTVI `/start`

Docs mention an RTVI-compatible `POST /start` endpoint for Daily flows that:

- creates room + token
- spawns a bot instance with request body data
- returns connection info to the client

Use this pattern to keep provider secrets on the server.

## Transport utilities (for custom runners)

Docs describe utilities for advanced setups:

- `create_transport(runner_args, transport_params)`: build the correct transport without manual conditionals
- `parse_telephony_websocket(websocket)`: detect provider from initial messages and extract call/session data
- daily/livekit `configure()` helpers to create rooms and tokens
- helper functions to get transport-specific client ids and optionally capture participant camera/screen when supported

## Practical checklist

- Start with the development runner, then build a custom runner only if you need custom auth/endpoints.
- Treat telephony/provider credentials as required configuration; validate them explicitly.
- Use lazy imports inside transport-specific branches to keep optional dependencies truly optional.
