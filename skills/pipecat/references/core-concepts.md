# Core concepts & architecture (Pipecat)

## Why voice AI is hard (what Pipecat abstracts)

Real-time voice bots need tight coordination across multiple streaming subsystems:

- Speech recognition (STT) while the user is speaking
- LLM generation with evolving context
- Speech synthesis (TTS) that can start early for low latency
- A transport that streams audio with minimal delay, buffering, and robust reconnect/error behavior

## Key concepts

- **Pipecat**: Python framework for real-time voice and multimodal bots.
- **RTVI**: a message/event standard used between clients and servers for real-time multimedia + LLM interactions.
- **Pipeline**: chain of processors (STT, LLM, TTS, aggregators, observers, transports).
- **Frame**: the unit flowing through the pipeline (audio, text, context, events).
- **Transport**: manages media devices, connectivity, transmission, and lifecycle state.

## Frames, processors, pipelines (one-liners)

- **Frames** are typed “data packets” (audio chunks, transcripts, LLM output, synthesized audio, events).
- **Frame processors** are single-purpose workers that transform frames (audio → text, text → audio, etc.).
- **Pipelines** connect processors so frames flow and orchestration happens automatically.

## Typical runtime architecture

A common pattern is **two processes**:

- **Bot runner** (HTTP service)
  - Receives “start session” requests from clients
  - Creates/allocates a transport session (e.g., a WebRTC room)
  - Spawns a **bot process** with transport credentials
  - Returns connection parameters to the client

- **Bot process**
  - Connects to the transport
  - Runs the pipeline
  - Exchanges RTVI messages/events with the client

## Transport lifecycle (high-level)

Transports typically model a state machine. The docs list states like:

- Disconnected → Initializing → Initialized → Authenticating → Authenticated → Connecting → Connected → Ready
- Disconnecting / Error

## Best practices

- Keep provider keys server-side; client should only receive transport credentials.
- Use a start endpoint to initialize bot context (prompt/config) before connecting.
- Prefer WebRTC transports for production voice apps.
