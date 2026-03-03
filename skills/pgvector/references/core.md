# pgvector core (SQL)

## Install + enable

- pgvector is a PostgreSQL extension (README states Postgres 13+).
- Enable per-database:
  - `CREATE EXTENSION vector;`

## Getting started (minimal SQL)

```sql
CREATE EXTENSION vector;

CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding vector(3)
);

INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');

SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

Note: `<#>` returns the negative inner product.

## Data model

- Fixed dimension column:
  - `embedding vector(1536)`
- Variable dimensions (no `(n)`):
  - `embedding vector`
  - Indexing then typically uses expression + partial indexes per dimension.

## Insert / update

- Insert: `INSERT INTO items (embedding) VALUES ('[1,2,3]');`
- Upsert: normal `ON CONFLICT ... DO UPDATE` works.
- Bulk load:
  - Prefer `COPY` for initial loads; add ANN indexes after.

## Querying nearest neighbors

- Basic pattern (index-friendly):
  - `ORDER BY <distance-op> ... LIMIT ...`

### Common query patterns

```sql
-- nearest neighbors to a query vector
SELECT * FROM items
ORDER BY embedding <-> '[3,1,2]'
LIMIT 5;

-- nearest neighbors to an existing row
SELECT * FROM items
WHERE id != 1
ORDER BY embedding <-> (SELECT embedding FROM items WHERE id = 1)
LIMIT 5;

-- within a distance threshold
SELECT * FROM items
WHERE embedding <-> '[3,1,2]' < 5;
```

Tip: combine distance filtering with `ORDER BY` + `LIMIT` when you want index usage.

### Distance operators

- L2 (Euclidean): `<->`
- Inner product: `<#>` (returns negative inner product)
- Cosine distance: `<=>`
- L1 (taxicab): `<+>`
- Binary: Hamming `<~>`, Jaccard `<%>`

### Distance vs similarity

- Inner product value: `-(embedding <#> query_vec)`
- Cosine similarity: `1 - (embedding <=> query_vec)`

## Aggregates

- Average vector: `SELECT AVG(embedding) FROM items;`
- Grouped average: `SELECT category_id, AVG(embedding) FROM items GROUP BY category_id;`

## Practical tips

- `NULL` vectors are not indexed; for cosine distance, zero vectors are not indexed (important for recall).
