# Qdrant Indexing — overview (ingested: indexing concept page)

Source: https://qdrant.tech/documentation/concepts/indexing/

This note summarizes the indexing model and the handful of decisions that most teams actually need.

## Mental model (how to think about indexes)

- Qdrant combines **vector indexes** (for similarity search) with **payload indexes** (for filtering and query planning).
- Index configuration is applied at the **collection** level, but indexes may be built per-segment as data grows and optimizers decide it’s worthwhile.

## Payload indexes (what you need for fast filters)

- Payload indexes are created per field and type; they speed up filtering and help estimate filter selectivity.
- Index only fields you filter on frequently; indexes cost memory and build time.
- A practical heuristic from the guide: indexing fields with more distinct values often yields more benefit.

Supported payload index types mentioned include:
- keyword / integer / float / bool
- datetime
- uuid (doc notes this can be more memory-efficient than keyword for UUIDs)
- geo
- text (full-text)

### Parameterized integer index (performance trap)

- Integer indexes can be configured to support “lookup” (exact match) and/or “range”.
- The guide warns that enabling lookup in the wrong context can cause performance issues.

### On-disk payload indexes (memory vs latency)

- Default: payload-related structures are kept in memory for low latency.
- On-disk payload index exists for large/rarely used indexes to reduce memory pressure.
- Tradeoff: cold requests may be slower due to disk I/O.

### Tenant index / principal index (special-purpose)

- Tenant index: optimizes multi-tenant collections when most queries filter by tenant.
- Principal index: optimizes when most queries filter by a primary “timeline” field (e.g., timestamp).

## Full-text index (text filtering semantics)

- Full-text indexing enables token-based filtering on string payload.
- Key design choices:
  - tokenizer (word/whitespace/prefix/multilingual)
  - lowercasing / ASCII folding
  - stemming / stopwords (language-specific)
  - phrase matching (requires additional structure; enable explicitly)

Practical rule: text filter semantics depend on how you build the full-text index.

## Vector index (dense)

- The guide states dense vectors use an HNSW index.
- Parameters you’ll see:
  - `m` (graph degree)
  - `ef_construct` (build quality/speed)
  - `ef` (search-time quality/latency)
  - `full_scan_threshold` (when to skip HNSW)

Practical rule: don’t tune HNSW blindly — benchmark on your data.

## Sparse vector index

- Designed for sparse vectors (many zeros), conceptually closer to inverted-index style retrieval.
- Can be stored on disk to save memory, with expected latency tradeoffs.
- Supports dot-product similarity (as described in the guide).

## Filterable index / graph-filter interaction

- The guide describes additional mechanisms to keep graph traversal effective under filtering.
- Practical takeaway: the combination of vector search + filters has specific index support; strict multi-filter combinations may require special search algorithms.

## What to enforce in projects (portable)

- Treat payload indexes as mandatory for production filtered search.
- Prefer least number of indexed fields, chosen from actual query patterns.
- Decide early whether multi-tenancy will be “one collection per tenant” vs “shared collection + tenant index”.
- Document whether text filters require phrase semantics (and configure phrase matching accordingly).

