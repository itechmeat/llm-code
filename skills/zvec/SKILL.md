---
name: zvec
description: "Zvec in-process vector database. Covers collections, embedding, reranking, persistence. Use when embedding Zvec as an in-process vector database, managing collections, configuring embedding/reranking, or running approximate nearest-neighbor searches. Keywords: Zvec, vector DB, ANN, SQLite for vectors."
metadata:
  version: "0.2.0"
  release_date: "2026-02-13"
---

# Zvec

Zvec is a lightweight, in-process vector database meant to be embedded into applications ("SQLite for vectors").

## Quick navigation

- Overview: `references/overview.md`
- Concepts: `references/concepts.md`
- Quickstart (first operations): `references/quickstart.md`
- Installation (only if needed): `references/installation.md`
- Embedding pipelines: `references/embedding.md`
- Reranking pipelines: `references/reranker.md`
- Data modeling & collections: `references/collections.md`
- CRUD / search operations: `references/data-operations.md`
- Configuration & persistence: `references/configuration.md`

## Operator recipes (high signal)

- Minimal “embed Zvec” checklist
  - (Optional) Configure globals once at startup via `zvec.init(...)` (logging, `query_threads`).
  - Create a collection on disk with `create_and_open(path=..., schema=..., option=...)`.
  - Ingest documents as `Doc(id=..., fields=..., vectors=...)` via `insert()` or `upsert()`.
  - Query via `collection.query(vectors=VectorQuery(...), topk=...)`.
  - Call `collection.optimize()` periodically after heavy ingestion.

- Bulk ingest + keep query latency stable
  - Prefer batched `insert()` / `upsert()`.
  - Monitor `collection.stats` and run `optimize()` when flat buffers grow.

- Hybrid retrieval patterns
  - Filter-only: `collection.query(filter=..., topk=...)`.
  - Vector + filter: pass both `vectors=...` and `filter=...`.
  - Multi-vector fusion: pass multiple `VectorQuery` items and rerank using `WeightedReRanker` or RRF.

- Safe evolution of live collections
  - Add/drop/alter scalar columns via `add_column()`, `drop_column()`, `alter_column()`.
  - Manage indexes via `create_index()` / `drop_index()` (scalar). Vector indexes cannot be dropped.

## Critical prohibitions

- Do not mirror vendor docs verbatim; summarize in your own words.
- Do not assume a client/server deployment model: Zvec is in-process.
- Do not add project-specific paths, secrets, or environment assumptions.

## Links

- Documentation: https://zvec.org/en/docs/
- GitHub: https://github.com/alibaba/zvec
- Releases: https://github.com/alibaba/zvec/releases
- Issues: https://github.com/alibaba/zvec/issues
