# OpenClaw Configuration and Workspace Bootstrap

## Operator mental model for `openclaw.json`

Treat the config as six blocks that should be reviewed in order:

1. `gateway`
2. `agents`
3. `channels`
4. `bindings`
5. `session` and `messages`
6. `heartbeat`, `tools`, `cron`, and `hooks`

This keeps debugging local: gateway issues first, routing next, then behavior/policy.

## Config format and validation

- The main config is typically `~/.openclaw/openclaw.json`.
- OpenClaw uses strict schema validation; unknown keys, wrong types, and malformed structure should be treated as startup blockers.
- Run `openclaw config validate` before restart/reload after manual edits.
- If you are unsure whether a change hot-applies, validate first and then use `openclaw gateway restart` instead of guessing.

## Includes and composition

- Use `$include` to split large configs into logical files such as agents and channels.
- Keep include boundaries stable so operators know where to look during incidents.
- Prefer composition for multi-agent or multi-channel deployments instead of one oversized config blob.

Example shape:

```json5
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  channels: { $include: "./channels.json5" },
}
```

## Secrets and environment sources

- Environment variables can come from the process, a local `.env`, or `~/.openclaw/.env`.
- Do not hardcode channel tokens or provider secrets when an env-based path is available.
- After changing secret sources, rerun validation and health checks before testing channels.

## Hot-reload vs restart boundaries

- Runtime behavior such as agents, channels, heartbeat, messages, and some tools settings often hot-apply.
- Gateway server settings such as bind, port, and related HTTP exposure should be treated as restart-bound unless verified otherwise.
- When rollout safety matters more than speed, prefer an explicit restart and status check over assuming live reload.

## Local-model lean mode (v2026.4.15)

- `agents.defaults.experimental.localModelLean: true` drops heavyweight default tools such as `browser`, `cron`, and `message` for weaker local-model deployments.
- Treat this as an opt-in low-context profile for constrained local runtimes, not as the normal default for strong hosted models.

## Workspace bootstrap files

Common workspace/bootstrap surfaces include:

- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `IDENTITY.md`
- `MEMORY.md`
- `memory/YYYY-MM-DD.md`

These files are part of the agent context surface. Keep them short, current, and role-specific.

## Memory backend updates (v2026.4.15)

- `memory-lancedb` can now store durable indexes on cloud object storage instead of local disk only.
- Dreaming now defaults to `separate` storage mode; Dreaming phase files go under `memory/dreaming/...` instead of inflating the daily memory file.
- If you want the old inline behavior, set the corresponding dreaming storage mode explicitly instead of assuming the legacy default.

## Heartbeat guidance

- Do not enable proactive heartbeat just because the feature exists.
- Add a clear `HEARTBEAT.md` contract first, including when to stay silent.
- Use lightweight context for heartbeat when bootstrap files are large.
- Give each agent its own heartbeat settings in multi-agent deployments.

## Safe initial tool posture

- Start from least privilege and open up only the tools you need.
- `tools.deny` is a practical way to block high-risk surfaces such as browser automation or canvas while the deployment is still being proven.
- Revisit tool policy after channel trust, allowlists, and routing rules are stable.
