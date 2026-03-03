# Go (pgvector-go)

Upstream: https://github.com/pgvector/pgvector-go

## Install

- `go get github.com/pgvector/pgvector-go`

## Supported libraries (README)

- pgx, pg, Bun, Ent, GORM, sqlx

## pgx (important detail: type registration)

- Import and register types per connection/pool:
  - `pgxvec.RegisterTypes(ctx, conn)`
  - or in `config.AfterConnect` for pools

This is typically required so pgx can encode/decode `vector`, `halfvec`, `sparsevec`, etc.

## Data model

- Use `pgvector.Vector` in structs and tag the DB type in your ORM/driver metadata (examples show `vector(3)`).
- Create vectors with:
  - `pgvector.NewVector([]float32{...})`

## Querying

- Use raw SQL with distance operators:

```sql
SELECT id FROM items ORDER BY embedding <-> $1 LIMIT 5
```

- In ORMs, use `OrderExpr("embedding <-> ?", vec)` / selector expressions.

## Indexing

- Create HNSW or IVFFlat indexes with the right operator class:

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

- Use `vector_ip_ops` for inner product and `vector_cosine_ops` for cosine distance.

## Reference: other vector types

- Half vectors:
  - `pgvector.NewHalfVector([]float32{...})`
- Sparse vectors:
  - `pgvector.NewSparseVector([]float32{...})`
  - or `pgvector.NewSparseVectorFromMap(elements, dimensions)`
  - Note: indices start at 0 in the Go API (different from SQL `sparsevec` format).
