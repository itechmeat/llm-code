# Components (Agents UI)

Compressed operator reference for LiveKit Agents UI components.

This consolidates:

- Agents UI section pages: https://docs.livekit.io/frontends/agents-ui/
- Agents UI component reference: https://docs.livekit.io/reference/components/agents-ui/

## Install model (shadcn registry)

Agents UI follows the shadcn pattern: you install components _into your repo as source_.

```bash
npx shadcn@latest init
npx shadcn@latest registry add @agents-ui
npx shadcn@latest add @agents-ui/{component-name}
```

Installed code typically lands in `components/agents-ui/`.

Practical pattern:

- Install only what you need (keeps diffs and maintenance manageable).
- Treat installed components as _your_ code: review, adjust styling, and pin upgrades intentionally.

## Runtime assumptions (React)

Most components assume you have an active agent session context.

- `AgentSessionProvider` supplies session/room context.
- `useAgent()` (from `@livekit/components-react`) commonly provides:
  - `audioTrack` (for visualizers)
  - `state` (agent state, e.g. connecting/listening/thinking/speaking)

If you render Agents UI components outside the provider, expect missing track/state and “nothing happens” failure modes.

## Session management

- `AgentSessionProvider`
  - Use: wrap the part of your app that renders chat/visualizers/controls.
- `AgentDisconnectButton`
  - Use: explicit “end session / leave room” action.
- `StartAudioButton`
  - Use: satisfy browser autoplay restrictions (needs a user gesture before audio playback).
  - Symptom when missing: user connects but cannot hear the agent until they click somewhere else.

Minimal “make audio work” pattern:

1. Render `StartAudioButton` early.
2. Ensure users can click it (don’t hide it behind overlays).

## Media controls

Goal: user control over mic/camera and session lifecycle.

- `AgentControlBar`
  - Use: fastest path (pre-styled all-in-one control bar).
  - When: you want standard controls without composing your own UI.
  - Key props (shown in docs demos):
    - `variant`
    - `isChatOpen`, `isConnected`
    - `controls`: `microphone`, `camera`, `screenShare`, `chat`, `leave`

Minimal example:

```tsx
import { AgentControlBar } from "@/components/agents-ui/agent-control-bar";

export function Controls() {
  return <AgentControlBar controls={{ microphone: true, leave: true }} />;
}
```

- `AgentTrackControl`
  - Use: per-track control (often includes device selection) for custom layouts.
- `AgentTrackToggle`
  - Use: simplest on/off toggle for a track (mic/camera) when you do not need device selection.

Rule of thumb:

- Need “one row of controls” quickly → `AgentControlBar`.
- Need custom layout + device selection → `AgentTrackControl`.
- Need a single toggle button → `AgentTrackToggle`.

## Chat

Goal: show realtime conversation.

- `AgentChatTranscript`
  - Use: transcript UI for speech transcriptions + text messages.
  - Behavior: updates in realtime; intended to work inside `AgentSessionProvider` without manual data plumbing.
- `AgentChatIndicator`
  - Use: “thinking/typing/processing” indicator driven by agent state.
  - UX: give feedback during pauses (tool calls, long generations, etc.).

## Audio visualizers (prebuilt)

Goal: give the agent a visible “presence” driven by audio + agent state.

Components:

- `AgentAudioVisualizerBar`
- `AgentAudioVisualizerGrid`
- `AgentAudioVisualizerRadial`
- `AgentAudioVisualizerWave`
- `AgentAudioVisualizerAura`

“Best for” guidance (from the docs):

- Bar: clean/minimal; configurable bar count/size.
- Grid: compact + subtle pulsing pattern.
- Radial: centered, prominent agent display.
- Wave: horizontal/inline layouts.
- Aura: premium/immersive look.

Common wiring pattern (React):

- Obtain `audioTrack` + `state` from `useAgent()`.
- Pass them to the visualizer as props.
- Typical shared props: `audioTrack`, `state`, `size` (+ component-specific props like `barCount`).

Minimal example (React):

```tsx
"use client";

import { useAgent } from "@livekit/components-react";
import { AgentAudioVisualizerBar } from "@/components/agents-ui/agent-audio-visualizer-bar";

export function Visualizer() {
  const { audioTrack, state } = useAgent();
  return <AgentAudioVisualizerBar size="lg" barCount={5} state={state} audioTrack={audioTrack} />;
}
```

## Audio visualizers (custom)

Goal: bespoke shader-based effects that react to audio volume + agent state.

Practical approach:

1. Start from an existing visualizer (often Aura) and modify it.
2. Keep layers separate:
   - React component props (`state`, `audioTrack`, `size`, `color`, …)
   - animation hook (smooth transitions between agent states)
   - shader (GLSL fragment shader)
3. Drive intensity from audio volume when the agent is speaking.

Start point used by the docs:

```bash
pnpm dlx shadcn@latest add @agents-ui/agent-audio-visualizer-aura
```

What you typically edit:

- A component under `components/agents-ui/` (owns props + passes uniforms)
- A hook under `hooks/agents-ui/` (owns animated values + state transitions)
- A shader renderer (`ReactShaderToy`) + GLSL fragment shader source

Key implementation notes (from the docs):

- Shaders follow a ShaderToy-style `mainImage` function.
- `ReactShaderToy` injects common uniforms like `iTime` and `iResolution`.
- Add _custom_ uniforms from React via a `uniforms` object.
- Animate uniform values when agent `state` changes, and optionally update intensity from live volume.

Uniform type cheat sheet (as shown):

- `1f` → float
- `3f` / `3fv` → vec3
- `Matrix4fv` → mat4

Supporting utility:

- `ReactShaderToy`
  - Use: render a fragment shader with uniforms passed from React.

## Blocks / templates

These are higher-level starting points referenced by the docs.

- `AgentSessionView` (block)
  - Use: a prebuilt session-oriented layout you can copy and adapt.

## Next.js helper

- NextJS API Token Route
  - Use: a template/route pattern referenced by the docs for token-related API needs in Next.js.
  - Treat it as a starting point; wire it to your auth model and keep tokens off the client.

## Minimal “what to install” cheat sheet

- Voice-only UI: `StartAudioButton` + `AgentControlBar` + one visualizer + (optional) chat transcript
- Chat-first UI: `AgentChatTranscript` + `AgentChatIndicator` + `AgentDisconnectButton`
- Custom layout: `AgentTrackToggle`/`AgentTrackControl` + `AgentDisconnectButton` + `StartAudioButton`
