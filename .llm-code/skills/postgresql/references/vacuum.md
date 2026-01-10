# PostgreSQL Vacuum Settings

Runtime parameters for manual VACUUM and autovacuum.

## Why Vacuum Matters

VACUUM is essential for PostgreSQL because:
- Reclaims space from dead tuples (deleted/updated rows)
- Updates visibility map for index-only scans
- Prevents transaction ID wraparound
- Updates planner statistics (ANALYZE)

## Cost-Based Vacuum Throttling

VACUUM uses a cost model to limit I/O impact on running queries.

### Cost Settings

```sql
vacuum_cost_delay = 0           -- Delay in ms when cost limit reached (0 = disabled)
vacuum_cost_limit = 200         -- Accumulated cost before sleeping
vacuum_cost_page_hit = 1        -- Cost of page found in shared buffers
vacuum_cost_page_miss = 2       -- Cost of page read from OS cache
vacuum_cost_page_dirty = 20     -- Cost of dirtying a clean page
```

**Tip:** For dedicated maintenance windows, set `vacuum_cost_delay = 0` to run full speed.

## Freeze Settings

Prevent transaction ID wraparound:

```sql
vacuum_freeze_min_age = 50000000      -- Min XID age before freezing
vacuum_freeze_table_age = 150000000   -- Whole-table scan threshold
vacuum_multixact_freeze_min_age = 5000000
vacuum_multixact_freeze_table_age = 150000000
vacuum_failsafe_age = 1600000000      -- Emergency freeze threshold (PG14+)
```

**Warning:** If `vacuum_failsafe_age` is reached, autovacuum becomes aggressive and ignores cost limits.

## Autovacuum Settings

### Enable/Workers

```sql
autovacuum = on                    -- Enable autovacuum
autovacuum_max_workers = 3         -- Max concurrent workers
```

### Timing

```sql
autovacuum_naptime = 1min          -- Time between launcher runs
```

### Thresholds

When to trigger VACUUM:

```sql
autovacuum_vacuum_threshold = 50           -- Min dead tuples
autovacuum_vacuum_scale_factor = 0.2       -- Fraction of table size
autovacuum_vacuum_insert_threshold = 1000  -- Inserts (PG13+)
autovacuum_vacuum_insert_scale_factor = 0.2
```

**Formula:** `threshold + scale_factor * table_size`

With defaults, a 10,000-row table triggers at: `50 + 0.2 * 10000 = 2050` dead tuples.

### ANALYZE Thresholds

```sql
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1
```

### Autovacuum Cost Limits

```sql
autovacuum_vacuum_cost_delay = 2ms    -- Delay between cost limit hits
autovacuum_vacuum_cost_limit = -1     -- -1 = use vacuum_cost_limit
```

**Note:** Cost limit is shared among all autovacuum workers.

## Per-Table Settings

Override autovacuum settings for specific tables:

```sql
ALTER TABLE hot_table SET (
  autovacuum_vacuum_threshold = 100,
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_vacuum_cost_delay = 0,
  autovacuum_analyze_threshold = 100
);

-- Disable autovacuum for specific table (rarely needed)
ALTER TABLE archive_table SET (autovacuum_enabled = false);
```

## Quick Reference

### Production Defaults (OLTP)

```sql
# Increase workers for high-update workloads
autovacuum_max_workers = 5

# More aggressive thresholds
autovacuum_vacuum_scale_factor = 0.05
autovacuum_vacuum_threshold = 50
autovacuum_analyze_scale_factor = 0.02
autovacuum_analyze_threshold = 50

# Faster vacuum (if I/O permits)
autovacuum_vacuum_cost_delay = 2ms
autovacuum_vacuum_cost_limit = 1000
```

### Large Tables

For tables with millions of rows:

```sql
ALTER TABLE large_table SET (
  autovacuum_vacuum_scale_factor = 0.01,  -- 1% instead of 20%
  autovacuum_analyze_scale_factor = 0.005
);
```

### Monitor Vacuum Progress

```sql
-- Current vacuum operations
SELECT * FROM pg_stat_progress_vacuum;

-- Last vacuum times
SELECT relname, last_vacuum, last_autovacuum, 
       last_analyze, last_autoanalyze
FROM pg_stat_user_tables;

-- Dead tuples count
SELECT relname, n_dead_tup, n_live_tup,
       n_dead_tup::float / NULLIF(n_live_tup, 0) AS dead_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Transaction ID age
SELECT relname, age(relfrozenxid) AS xid_age
FROM pg_class
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC;
```

### Manual Vacuum

```sql
-- Standard vacuum (concurrent)
VACUUM tablename;

-- Vacuum with analyze
VACUUM ANALYZE tablename;

-- Full vacuum (exclusive lock, rewrites table)
VACUUM FULL tablename;

-- Freeze all rows
VACUUM FREEZE tablename;

-- Verbose output
VACUUM VERBOSE tablename;
```

## Troubleshooting

### Autovacuum Not Running

Check:
```sql
SHOW autovacuum;                    -- Is it enabled?
SELECT * FROM pg_stat_activity 
WHERE backend_type = 'autovacuum worker';
```

### Dead Tuples Growing

Possible causes:
- Long-running transactions blocking vacuum
- Thresholds too high for table size
- Autovacuum cost limits too aggressive

Check bloat:
```sql
SELECT relname, n_dead_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

### Transaction ID Wraparound Warning

If you see "database is not accepting commands to avoid wraparound":

```sql
-- Check age
SELECT datname, age(datfrozenxid) FROM pg_database;

-- Emergency vacuum
VACUUM FREEZE;
```

## Parameter Context

| Parameter | Requires |
|-----------|----------|
| `autovacuum` | Reload |
| `autovacuum_max_workers` | Restart |
| `autovacuum_naptime` | Reload |
| `autovacuum_vacuum_*` | Reload |
| `vacuum_cost_*` | Session/Reload |
| `vacuum_freeze_*` | Session/Reload |

## See Also

- [PostgreSQL Vacuum docs](https://www.postgresql.org/docs/current/routine-vacuuming.html)
- [Runtime Config Vacuum](https://www.postgresql.org/docs/current/runtime-config-vacuum.html)
