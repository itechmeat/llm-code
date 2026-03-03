# Java / Kotlin (pgvector-java)

Upstream: https://github.com/pgvector/pgvector-java

## JDBC (Java)

Key pattern:

- Enable extension: `CREATE EXTENSION IF NOT EXISTS vector`
- Register types on the `Connection`:
  - `PGvector.registerTypes(conn)`
- Use `PreparedStatement#setObject(..., new PGvector(float[]))` for parameters.

Nearest neighbors:

- `ORDER BY embedding <-> ? LIMIT 5`

## Spring JDBC

- Same idea as raw JDBC: pass `PGvector` objects as parameters.

## Hibernate / R2DBC

- Hibernate 6.4+ includes a dedicated vector module (`hibernate-vector`) and recommends using it instead of the older `com.pgvector.pgvector` integration.
- R2DBC PostgreSQL 1.0.3+ has built-in support for the vector type.

## Kotlin

- `PGvector(floatArrayOf(...))` works similarly for JDBC.

## Indexing

- Create ANN indexes with SQL:

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

- Use `vector_ip_ops` for inner product and `vector_cosine_ops` for cosine distance.

## Reference: helper types

- `PGvector` (vector)
- `PGhalfvec` (halfvec)
- `PGbit` (bit)
- `PGsparsevec` (sparsevec)

Sparse vector note:

- The Java API examples note indices start at 0 (different from SQL `sparsevec` text format where indices start at 1).
