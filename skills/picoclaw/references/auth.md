# Auth (OAuth / token store)

Credentials are stored in `~/.picoclaw/auth.json`.

## Commands

- Login:
  - `picoclaw auth login --provider openai`
  - `picoclaw auth login --provider openai --device-code` (headless)
  - `picoclaw auth login --provider anthropic` (paste token)
  - `picoclaw auth login --provider google-antigravity`

- Status:
  - `picoclaw auth status`

- List Antigravity models:
  - `picoclaw auth models`

- Logout:
  - `picoclaw auth logout --provider openai`

## Google Antigravity (headless note)

If browser redirect to `localhost:51121` can’t be reached (remote/VPS), the documented flow is:

- Run login.
- Open the printed URL locally.
- After consent, copy the final redirect URL (even if it fails to load) and paste it back into the terminal.

## What login updates

Auth commands may also patch `~/.picoclaw/config.json`:

- Set `providers.<name>.auth_method` for backward compatibility.
- Add/update a `model_list` entry with `auth_method`.
- Update `agents.defaults.model_name` to a sensible default for that provider.

## Troubleshooting

- `auth status` shows if tokens are expired or need refresh.
- If Antigravity returns empty/blocked responses, try a different model from `auth models`.
