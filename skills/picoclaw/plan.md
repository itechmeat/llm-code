# picoclaw skill — ingestion plan (local docs/code)

Snapshot:

- Source: `picoclaw-main/`
- Version basis: git describe returned `3488536` (no tags in this snapshot)
- Commit date: 2026-02-24

## Queue (ingest one file/folder at a time)

### Entry points

- [x] picoclaw-main/README.md
- [x] picoclaw-main/config/config.example.json
- [x] picoclaw-main/cmd/picoclaw/main.go (commands + version)

### CLI commands

- [x] picoclaw-main/cmd/picoclaw/cmd_onboard.go
- [x] picoclaw-main/cmd/picoclaw/cmd_agent.go
- [x] picoclaw-main/cmd/picoclaw/cmd_gateway.go
- [x] picoclaw-main/cmd/picoclaw/cmd_status.go
- [x] picoclaw-main/cmd/picoclaw/cmd_auth.go
- [x] picoclaw-main/cmd/picoclaw/cmd_skills.go
- [x] picoclaw-main/cmd/picoclaw/cmd_cron.go
- [x] picoclaw-main/cmd/picoclaw/cmd_migrate.go

### Docs: auth/providers/tools/migration

- [x] picoclaw-main/docs/tools_configuration.md
- [x] picoclaw-main/docs/ANTIGRAVITY_USAGE.md
- [x] picoclaw-main/docs/ANTIGRAVITY_AUTH.md
- [x] picoclaw-main/docs/migration/model-list-migration.md

### Docs: channels

- [x] picoclaw-main/docs/wecom-app-configuration.md
- [x] picoclaw-main/docs/channels/\* (Telegram/Discord/QQ/WeCom/etc)

### Finalization

- [x] Consistency pass (no conflicting commands/paths)
- [x] De-dup pass (merge overlapping reference notes)
