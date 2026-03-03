# Session initialization (runner, bot, client)

This page adds practical guidance for how users and bots connect before any audio can flow.

## Roles

- **Runner**: an HTTP server (docs use FastAPI) that accepts connection/start requests and coordinates session setup.
- **Bot**: your Pipecat pipeline code, typically started as a separate server-side process.
- **Client**: the user app (web/mobile) that captures audio and connects via a transport.

## Recommendation: start with the development runner

Docs describe a built-in “development runner” that:

- Spins up the HTTP server and endpoints for you
- Manages connection setup and bot process lifecycle
- Can provide a web UI for WebRTC flows

Your bot exposes a single async entry point that receives runner arguments (including transport connection info), then you create the appropriate transport and run your pipeline.

## Connection patterns (under the hood)

### 1) P2P WebRTC

- Runner serves a local client page.
- The browser generates a WebRTC offer.
- Runner starts the bot and passes the negotiated connection.
- Browser and bot exchange audio directly over WebRTC.

Use when: local development, direct browser-to-bot experiments.

### 2) Room-based WebRTC (Daily)

- Runner creates a room + token via Daily API.
- Both the client and the bot join the same room.
- A handshake event (client readiness) indicates the client can receive the first bot messages.

Use when: production deployments, richer call scenarios.

### 3) WebSocket (telephony)

- A telephony provider connects to your runner’s websocket/webhook.
- Runner parses provider-specific frames/messages.
- Bot starts immediately with the parsed connection data.

Use when: phone bots and PSTN/SIP integrations.

## Starting the conversation: timing matters

Docs distinguish:

- **Immediate start** (P2P WebRTC / WebSocket): you can start the LLM run once the client is connected.
- **Handshake-required start** (room-based client/server): wait for a “client ready” signal, then mark the bot ready and start the first turn.

If you start too early in a room-based flow, the client may miss the beginning of the bot’s first message.

## Process isolation (one bot per session)

Docs recommend per-session bot instances for:

- Resource management (CPU/memory per session)
- Failure isolation
- Cleaner teardown

## When to build a custom runner

Use a custom runner when you need:

- Custom auth or endpoints
- Deeper integration with an existing backend
- Non-standard session lifecycle

Docs suggest using the development runner’s source code as a reference, since it handles real-world edge cases.
