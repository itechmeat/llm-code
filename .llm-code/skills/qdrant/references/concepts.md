# Qdrant Concepts — overview (ingested: concepts landing page)

Source: https://qdrant.tech/documentation/concepts/

This note summarizes the **Concepts landing page** only. It is a navigation/terminology map rather than a deep technical spec.

## Concept map (from the docs TOC)

- **Collections**: named datasets that contain points.
- **Points**: the main record type; a point contains vector(s) and optional payload.
- **Payload**: metadata stored alongside vectors.
- **Search**: similarity search (retrieve nearest points in vector space).
- **Explore**: a set of APIs for exploring the collection beyond basic similarity search.
- **Hybrid Queries**: multi-stage or multi-query retrieval patterns.
- **Filtering**: database-style conditions and clauses.
- **Inference**: generating vectors (embeddings) from text or images.
- **Optimizer**: mechanisms to rebuild/optimize internal DB structures for faster search.
- **Storage**: segments, indexes, and ID mapping at a high level.
- **Indexing**: available index types (payload, vector, sparse vector, filterable).
- **Snapshots**: node-level backup/restore artifacts.

## What this page does NOT fully explain

The landing page itself does not provide detailed technical specifics on:
- vector distance metrics
- ANN index internals (e.g., HNSW)
- distributed topology (sharding/replication)
- security/auth/TLS

Those likely live in the linked sub-pages. Fetch them **one by one** and extend this skill.

## Next ingestion targets (sub-pages)

Recommended order:
1) Collections → 2) Points → 3) Payload → 4) Filtering → 5) Search → 6) Indexing → 7) Storage/Optimizer → 8) Snapshots

(Each should be ingested as a separate URL, with its own reference note if needed.)
