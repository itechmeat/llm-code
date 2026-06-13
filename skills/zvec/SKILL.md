---
name: zvec
description: "Zvec in-process vector database. Covers collections, indexing, embeddings, reranking, and persistence. Use when embedding Zvec into applications or tuning retrieval/storage behavior. Keywords: Zvec, HNSW-RaBitQ, vector database, ANN."
metadata:
  version: "0.5.0"
  release_date: "2026-06-12"
---

# Zvec

Zvec is a lightweight, in-process vector database meant to be embedded into applications ("SQLite for vectors").

## Quick navigation

- Overview: `references/overview.md`
- Concepts: `references/concepts.md`
- Quickstart (first operations): `references/quickstart.md`
- Installation (only if needed): `references/installation.md`
- Index types & quantization: `references/indexing.md`
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

- Memory-sensitive ANN on x86_64
  - Prefer `HNSW-RaBitQ` when HNSW-quality recall matters but memory is the limiting factor.
  - Start with the documented defaults (`total_bits=7`, `num_clusters=16`) and tune query-time `ef` before changing quantization bits.

- Safe evolution of live collections
  - Add/drop/alter scalar columns via `add_column()`, `drop_column()`, `alter_column()`.
  - Manage indexes via `create_index()` / `drop_index()` (scalar). Vector indexes cannot be dropped.

## Critical prohibitions

- Do not mirror vendor docs verbatim; summarize in your own words.
- Do not assume a client/server deployment model: Zvec is in-process.
- Do not add project-specific paths, secrets, or environment assumptions.
- Do not choose `HNSW-RaBitQ` on unsupported hardware; current docs limit it to `x86_64` with `AVX2` or better.

## Release Highlights (0.5.0)

- **Full-text search (FTS)**: attach an FTS index to any string field via `create_index()` / `drop_index()` and query it with natural-language or structured expressions, alongside vector indexes.
- **Hybrid retrieval**: the `MultiQuery` API combines dense vectors, sparse vectors, scalar filters, and text in one query with consistent reranking across Python, Go, Rust, and C++.
- **DiskANN index**: keeps the bulk of the index on disk instead of RAM, cutting memory use for billion-scale datasets on memory-constrained hosts.
- **Output field selection**: `fetch()` accepts an `output_fields` parameter to control which fields are returned.
- **New SDKs and tooling**: official Go SDK (cgo, prebuilt Linux/macOS/Windows libs), Rust SDK (RAII, builder APIs), and Zvec Studio (`pip install zvec-studio`) for visual data browsing and query testing.

## Release Highlights (0.3.0 -> 0.4.0)

- **Windows** support and official Windows packages for Python and Node.js
- **HNSW-RaBitQ** quantized vector indexing for lower-memory ANN on supported x86_64 hosts
- **Stable C API** for building or maintaining additional language bindings
- **MCP server / agent skills** ecosystem for AI-driven collection management and retrieval workflows
- **0.3.1 hotfixes** for relaxed collection path restrictions and better Windows cross-drive/path handling
- **0.4.0** adds official Dart/Flutter bindings, iOS build support, a larger `topK` ceiling, stricter `query_params` validation, and fixes an SQ8 quantizer recall regression.

## Links

- Documentation: https://zvec.org/en/docs/
- GitHub: https://github.com/alibaba/zvec
- Releases: https://github.com/alibaba/zvec/releases
- Issues: https://github.com/alibaba/zvec/issues
