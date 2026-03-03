# Indexing (HNSW / IVFFlat)

pgvector supports exact search by default. Add an index for approximate nearest-neighbor (ANN) search when you need better latency at some recall cost.

## Core rule

- Create a separate ANN index for each distance function/operator class you plan to query with.
- Queries typically need `ORDER BY <distance-op> ... LIMIT ...` to use the ANN index.

## HNSW

**When to choose**

- Better speed/recall tradeoff than IVFFlat, but slower builds and higher memory usage.
- Can create the index before loading data (no training step).

**Create index (examples)**

```sql
-- L2
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);

-- inner product
CREATE INDEX ON items USING hnsw (embedding vector_ip_ops);

-- cosine
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

-- L1
CREATE INDEX ON items USING hnsw (embedding vector_l1_ops);

-- binary
CREATE INDEX ON items USING hnsw (embedding bit_hamming_ops);
CREATE INDEX ON items USING hnsw (embedding bit_jaccard_ops);
```

**Operator classes for other types**

- Use `halfvec_*_ops` for `halfvec`
- Use `sparsevec_*_ops` for `sparsevec`

**Index options**

- `m` (default 16): max connections per layer
- `ef_construction` (default 64): candidate list size during build

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 64);
```

**Query option**

- `hnsw.ef_search` (default 40): candidate list size during search

```sql
SET hnsw.ef_search = 100;
-- or per query
BEGIN;
SET LOCAL hnsw.ef_search = 100;
SELECT ...;
COMMIT;
```

**Build performance**

- Index build is much faster when the graph fits in `maintenance_work_mem`.
- If you see a notice that the HNSW graph no longer fits, builds will slow down; increase `maintenance_work_mem` but avoid exhausting server memory.
- Create ANN indexes after bulk loading initial data when possible.
- Parallelism: tune `max_parallel_maintenance_workers` (and possibly `max_parallel_workers`).

**Build progress**

- Check `pg_stat_progress_create_index` phases for HNSW:
  - `initializing`
  - `loading tuples`

## IVFFlat

**When to choose**

- Faster builds / lower memory, but typically worse speed/recall than HNSW.
- Works best when created after the table has enough data (it performs a k-means step).

**Create index (example)**

```sql
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

**Choosing parameters (rule of thumb from README)**

- Build after you have data.
- `lists`:
  - up to 1M rows: `rows / 1000`
  - over 1M rows: `sqrt(rows)`
- Query: set `ivfflat.probes` (higher = better recall, slower).

Note: setting `ivfflat.probes` to the number of `lists` makes the search exact, and the planner may stop using the index.

```sql
SET ivfflat.probes = 10;
BEGIN;
SET LOCAL ivfflat.probes = 10;
SELECT ...;
COMMIT;
```

**Build progress**

- Check `pg_stat_progress_create_index` phases for IVFFlat:
  - `initializing`
  - `performing k-means`
  - `assigning tuples`
  - `loading tuples` (the `%` field is only populated here)

**Progress monitoring**

- Use `pg_stat_progress_create_index` to see phases and progress.
