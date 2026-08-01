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

- **MOQTransport (`1.6.0`)**
  - Media over QUIC (MoQ) transport: bidirectional, low-latency audio + RTVI over QUIC instead of WebRTC/WebSocket.
  - Install with `pip install "pipecat-ai[moq]"`.
  - By default the bot runs as its own MoQ server (`serve=True`) and accepts the browser's direct connection, so local dev does not need a separate `moq-relay` process; dialing an external relay in client mode is wired up but not yet enabled.
  - Audio rides a single Opus track; RTVI messages (including the transcript) ride a compressed, ordered JSON stream track, putting MoQ on par with the Daily and WebSocket transports for RTVI support.
  - See `examples/transports/transports-moq.py`.

The Learn guide also calls out additional transports you may encounter:

- LiveKit-based WebRTC transports
- Vonage Video Connector transport for real-time Vonage WebRTC sessions
- FastAPI-oriented websocket transports for telephony/webhooks
- Video/avatar generation transports (e.g., HeyGen, Tavus)

## Common configuration surface

The Learn guide describes a shared `TransportParams` structure with flags for:

- audio in/out enablement
- video in/out enablement
- video output sizing / bitrate / framerate

Transport-specific parameter types may extend this base.

Migration note for `1.0.0`: deprecated transport-level VAD/turn parameters are gone, and the older `camera_*` compatibility params were removed in favor of the `video_in_*` / `video_out_*` names.

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
- Do not keep transport-specific workarounds for interruption/VAD behavior if you are upgrading; that policy now belongs with user-turn aggregation.

## WebRTC vs WebSocket (rules of thumb)

- Prefer **WebRTC** for client applications: better resilience, built-in audio processing, and quality telemetry.
- Prefer **WebSocket** for telephony and server-to-server; expect to implement more reconnection/timestamping/observability yourself.
- In `1.3.0`, the development runner can expose a plain WebSocket `/ws-client` endpoint alongside WebRTC/Daily/telephony. Use it for non-telephony clients, but keep production readiness checks and auth around the custom runner surface.
