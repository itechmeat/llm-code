# Migration

## OpenClaw → PicoClaw

Use the CLI migrator:

- `picoclaw migrate` (auto-detect + prompt)

Common flags:

- `--dry-run` (preview)
- `--refresh` (re-sync workspace)
- `--config-only` / `--workspace-only`
- `--force`
- `--openclaw-home` / `--picoclaw-home`

## `providers` → `model_list`

`model_list` is the preferred model-centric config.

Benefits:

- Zero-code addition for OpenAI-compatible providers
- Load balancing (multiple entries with same `model_name`)
- Protocol-prefixed routing like `openai/`, `anthropic/`, `antigravity/`, `openrouter/`, `groq/`, `deepseek/`, `cerebras/`.

See also: `config.md`.
