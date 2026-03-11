# Quickstart (CLI + gateway)

## Install options

Pick one:

1. Prebuilt binary (recommended for users)

- Download a release artifact for your OS/arch.
- Run `picoclaw version` to confirm it starts.

2. Build from source (good for dev)

- `make deps`
- `make build` (binary goes to `picoclaw-main/build/`)
- `make install` (installs to `~/.local/bin/picoclaw` by default)

3. Docker Compose (gateway)

- Copy config and set tokens/keys.
- Start gateway profile.

## First run

1. Initialize config and workspace templates:

- `picoclaw onboard`

2. Edit config:

- File: `~/.picoclaw/config.json`
- Minimum: set an API key for at least one entry in `model_list` and select it via `agents.defaults.model_name`.

3. Sanity check:

- `picoclaw status`

## Talk to the agent (CLI)

- One-shot:
  - `picoclaw agent -m "Hello"`
- Interactive:
  - `picoclaw agent`
- Override model for one call:
  - `picoclaw agent -m "Hello" --model <model_name>`

## Run gateway

- Start:
  - `picoclaw gateway`
- Debug logs:
  - `picoclaw gateway --debug`

Gateway brings up:

- Channels (if enabled)
- Cron service + heartbeat service
- Health server: `http://<host>:<port>/health` and `/ready`

## Next

- See config details: `config.md`
- Enable a chat channel: `channels.md`
- Add a scheduled job: `cron.md`
- Configure auth (OAuth/token): `auth.md`

If you use the web frontend, v0.2.2 also improves launcher integration and adds agent-management UI, so upgrade first before troubleshooting mismatches between CLI state and the browser view.
