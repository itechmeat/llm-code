# Swift (pgvector-swift)

Upstream: https://github.com/pgvector/pgvector-swift

## Supported clients (README)

- PostgresNIO
- PostgresClientKit

## PostgresNIO

- Add `pgvector-swift` to `Package.swift` and include products:
  - `Pgvector`
  - `PgvectorNIO`

Key steps:

- Enable extension: `CREATE EXTENSION IF NOT EXISTS vector`
- Register types:
  - `PgvectorNIO.registerTypes(client)`
- Use `Vector([Float])` values for interpolation in query strings.

## PostgresClientKit

- Add products:
  - `Pgvector`
  - `PgvectorClientKit`

- Use prepared statements and pass `Vector([..])` as parameter values.
- Decode vectors using `columns[i].vector()`.

## Indexing

- HNSW / IVFFlat examples match the core extension:
  - `CREATE INDEX ... USING hnsw (embedding vector_l2_ops)`
  - `CREATE INDEX ... USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)`

## Reference: vector types

- `Vector`, `HalfVector`, `SparseVector`
- Sparse vector note: indices start at 0 in the Swift API.
