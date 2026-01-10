# PostgreSQL Query Tuning Settings

Runtime parameters affecting query planning and execution.

## Planner Method Switches

Enable/disable specific plan types for debugging or forcing behavior:

```sql
enable_seqscan = on          -- Sequential scans
enable_indexscan = on        -- Index scans
enable_indexonlyscan = on    -- Index-only scans
enable_bitmapscan = on       -- Bitmap scans
enable_tidscan = on          -- TID scans
enable_sort = on             -- Explicit sorts
enable_hashagg = on          -- Hash aggregation
enable_hashjoin = on         -- Hash joins
enable_mergejoin = on        -- Merge joins
enable_nestloop = on         -- Nested loop joins
enable_material = on         -- Materialization
enable_memoize = on          -- Memoize (PG14+)
enable_partitionwise_join = off
enable_partitionwise_aggregate = off
enable_parallel_hash = on
enable_parallel_append = on
enable_partition_pruning = on
```

**Tip:** Use `SET enable_seqscan = off` temporarily to force index usage for debugging, but don't leave disabled in production.

## Cost Constants

### Page Costs

```sql
seq_page_cost = 1.0           -- Sequential page fetch cost
random_page_cost = 4.0        -- Random page fetch cost
```

**SSD tuning:** Lower `random_page_cost` for SSDs:

```sql
random_page_cost = 1.1        -- SSD: almost same as sequential
```

### CPU Costs

```sql
cpu_tuple_cost = 0.01         -- Processing one row
cpu_index_tuple_cost = 0.005  -- Processing one index entry
cpu_operator_cost = 0.0025    -- Processing one operator
```

### effective_cache_size

Hint to planner about available OS cache:

```sql
effective_cache_size = 4GB    -- Default varies
```

**Sizing:** Set to ~50-75% of total RAM (includes OS cache + shared_buffers):

```sql
-- 16GB RAM system
effective_cache_size = 12GB
```

### effective_io_concurrency

For SSDs and RAID arrays:

```sql
effective_io_concurrency = 1    -- HDD default
effective_io_concurrency = 200  -- SSD recommended
```

## Memory Settings

### work_mem

Memory per sort/hash operation (per query, per operation):

```sql
work_mem = 4MB  -- Default
```

**Warning:** A single query with multiple sorts can use `N × work_mem`. Be conservative.

**Sizing guidance:**
- `(RAM - shared_buffers) / max_connections / 4`
- Increase for complex analytical queries
- Set per-session for specific workloads

```sql
SET work_mem = '256MB';  -- For complex query
```

### maintenance_work_mem

Memory for maintenance operations (VACUUM, CREATE INDEX):

```sql
maintenance_work_mem = 64MB   -- Default
maintenance_work_mem = 1GB    -- For large indexes
```

### hash_mem_multiplier (PG13+)

```sql
hash_mem_multiplier = 2.0     -- Hash can use 2x work_mem
```

## Parallel Query Settings

### Workers

```sql
max_parallel_workers_per_gather = 2  -- Max workers per Gather node
max_parallel_workers = 8             -- Total parallel workers
max_parallel_maintenance_workers = 2 -- For CREATE INDEX
parallel_leader_participation = on   -- Leader also does work
```

### Parallel Thresholds

```sql
min_parallel_table_scan_size = 8MB   -- Min table size for parallel
min_parallel_index_scan_size = 512kB -- Min index size for parallel
```

### Parallel Costs

```sql
parallel_tuple_cost = 0.1     -- Cost per tuple passed to leader
parallel_setup_cost = 1000    -- Cost to launch worker
```

## Join and Aggregation Limits

### Join Planning Limits

```sql
from_collapse_limit = 8       -- Max FROM items before explicit join order
join_collapse_limit = 8       -- Max items in explicit JOIN before fixing order
```

**Note:** For complex queries with many joins, increasing may improve plans but increases planning time.

### GEQO (Genetic Query Optimizer)

For queries with many tables:

```sql
geqo = on
geqo_threshold = 12           -- Use GEQO for 12+ FROM items
geqo_effort = 5               -- 1-10, higher = better plans, slower
```

## Statistics and Estimation

### Statistics Target

Controls histogram detail:

```sql
default_statistics_target = 100  -- Default
```

Per-column override:

```sql
ALTER TABLE t ALTER COLUMN c SET STATISTICS 1000;
ANALYZE t;
```

### Planner Estimates

```sql
cursor_tuple_fraction = 0.1   -- Expected fraction of cursor rows fetched
```

## Plan Caching

### plan_cache_mode (PG12+)

```sql
plan_cache_mode = auto        -- Default
plan_cache_mode = force_custom_plan
plan_cache_mode = force_generic_plan
```

### JIT Compilation (PG11+)

```sql
jit = on                      -- Enable JIT
jit_above_cost = 100000       -- Min cost to use JIT
jit_inline_above_cost = 500000
jit_optimize_above_cost = 500000
```

## Quick Reference

### Production Defaults (SSD)

```sql
# Storage costs (SSD)
random_page_cost = 1.1
effective_io_concurrency = 200

# Memory
effective_cache_size = 12GB   # ~75% of RAM
work_mem = 64MB               # Adjust based on workload
maintenance_work_mem = 1GB

# Parallelism
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
```

### Per-Session Tuning

```sql
-- For complex analytical query
SET work_mem = '256MB';
SET enable_seqscan = off;  -- Debug only

-- Reset
RESET work_mem;
RESET enable_seqscan;
```

### EXPLAIN Analysis

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
```

Look for:
- Seq Scan on large tables (may need index)
- High `actual time` vs `estimated`
- Sort spilling to disk (`Sort Method: external merge`)

## Parameter Context

| Parameter | Requires |
|-----------|----------|
| `max_parallel_workers` | Restart |
| `effective_cache_size` | Reload |
| `work_mem` | Session/Reload |
| `random_page_cost` | Session/Reload |
| `enable_*` | Session/Reload |

## See Also

- [table-design.md](table-design.md) — Indexing patterns
- [PostgreSQL EXPLAIN docs](https://www.postgresql.org/docs/current/using-explain.html)
- [PostgreSQL Query Planning docs](https://www.postgresql.org/docs/current/runtime-config-query.html)
