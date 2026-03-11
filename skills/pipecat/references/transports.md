# Transports

Transports handle connectivity, media IO, and session state.

## Pipeline integration

Transports typically expose two processors:

- `transport.input()` to inject user media frames into the pipeline
- `transport.output()` to send bot media frames back to the user

You do not have to put `transport.output()` as the final processor. Placing processors after output enables tightly synchronized work (recording, subtitles, timing-aligned context updates).

## When to choose which

- **WebRTC**: best for production voice UX (latency, jitter handling, audio quality).
- **WebSocket**: good for server↔server, prototypes, and simpler integration.
- **Direct provider realtime**: connects the transport directly to a provider’s realtime endpoint (useful for fast prototyping).

## Examples mentioned in docs

- **DailyTransport (WebRTC)**
  - “Production-ready” WebRTC transport.
  - Often connects using `{ url, token }` returned from a start endpoint.

- **SmallWebRTCTransport**
  - Lightweight peer-to-peer WebRTC.
  - Typically used with a matching server implementation.

- **WebSocketTransport**
  - WebSocket-based transport.
  - Can use different serializers (the docs mention Protobuf and Twilio-oriented serialization).

- **OpenAIRealtimeWebRTCTransport**
  - WebRTC directly to OpenAI Realtime (construct with an API key + session config).

- **GeminiLiveWebsocketTransport**
  - WebSocket transport to Gemini Live / multimodal realtime (API key + generation config).

The Learn guide also calls out additional transports you may encounter:

- LiveKit-based WebRTC transports
- FastAPI-oriented websocket transports for telephony/webhooks
- Video/avatar generation transports (e.g., HeyGen, Tavus)

## Common configuration surface

The Learn guide describes a shared `TransportParams` structure with flags for:

- audio in/out enablement
- video in/out enablement
- video output sizing / bitrate / framerate

Transport-specific parameter types may extend this base.

## Daily transport updates (0.0.105)

- `DailyParams` can publish custom video tracks via `video_out_destinations`, mirroring the existing multi-destination audio model.
- Daily recording supports a `cloud-audio-only` mode when you need cloud recording without storing video.

Use these options when the bot needs to publish more than one visual stream or when compliance/cost requirements make audio-only recording preferable.

## Telephony over WebSocket

Telephony providers typically stream media over WebSockets using provider-specific framing/serialization.

Docs mention provider serializers for:

- Twilio
- Telnyx
- Plivo
- Exotel

Implementation tip: treat provider credentials as required configuration and fail fast if they are missing (avoid empty-string fallbacks).

## Multi-transport bots (selection by runner args)

The Learn guide shows a practical pattern:

- The bot entry point receives runner arguments that describe the connection type.
- Construct the correct transport implementation based on those args.
- Then run the same pipeline logic regardless of transport.

## Operational gotchas

- Model the transport as a state machine; do not start streaming audio until the bot is “ready”.
- Buffer local audio until the bot is ready if the transport supports it.
- Prefer a server “start” endpoint that creates the transport session and returns connection params to the client.

## WebRTC vs WebSocket (rules of thumb)

- Prefer **WebRTC** for client applications: better resilience, built-in audio processing, and quality telemetry.
- Prefer **WebSocket** for telephony and server-to-server; expect to implement more reconnection/timestamping/observability yourself.
