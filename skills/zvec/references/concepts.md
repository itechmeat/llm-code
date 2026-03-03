# Concepts

Zvec is an **in-process** vector database: you embed it into your application process, store vectors plus metadata, and query by similarity.

## Data model

- **Collection**: container of documents (roughly a table).
- **Document**: record with:
  - `id` (unique string; immutable after insertion)
  - `vectors` (named vector fields)
  - `fields` (named scalar metadata)

### Schema rules

- Each collection has a schema describing scalar fields + vector fields, their types, and index parameters.
- All documents must conform to the collection’s schema.
- Schema is **dynamic** (you can add/remove scalar fields and indexes without recreating the collection).
- No cross-collection queries (no joins/unions/multi-collection search).

### Persistence model

- Each collection is persisted in its own directory and is self-contained (directory can be relocated).

## Embeddings and vectors

### Retrieval loop

1. Generate embeddings for items and store them.
2. Generate the query embedding with the **same model/pipeline**.
3. Run similarity search to retrieve nearest neighbors.

### Metric alignment

Embedding models are typically trained with a particular similarity objective (cosine, dot product/IP, Euclidean/L2). For best relevance, use the same metric in Zvec indexing/querying.

### Dense vs sparse

- **Dense**: fixed-length arrays; strong semantic generalization; less interpretable.
- **Sparse**: few non-zero dimensions (often term-weight style); more interpretable; weaker semantic generalization unless encoded.

## Indexing and filtering

### Vector index

- Flat/brute-force search is exact but becomes too slow at scale.
- ANN indexes trade a small amount of accuracy for large speed gains.
- Docs mention index types: Flat, HNSW, IVF.

ANN quality is often measured as $\text{Recall@}k$:

$$
	ext{Recall@}k = \frac{\text{# of true nearest neighbors found in top-}k}{k}
$$

### Inverted index

- Use inverted indexes for scalar fields you filter on frequently (exact match/IN, ranges, membership).
- Trade-offs: extra storage + slower writes due to index maintenance.

## Links

- Concepts: https://zvec.org/en/docs/concepts/
- Data modeling: https://zvec.org/en/docs/concepts/data-modeling/
- Vector embedding: https://zvec.org/en/docs/concepts/vector-embedding/
- Vector index: https://zvec.org/en/docs/concepts/vector-index/
- Inverted index: https://zvec.org/en/docs/concepts/inverted-index/
