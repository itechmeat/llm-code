# Cron (scheduled jobs)

Cron jobs are executed by the gateway’s cron service.

## List jobs

- `picoclaw cron list`

## Add a job

Two schedule styles:

1. Every N seconds

- `picoclaw cron add --name "Ping" --every 60 --message "Say hi"`

2. Cron expression

- `picoclaw cron add --name "Daily" --cron "0 9 * * *" --message "Send a daily summary"`

Delivery options:

- Add `--deliver` plus `--channel` and `--to` to route the result to a channel.

## Execution policy note (v0.2.3)

Cron command execution is now gated through exec settings.

- If a cron task needs command execution, verify the relevant `tools.exec` policy first.
- Keep deny patterns enabled unless the environment is fully trusted.
- Use `tools.cron.exec_timeout_minutes` together with exec policy so scheduled commands stay bounded.

## Enable/disable

- `picoclaw cron disable <job_id>`
- `picoclaw cron enable <job_id>`

## Remove

- `picoclaw cron remove <job_id>`
