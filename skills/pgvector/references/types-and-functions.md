# Types, operators, functions

This reference focuses on practical type choices, indexing implications, and a minimal operator/function checklist.

## Types at a glance

- `vector`: float32 elements
- `halfvec`: float16 elements (smaller storage, and can be indexed at half precision)
- `bit`: binary vectors (useful for hashes/quantization)
- `sparsevec`: sparse vectors (index/value map + dimensions)

Indexing dimension limits called out in the README:

- `vector`: up to 2,000 dims for ANN indexes
- `halfvec`: up to 4,000 dims for ANN indexes
- `bit`: up to 64,000 dims for ANN indexes
- `sparsevec`: up to 1,000 non-zero elements for ANN indexes

## `vector` basics

- Fixed dims: `vector(n)`
- Variable dims: `vector` (indexes usually require expression + partial indexes per dimension)

### Storage + validity

- README notes: roughly `4 * dimensions + 8` bytes.
- Elements must be finite (no NaN/Infinity).

### Common operators

- Element-wise: `+`, `-`, `*`, concatenation `||`
- Distances: `<->`, `<#>`, `<=>`, `<+>`

### Common functions

- `vector_dims(v)`
- `vector_norm(v)`
- `l2_normalize(v)`
- `subvector(v, start, count)`
- `l2_distance(a, b)`, `inner_product(a, b)`, `cosine_distance(a, b)`, `l1_distance(a, b)`

### Aggregates

- `avg(v)`
- `sum(v)`

## Half precision (`halfvec`)

### Store half-precision vectors

```sql
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding halfvec(3)
);
```

### Index at half precision

- Smaller indexes by indexing via a cast:

```sql
CREATE INDEX ON items
USING hnsw ((embedding::halfvec(3)) halfvec_l2_ops);
```

### Query

```sql
SELECT *
FROM items
ORDER BY embedding::halfvec(3) <-> '[1,2,3]'
LIMIT 5;
```

### Storage + validity

- README notes: roughly `2 * dimensions + 8` bytes.
- Elements must be finite (no NaN/Infinity).

## Operator class reminder

- Use `halfvec_*_ops` for `halfvec`
- Use `sparsevec_*_ops` for `sparsevec`
- Use `bit_*_ops` for `bit`

## Binary vectors (`bit`) and quantization

### Store binary vectors

```sql
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding bit(3)
);

INSERT INTO items (embedding) VALUES ('000'), ('111');
```

### Query

- Hamming distance: `<~>`
- Jaccard distance: `<%>`

```sql
SELECT * FROM items ORDER BY embedding <~> '101' LIMIT 5;
```

### Binary quantization workflow

- Use expression indexing on `binary_quantize(...)` and then re-rank with original vectors:

```sql
CREATE INDEX ON items
USING hnsw ((binary_quantize(embedding)::bit(3)) bit_hamming_ops);

SELECT * FROM (
  SELECT *
  FROM items
  ORDER BY binary_quantize(embedding)::bit(3) <~> binary_quantize('[1,-2,3]')
  LIMIT 20
) t
ORDER BY embedding <=> '[1,-2,3]'
LIMIT 5;
```

## Sparse vectors (`sparsevec`)

### Store sparse vectors

```sql
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding sparsevec(5)
);
```

### Insert format

- Format: `{index:value,...}/dimensions`
- Indices start at 1 (like SQL arrays)

```sql
INSERT INTO items (embedding)
VALUES ('{1:1,3:2,5:3}/5'), ('{1:4,3:5,5:6}/5');
```

### Query

```sql
SELECT *
FROM items
ORDER BY embedding <-> '{1:3,3:1,5:2}/5'
LIMIT 5;
```

### Storage + validity

- README notes: roughly `8 * non-zero elements + 16` bytes.
- Elements must be finite (no NaN/Infinity).
