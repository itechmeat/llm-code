# CLI (pipecat / pc)

Pipecat provides a CLI for scaffolding projects (`init`), monitoring sessions (`tail`), and operating Pipecat Cloud deployments (`cloud`).

For installation, see: `references/installation.md`.

Verify:

- `pipecat --version`

Help:

- `pipecat --help`
- `pipecat init --help`
- `pipecat tail --help`
- `pipecat cloud --help`

Notes:

- Commands support both `pipecat` and the shorter `pc` alias.
- Requires Python 3.10+.

## `pipecat init`

Scaffolds a new Pipecat project (server bot, optional web client, optional cloud deploy config).

### Typical outputs

A generated project commonly includes:

- `server/` (Python bot)
  - `bot.py`
  - `pyproject.toml`
  - `.env.example`
  - `Dockerfile` (when cloud deploy files are enabled)
  - `pcc-deploy.toml` (when cloud deploy files are enabled)
- `client/` (optional)
  - `package.json`, `src/`, etc.
- Top-level helpers
  - `.gitignore`, `README.md`

### Modes

- Interactive: run `pipecat init` without `--name` / `--config`.
- Non-interactive: provide `--name` or `--config` (JSON). If required fields are missing, the command reports what’s missing.

### Useful flags (selected)

- Output and naming
  - `--output/-o <dir>`
  - `--name/-n <name>`
- Bot shape
  - `--bot-type/-b web|telephony`
  - `--transport/-t <provider>` (repeatable)
  - `--mode/-m cascade|realtime`
- Cascade services (STT/LLM/TTS)
  - `--stt <service>`
  - `--llm <service>`
  - `--tts <service>`
- Realtime service (realtime mode)
  - `--realtime <service>`
- Web client (web bots)
  - `--client-framework react|vanilla|none`
  - `--client-server vite|nextjs`
- Telephony-specific
  - `--daily-pstn-mode dial-in|dial-out`
  - `--twilio-daily-sip-mode dial-in|dial-out`
- Feature toggles (examples)
  - `--recording/--no-recording`
  - `--transcription/--no-transcription`
  - `--smart-turn/--no-smart-turn`
  - `--observability/--no-observability`
- Cloud scaffolding
  - `--deploy-to-cloud/--no-deploy-to-cloud`
  - `--enable-krisp/--no-enable-krisp` (cloud-related)
- Discovery/debug
  - `--list-options` (prints available services/options as JSON and exits)
  - `--dry-run` (prints resolved config JSON without generating files)

### Examples

- Interactive wizard:
  - `pipecat init`

- Non-interactive (cascade):
  - `pipecat init --name my-bot --bot-type web --transport daily --mode cascade --stt deepgram_stt --llm openai_llm --tts cartesia_tts`

- Non-interactive (realtime):
  - `pipecat init --name rt-bot --bot-type web --transport smallwebrtc --mode realtime --realtime openai_realtime`

## `pipecat tail`

Tail is a terminal dashboard to monitor Pipecat sessions in real time (logs, conversation, metrics/usage, audio levels).

### Requirements

- Add an observer to your server-side pipeline task:
  - `from pipecat_cli.tail import TailObserver`
  - `PipelineTask(..., observers=[TailObserver()])`

### Usage

- Start Tail:
  - `pipecat tail`
- Connect to a remote session:
  - `pipecat tail --url wss://my-bot.example.com`

Selected flag:

- `--url/-u <ws-url>`
  - Default: `ws://localhost:9292`

## `pipecat cloud`

Pipecat Cloud commands cover authentication, deployments, secrets, regions, and agent operations.

### Auth (`pipecat cloud auth`)

- `pipecat cloud auth login` (supports `--headless/-h` for remote/container environments)
- `pipecat cloud auth logout`
- `pipecat cloud auth whoami`

Config storage:

- Default path: `~/.config/pipecatcloud/pipecatcloud.toml`
- Override path with `PIPECAT_CONFIG_PATH`
- View effective config with: `pipecat cloud --config`

### Organizations (`pipecat cloud organizations`)

- `pipecat cloud organizations list`
- `pipecat cloud organizations select` (or `--organization/-o <org>`)

Notes:

- The currently selected organization is stored in the local config and used by default.
- Org/user management is not available via the CLI (use the dashboard).

### Regions (`pipecat cloud regions`)

- `pipecat cloud regions list`

Use the region code with other commands (deploy/agent/secrets). Keep secrets in the same region as the agents that consume them.

### Secrets (`pipecat cloud secrets`)

- List sets / keys:
  - `pipecat cloud secrets list`
  - `pipecat cloud secrets list <set-name>`
- Create/update a secret set:
  - `pipecat cloud secrets set <set-name> KEY=value ...`
  - `pipecat cloud secrets set <set-name> --file .env`
- Delete key or set:
  - `pipecat cloud secrets unset <set-name> <key>`
  - `pipecat cloud secrets delete <set-name>`
- Create image pull credentials (used by deploy):
  - `pipecat cloud secrets image-pull-secret <name> <host> [user:pass]`

Notes:

- Listing shows keys, not values.
- Prefer `--file` to avoid leaking secrets via shell history.

### Deploy (`pipecat cloud deploy`)

- Deploy/update an agent:
  - `pipecat cloud deploy <agent-name> <image>`

Selected options:

- `--credentials/-c <image-pull-secret-name>`
- `--secrets/-s <secret-set-name>`
- `--min-agents/-min <n>` / `--max-agents/-max <n>`
- `--profile/-p agent-1x|agent-2x|agent-3x`
- `--region/-r <code>`
- `--force/-f`

Config file support:

- `pcc-deploy.toml` (auto-detected in the current directory)
- Precedence: CLI args > `pcc-deploy.toml` > defaults.

Krisp note:

- Legacy `enable_krisp` is documented as deprecated in favor of `krisp_viva` config.

### Docker helper (`pipecat cloud docker`)

- Build and push using `pcc-deploy.toml`:
  - `pipecat cloud docker build-push`

Selected options:

- `--version/-v <tag>`
- `--no-push`
- `--no-latest`
- Registry overrides: `--registry`, `--registry-url`, `--username`

Platform:

- Docs state images are built for `linux/arm64` for Pipecat Cloud.

### Agent ops (`pipecat cloud agent`)

Core subcommands:

- `start` (supports `--data` JSON, `--use-daily`, `--daily-properties`)
- `stop` (requires `--session-id`)
- `status`
- `deployments` (deployment history)
- `logs` (filter by `--level`, `--deployment`, `--session-id`, `--limit`)
- `list` (supports `--region` and `--organization`)
- `sessions` (can show detailed metrics with `--id`)
- `delete` (irreversible; supports `--force`)
