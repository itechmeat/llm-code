# Python (pgvector-python)

Upstream: https://github.com/pgvector/pgvector-python

## Install

- `pip install pgvector`

## Django integration

### Enable extension via migrations

- Use `VectorExtension()` migration operation.

### Fields

- `VectorField(dimensions=n)`
- Also: `HalfVectorField`, `BitField`, `SparseVectorField`

### Query patterns

- Order by distance:
  - `L2Distance`, `MaxInnerProduct`, `CosineDistance`, `L1Distance`, `HammingDistance`, `JaccardDistance`
- Filter by distance:
  - compute/alias distance and filter (e.g. `< 5`)

### Approximate indexes (Django)

- Use `HnswIndex(...)` / `IvfflatIndex(...)` in `Meta.indexes`.
- Specify `opclasses` (examples in README use `vector_l2_ops` and mention `vector_ip_ops`, `vector_cosine_ops`).

### Half-precision indexing (Django)

- Use expression + opclass:
  - cast field to `HalfVectorField(dimensions=n)` and use `halfvec_*_ops`.

## SQLAlchemy integration

### Enable extension

- `CREATE EXTENSION IF NOT EXISTS vector`

### Column types

- `VECTOR(n)`
- Also: `HALFVEC`, `BIT`, `SPARSEVEC`

### Query patterns

- Column methods for distance:
  - `.l2_distance(...)`, `.max_inner_product(...)`, `.cosine_distance(...)`, `.l1_distance(...)`, `.hamming_distance(...)`, `.jaccard_distance(...)`

### Approximate indexes (SQLAlchemy)

- Create an `Index(..., postgresql_using='hnsw'|'ivfflat')`.
- Provide:
  - `postgresql_with` (e.g. `{'m': 16, 'ef_construction': 64}` or `{'lists': 100}`)
  - `postgresql_ops` mapping column name to operator class (e.g. `'vector_l2_ops'`).

### Advanced: expression indexing

- Half precision: index `cast(column, HALFVEC(n))` with `halfvec_*_ops`.
- Binary quantization: index `cast(binary_quantize(column), BIT(n))` with `bit_hamming_ops`, then re-rank with original vectors.

## Other supported DB libraries (README list)

- SQLModel, Psycopg 3, Psycopg 2, asyncpg, pg8000, Peewee

## Examples directory (what to look for)

The upstream repo has `examples/` covering common patterns and integrations, including:

- `loading` (bulk loading patterns)
- `hybrid_search` (hybrid retrieval patterns)
- `sparse_search` (sparse vectors)
- `rag` (RAG-style workflows)
- `openai`, `cohere`, `sentence_transformers` (embedding generation + storage)
- `image_search`, `imagehash` (image similarity / hashing)
- `citus` (distributed/sharded Postgres example)
