# PostgreSQL Error Handling Settings

Runtime parameters controlling error behavior and crash recovery.

## Error Termination

### exit_on_error

Terminate session on any error:

```sql
exit_on_error = off  -- Default
```

When `on`, any ERROR (not just FATAL) terminates the session. Useful for scripts that should abort on first failure.

**Usage:**

```bash
psql -v ON_ERROR_STOP=1 -f script.sql  # psql variable
```

Or per-session:

```sql
SET exit_on_error = on;
```

## Crash Recovery

### restart_after_crash

Auto-restart after backend crash:

```sql
restart_after_crash = on  -- Default
```

Set to `off` when:
- Using external cluster management (Patroni, Pacemaker)
- Clusterware needs to control failover decisions

### data_sync_retry

Retry fsync failures:

```sql
data_sync_retry = off  -- Default
```

**Warning:** Set to `off` (default) in most cases. When `on`, PostgreSQL retries failed fsync calls, which can mask serious storage issues.

Set to `on` only if your storage guarantees data isn't lost on fsync failure (rare).

### recovery_init_sync_method (PG14+)

How to sync data directory before crash recovery:

```sql
recovery_init_sync_method = fsync      -- Default: recursive fsync
recovery_init_sync_method = syncfs     -- Faster on some filesystems
```

`syncfs` is faster but less portable. Use `fsync` for safety.

## Memory Errors

### shared_memory_size_in_huge_pages (PG17+)

Report shared memory allocation:

```sql
SHOW shared_memory_size_in_huge_pages;
```

## Logging (Related)

For error logging configuration, see the logging settings:

```sql
log_min_messages = warning        -- Min severity to log
log_min_error_statement = error   -- Log statement on this severity
log_error_verbosity = default     -- terse, default, verbose
```

## Quick Reference

### Default Settings

```sql
exit_on_error = off              -- Don't exit on ERROR
restart_after_crash = on         -- Auto-restart postmaster
data_sync_retry = off            -- Don't retry fsync
recovery_init_sync_method = fsync
```

### With Cluster Management

When using Patroni, pg_auto_failover, or similar:

```sql
restart_after_crash = off        -- Let clusterware handle restart
```

### Script Execution

For scripts that should stop on first error:

```bash
# psql approach
psql -v ON_ERROR_STOP=1 -c "SELECT 1/0;" -c "SELECT 'this wont run';"

# In script, check $? or use set -e
```

## Parameter Context

| Parameter | Requires |
|-----------|----------|
| `exit_on_error` | Session |
| `restart_after_crash` | Reload |
| `data_sync_retry` | Restart |
| `recovery_init_sync_method` | Restart |

## See Also

- [PostgreSQL Error Handling docs](https://www.postgresql.org/docs/current/runtime-config-error-handling.html)
