```markdown
# Qdrant Collections — overview (ingested: collections concept page)

Source: https://qdrant.tech/documentation/concepts/collections/

This note captures what a collection is, what configuration choices matter in practice, and which lifecycle operations are operationally important.

## What a collection is

- A **collection** is a named set of points (vectors + optional payload).
- Within a collection, vectors must be comparable under a metric and dimensionality constraints.
- You can store **multiple vectors per point** using **named vectors** (each named vector can have its own size + distance metric).

## Distance metrics (practical notes)

- Supported metrics: `Dot`, `Cosine`, `Euclid`, `Manhattan`.
- Cosine similarity is implemented as dot product over normalized vectors; vectors are normalized on upload.

## Multitenancy decision: one collection vs many

The page explicitly calls out a key design choice:
- Prefer **one collection + payload-based partitioning** for “most cases” (the multitenancy approach).
- Use **multiple collections** when you need stronger isolation and you have a limited number of tenants/users; note that many collections can create overhead and cross-impact performance.

Practical takeaway:
- Decide early whether your tenant boundary is a payload field (single collection) or a collection boundary (many collections), and align indexing + access control with that choice.

## Create collection: what you must decide up front

At minimum:
- vector size (embedding dimensionality)
- distance metric

High-value optional knobs the page lists:
- `hnsw_config` (vector index behavior; see Indexing)
- `wal_config` (write-ahead log behavior; impacts ingestion durability/perf)
- `optimizers_config` (background optimization/compaction behavior)
- `shard_number` (sharding; relevant for distributed deployments)
- `on_disk_payload` (store payload on disk only; trades RAM for I/O)
- `quantization_config` (memory/speed tradeoffs)
- `strict_mode_config` (protect against expensive queries / unsafe operations)

## Keeping vectors on disk (memmap mode)

- Vectors are normally in RAM for fast access.
- You can store vectors on disk via `on_disk` in vector configuration.
- Disk vectors enable memmap-based storage, which is useful for large ingestions.

## Multiple vectors per point (named vectors)

- Named vectors let you keep multiple embeddings per point (e.g., `image`, `text`).
- Per-vector overrides are possible (e.g., vector-specific `hnsw_config`, `quantization_config`, `on_disk`).

## Vector datatypes (compressed embeddings)

- Qdrant supports `uint8` vectors (useful for providers that ship pre-quantized embeddings).
- Tradeoff: lower memory + potentially faster search, at the cost of precision.

## Sparse vectors (for text-style retrieval)

- Sparse vectors are first-class and must be **named**.
- Their distance is always `Dot`.
- Sparse vectors have optional tuning knobs via the sparse index configuration (see Indexing).

## Operational lifecycle endpoints worth remembering

- Existence check endpoint: `/collections/{collection_name}/exists`.
- Delete collection is explicit and irreversible (data loss).
- Collection info (`GET /collections/{name}`) exposes:
  - collection status (`green`/`yellow`/`grey`/`red`)
  - points/vectors counts (with important caveats)
  - effective config (params, HNSW, optimizer, WAL)

## Important operational caveats

- `points_count` / `indexed_vectors_count` are documented as **approximate** and can temporarily diverge due to internal optimization; do not use them as source-of-truth metrics.
- Index creation can be delayed depending on `indexing_threshold`; small collections may show `indexed_vectors_count = 0` even when inserts succeeded.
- Updating collection parameters can be blocking and may trigger heavy background rebuilds; the page recommends against using update-collection in production due to overhead risk.

## Grey collection status (after restart)

- Grey status can occur if Qdrant restarted while optimizations were in progress.
- The page says you need to send **any update operation** to trigger optimizations again (or use the Web UI “Trigger Optimizers”).

## Aliases (blue/green pattern)

- Collection aliases are atomic switches to route queries to different underlying collections.
- Useful for safe rebuilds: build a new collection in the background, then switch the alias.

## Next ingestion targets (one URL at a time)

- Search page (connect collection config + filtering/indexing knobs to search-time parameters)
- Snapshots page (to build an ops backup/restore runbook)

```
