# Installation & setup

This reference is for the initial setup required to run LiveKit Agents locally or in production.

## Prerequisites

- A LiveKit Cloud project (or a self-hosted LiveKit server).
- LiveKit credentials available as environment variables:
  - `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `LIVEKIT_URL`
- Model/provider credentials as needed (for example, an `OPENAI_API_KEY`).

## SDK runtime

- Python: docs examples use Python >= 3.10 and `uv`.
- Node.js: docs examples use Node >= 20 and `pnpm`.

## Packages (from docs examples)

Pick the extras you actually need:

- Pipeline (STT/LLM/TTS) examples:
  - `livekit-agents[silero,turn-detector]~=1.4`
- Realtime model examples:
  - `livekit-agents[openai]~=1.4`
- MCP tooling (when you use MCP servers in Python):
  - `livekit-agents[mcp]~=1.4`

## Minimal local project bootstrap (Python-first)

- Create a bare project (docs examples use `uv`):
  - `uv init <project> --bare`
- Install the package extras you need (examples above), then run using the SDK “modes” described in `references/get-started.md` (for example `dev`, `start`, and `download-files` when plugins require assets).

## Operational tooling

- LiveKit CLI is used for cloud auth/deploy workflows.
- Docs note you typically authenticate your LiveKit Cloud project before deploying (for example via `lk cloud auth`).
