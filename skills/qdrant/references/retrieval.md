# Retrieval (Search, Filtering, Explore, Hybrid Queries)

Sources:
- https://qdrant.tech/documentation/concepts/search/
- https://qdrant.tech/documentation/concepts/filtering/
- https://qdrant.tech/documentation/concepts/explore/
- https://qdrant.tech/documentation/concepts/hybrid-queries/

This note consolidates the practical parts of Qdrant retrieval.

## Query API as the “front door”

- Qdrant’s universal retrieval interface is the Query API:
  - `POST /collections/{collection_name}/points/query`
- Treat the `query` parameter as the thing that changes behavior (nearest, by-id, hybrid, etc.).

## Search-time knobs (recall vs latency)

Common parameters that matter operationally:
- `hnsw_ef`: higher often improves recall but increases latency.
- `exact`: disables ANN (can be very slow; full scan).
- `indexed_only`: can protect latency during indexing but may return partial results.

## Result projection

- Results do not necessarily include payload/vectors by default.
- Use `with_payload` / `with_vectors` and projection (include/exclude fields) when you need them.

## Filtering model (boolean logic)

Filters are composed with:
- `must` (AND)
- `should` (OR)
- `must_not` (NOT)

Field conditions include:
- equality / IN / NOT IN (keyword/int/bool)
- numeric ranges
- datetime ranges (RFC 3339)
- geo filters
- array length (“values count”)
- empty/null semantics
- `has_id` and `has_vector`

### Nested arrays: correctness gotcha

If you filter arrays of objects and need multiple conditions to apply to the **same element**, use nested filtering patterns; otherwise you may accidentally match across different array elements.

## Explore (recommendation / discovery)

Use Explore when you need:
- recommendations from multiple positives and/or negatives
- discovery / context constrained search
- dataset exploration (e.g., outliers)

Operational notes:
- performance often scales with number of examples
- accuracy may require increasing `ef` for constrained discovery/context searches

## Hybrid and multi-stage retrieval

Qdrant supports multi-stage retrieval via `prefetch`:
- prefetch generates candidate sets
- the main query re-scores/ranks candidates

Important gotcha:
- `offset` applies only to the main query; ensure prefetch limits are large enough.

### Fusion patterns

When combining multiple channels (dense + sparse, or multiple embeddings):
- RRF (rank fusion) is a common default.
- Distribution-based score fusion (DBSF) can help when score scales differ.

### Diversity (MMR)

MMR helps reduce near-duplicate results; results may be ordered by selection process, not strictly by similarity score.

### Formula rescoring

Use formula-based rescoring to blend business signals (payload fields) with vector scores.
Rule of thumb: treat formula rescoring as a controlled, eval-driven feature (not a default).

## Practical rules of thumb

- Start simple: vector search + filter + payload projection.
- Add grouping/dedup only when needed (and index the group field).
- Add hybrid/multi-stage only when you can justify it with eval + latency budgets.
