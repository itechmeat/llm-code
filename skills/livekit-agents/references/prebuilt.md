# Prebuilt components

## Prebuilt tasks (Beta, Python)

Docs list prebuilt tasks under `livekit.agents.beta.workflows`.

### What they are

- Ready-made tasks tuned for common voice workflows.
- You `await` them inside an agent (often triggered from a tool), or sequence them inside a `TaskGroup`.

### Tasks (from docs)

- **GetEmailTask**: collect + validate an email address (handles noisy voice transcription patterns).
- **GetAddressTask**: collect + validate a mailing address (supports international formats and spoken input).
- **GetDtmfTask**: capture keypad (DTMF) or spoken digits (IVR menus, PIN entry).
- **WarmTransferTask**: agent-assisted warm transfer (dial supervisor via SIP, hold music, handoff context).

### Customization knobs

- `extra_instructions`: append task-specific instructions/context.
- Some tasks accept `tools` to add/replace function tools used during completion.

## Prebuilt tools (Beta, Python)

Docs list prebuilt tools under `livekit.agents.beta.tools`.

- **EndCallTool**: gracefully end a call / disconnect from the room; can optionally delete the room and run “goodbye” instructions.
- **send_dtmf_events**: send DTMF tones to telephony providers (IVR navigation, keypad automation).

### Integration

- Add prebuilt tools to the agent’s `tools` list so the LLM can call them.

### Customization

- Tools expose constructor params like `extra_description` / `end_instructions` (refer to per-tool docs for exact params).
