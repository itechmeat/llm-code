# Troubleshooting

## Query isn’t using an ANN index

Checklist:

- Query must have both `ORDER BY` and `LIMIT`.
- `ORDER BY` must be the _distance operator result_ (not a derived expression) in ascending order.

Example:

```sql
-- index-friendly
SELECT *
FROM items
ORDER BY embedding <=> '[3,1,2]'
LIMIT 5;

-- not index-friendly
SELECT *
FROM items
ORDER BY 1 - (embedding <=> '[3,1,2]') DESC
LIMIT 5;
```

Planner nudge (use per-query):

```sql
BEGIN;
SET LOCAL enable_seqscan = off;
SELECT ...;
COMMIT;
```

Also: on small tables, a sequential scan can be legitimately faster.

## Query isn’t using a parallel table scan

The README notes the planner may underestimate the cost of out-of-line storage (TOAST). Options:

- Adjust cost thresholds per-query:

```sql
BEGIN;
SET LOCAL min_parallel_table_scan_size = 1;
SET LOCAL parallel_setup_cost = 1;
SELECT ...;
COMMIT;
```

- Or store vectors inline:

```sql
ALTER TABLE items ALTER COLUMN embedding SET STORAGE PLAIN;
```

## Fewer results after adding an HNSW index

- Often limited by `hnsw.ef_search` (default 40) and/or filtering and dead tuples.
- Enable iterative scans to scan more when filters prevent enough matches.
- Remember: `NULL` vectors are not indexed; for cosine distance, zero vectors are not indexed.

## Fewer results after adding an IVFFlat index

- Common cause: created with too little data for the chosen `lists`.
  - Drop and recreate later:

```sql
DROP INDEX index_name;
```

- Can also be limited by `ivfflat.probes`; iterative scans can help.
- Remember: `NULL` vectors are not indexed; for cosine distance, zero vectors are not indexed.
