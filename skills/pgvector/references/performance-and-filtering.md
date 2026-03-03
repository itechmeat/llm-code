# Filtering, iterative scans, performance

## Filtering with `WHERE`

When you combine ANN search with filters, pgvector/PG will often apply the filter after scanning the ANN index, which can reduce the number of returned rows.

### Start with exact indexes on filters

- Add a normal index on the filter column(s):

```sql
CREATE INDEX ON items (category_id);
CREATE INDEX ON items (location_id, category_id);
```

- Exact indexes work well when the filter matches a small fraction of rows.

### ANN + filtering gotcha

- If ~10% of rows match a filter and `hnsw.ef_search` is 40, you may get ~4 matches on average unless you scan more candidates.

## Iterative index scans (0.8.0+)

Iterative scans automatically scan more of the ANN index when filtering prevents enough rows from being found.

### Ordering modes

- `strict_order`: results strictly ordered by distance
- `relaxed_order`: may be slightly out of order, but improves recall

```sql
SET hnsw.iterative_scan = strict_order;
SET hnsw.iterative_scan = relaxed_order;
SET ivfflat.iterative_scan = relaxed_order;
```

### Make relaxed results strictly ordered

- Use a materialized CTE to re-sort:

```sql
WITH relaxed_results AS MATERIALIZED (
  SELECT id, embedding <-> '[1,2,3]' AS distance
  FROM items
  WHERE category_id = 123
  ORDER BY distance
  LIMIT 5
)
SELECT * FROM relaxed_results
ORDER BY distance + 0;
```

Note: the README mentions `+ 0` is needed for Postgres 17+.

### Filter by distance efficiently

- Put the distance filter outside a materialized CTE:

```sql
WITH nearest_results AS MATERIALIZED (
  SELECT id, embedding <-> '[1,2,3]' AS distance
  FROM items
  ORDER BY distance
  LIMIT 5
)
SELECT *
FROM nearest_results
WHERE distance < 5
ORDER BY distance;
```

## Tuning knobs for “scan more”

### HNSW

```sql
-- scan more candidates (recall ↑, latency ↑)
SET hnsw.ef_search = 200;

-- stop conditions
SET hnsw.max_scan_tuples = 20000;
SET hnsw.scan_mem_multiplier = 2;
```

Notes:

- `hnsw.max_scan_tuples` is approximate and does not affect the initial scan.
- If increasing `hnsw.max_scan_tuples` doesn’t help recall, try increasing `hnsw.scan_mem_multiplier`.

### IVFFlat

```sql
SET ivfflat.max_probes = 100;
```

Note: if `ivfflat.max_probes` is lower than `ivfflat.probes`, `ivfflat.probes` is used.

## Production performance workflow

- Bulk load with `COPY`, add indexes after loading.
- Use `EXPLAIN (ANALYZE, BUFFERS)` to validate index usage and latency.
- Prefer `SET LOCAL` inside transactions to tune per-query.

## General performance notes

### Postgres tuning

- The README suggests using tools like PgTune for initial server settings.
- Useful inspection queries:

```sql
SHOW config_file;
SHOW shared_buffers;
```

### Loading and indexing

- Bulk load with `COPY` when possible; create ANN indexes after the initial load.
- In production, consider concurrent index creation to avoid blocking writes:

```sql
CREATE INDEX CONCURRENTLY ...
```

### Query performance debugging

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM items
ORDER BY embedding <-> '[3,1,2]'
LIMIT 5;
```

### Exact search (no ANN index)

- Increase parallelism for large scans:

```sql
SET max_parallel_workers_per_gather = 4;
```

- If vectors are normalized to length 1, the README suggests inner product for best performance:

```sql
SELECT * FROM items ORDER BY embedding <#> '[3,1,2]' LIMIT 5;
```

### IVFFlat speed vs recall

- Increasing `lists` can improve speed (and can reduce recall):

```sql
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 1000);
```

### Vacuuming with HNSW

- Vacuum can be slow; the README suggests reindexing first:

```sql
REINDEX INDEX CONCURRENTLY index_name;
VACUUM table_name;
```

### Monitoring

- Use `pg_stat_statements` (requires `shared_preload_libraries`):

```sql
CREATE EXTENSION pg_stat_statements;
```

- Compare ANN results with exact results to monitor recall:

```sql
BEGIN;
SET LOCAL enable_indexscan = off;
SELECT ...;
COMMIT;
```

### Scaling

- Scale the same way you scale Postgres: vertically (bigger instance) or horizontally (replicas / sharding approaches like Citus).
