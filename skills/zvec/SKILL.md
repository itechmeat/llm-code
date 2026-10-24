---
name: zvec
description: "Zvec in-process vector database. Covers collections, indexing, embeddings, reranking, and persistence. Use when embedding Zvec into applications or tuning retrieval/storage behavior. Keywords: Zvec, HNSW-RaBitQ, vector database, ANN."
metadata:
  version: "0.8.0"
  release_date: "2026-10-21"
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
- Chinese FTS dictionaries (Jieba): `references/fts-chinese-dictionaries.md`
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

- Chinese full-text search
  - The default Jieba dictionary and HMM model are embedded in the native libraries; nothing to install.
  - Override the main dictionary per FTS field with `extra_params.jieba_dict_dir`, or set `ZVEC_JIEBA_DICT_DIR`; field configuration wins over the environment variable.
  - Add domain vocabulary with `user_dict_path`; custom user dictionaries stay isolated between tokenizer instances.
  - The global `init(jieba_dict_dir=...)` configuration was removed in `0.8.0` — see `references/fts-chinese-dictionaries.md` for the migration.

## Critical prohibitions

- Do not mirror vendor docs verbatim; summarize in your own words.
- Do not assume a client/server deployment model: Zvec is in-process.
- Do not add project-specific paths, secrets, or environment assumptions.
- Do not choose `HNSW-RaBitQ` on unsupported hardware; it stays limited to `x86_64` with `AVX2` or better (Windows `x86_64` included since `0.8.0`).
- Do not call `init(jieba_dict_dir=...)` or the `set_default_jieba_dict_dir()` / `get_default_jieba_dict_dir()` helpers — removed in `0.8.0`. Configure the FTS field or use `ZVEC_JIEBA_DICT_DIR`.

## Release Highlights (0.8.0)

- **Jieba global dictionary configuration removed (breaking).** `init(jieba_dict_dir=...)`, `set_default_jieba_dict_dir()`, `get_default_jieba_dict_dir()` and the matching C/C++ global-directory APIs are gone; the default dictionary and HMM model are embedded in the native libraries. Override the main dictionary per field with `FtsIndexParam.extra_params.jieba_dict_dir` or the `ZVEC_JIEBA_DICT_DIR` env var (field configuration wins); add business vocabulary with `user_dict_path`. Migration: `references/fts-chinese-dictionaries.md`.
- **Embedded Chinese FTS dictionary.** The default Jieba dictionary and HMM model ship as LZ4-compressed resources in the Python wheels and native SDKs. Parsed defaults are shared across tokenizer instances, while custom user dictionaries stay isolated between them.
- **Uniform quantization wired into collections.** Uniform `UINT4` joins `UINT7`/`UINT8`, and all three are now connected to the database layer and HNSW. A shared quantization range removes per-datapoint score reconstruction at query time; sharing min/max across all indexed points increases quantization error and lowers recall.
- **Turbo PQ and FastScan.** `PQ-INT4` plus a 4-bit PQ FastScan implementation with packed block scanning, SIMD and scalar distance kernels, and precomputed residual distance tables for IVF.
- **OPQ preprocessing.** Optimized Product Quantization rotation in the Turbo framework; training and serialization logic is consolidated across the PQ quantizers.
- **Shared page cache for vector indexes.** HNSW, IVF and DiskANN read through one buffer-backed cache with pinned reads and batched page access; DiskANN falls back to direct I/O under cache pressure.
- **More flexible identifiers.** Document IDs accept valid UTF-8 up to 1024 bytes; collection names accept 1–256 bytes of valid UTF-8 (no control or separator characters); field names keep an ASCII charset, are capped at 64 bytes, and reject reserved internal names.
- **Wider platform coverage.** Intel Mac (macOS `x86_64`) builds, Windows ARM64 with MSVC plus Windows ARM64 SDK packages, and native Python 3.11–3.14 wheels.
- **DiskANN beyond Linux/macOS.** DiskANN now runs on Windows (asynchronous unbuffered reads through I/O completion ports) and on mobile (portable `pread` for Android and iOS). RaBitQ indexes work on Windows `x86_64`.
- **Turbo distance kernels across index families.** Flat, HNSW, IVF and DiskANN migrated to Turbo distance computation with AVX2, AVX512, AVX512-FP16, SSE and ARM NEON kernels selected at runtime; the largest gains are on INT4 kernels and Linux ARM workloads.
- **Cheaper builds, faster HNSW RaBitQ.** IVF and DiskANN builds use less memory (fewer vector copies, streamed merged inputs, bounded temporary buffers); HNSW RaBitQ construction reuses raw vectors during neighbor pruning and batches Flat provider lookups under segment locking.
- **Vamana search and refinement.** Split contiguous packed layout, optimized candidate state and prefetching, corrected medoid selection, and two-pass graph construction enabled by default. HNSW and Vamana can refine with FP16 or UINT8 vectors, with `scale_factor` controlling the candidate budget.
- **Stability fixes.** `fetch()`/`query()` no longer crash or lose rows when racing a segment switch or flush; reads of writing segments are synchronized; Flat cache synchronization and key-map iterator lifetimes are fixed; vector-to-row mappings survive index rebuilds containing deleted rows; IVF `n_iters` propagation is corrected.

## Release Highlights (0.7.0)

- **C++ API is now snake_case (breaking).** `Index`, `Collection` and methods like `Open()`, `Search()`, `Query()`, `Insert()` moved to `index`, `collection`, `open()`, `search()`, `query()`, `insert()`. C and Python API names are unchanged. See `references/data-operations.md` for migration notes.
- **Wider DiskANN platform support.** DiskANN indexes now run on Linux ARM64 and macOS ARM64 (Apple Silicon), auto-selecting the best I/O backend.
- **New index and quantization options.** IVF RaBitQ, uniform uint7/uint8 quantizers, a Turbo PQ-INT8 quantizer (L2/Cosine/IP), Turbo record quantizers with portable scalar distance kernels, and an optional Fast Hadamard Transform (FHT) preprocessor before quantization.
- **RaBitQ runtime SIMD dispatch.** HNSW-RaBitQ selects AVX2 or AVX512 at runtime from the host CPU, so no instruction set needs to be hard-coded at build time.
- **Better HNSW graph quality.** Optional Vamana two-pass graph build, and building the graph from the original (unquantized) vectors while search still runs against the stored lossy vectors.
- **FTS ngram tokenizer.** A character-level tokenizer for short text, code, or pinyin, configured via the index `extra_params`.
- **`DocIterator`.** Stream the full collection as a snapshot without loading it into memory; exposed across the C++, C, and Python bindings.
- **Concurrent `optimize()`.** Reads and writes now proceed while optimization runs, so long optimizations no longer stall ingest or retrieval.

## Release Highlights (0.6.0)

- **Pluggable Turbo quantizer**: the Turbo module now exposes a Quantizer abstraction with a uniform interface, decoupling quantization logic from index builders/searchers so future quantizers (int8 uniform, int8 record, PQ, RaBitQ, and more) can plug in without touching index code. Ships with a first `Fp32Quantizer` implementation and scalar FP32 distance kernels.
- **Random rotation for INT8/INT4 quantization**: an optional random orthogonal rotation (`enable_rotate`) spreads variance evenly across dimensions before quantizing, cutting quantization error. On the cohere-1m benchmark this took HNSW INT8 recall from 0.9285 to 0.9397, Flat INT8 from 0.9695 to 0.9881, and HNSW INT4 recall from 0.2114 to 0.7117 — a large jump that makes INT4 viable in more scenarios.
- **Group-by search**: query results can now be deduplicated/grouped so you get the top-K per group instead of top-K globally, across Flat, HNSW, HNSW-RaBitQ, and sparse indexes (with `fetch_vector`, `is_linear`, and `bf_pks` query modes), exposed through the Python API.
- **Zero-copy Python vector queries**: the Python query path now points `VectorViewClause` directly at the source numpy buffer instead of memcpy-ing through `serialize_vector`, removing redundant copies for dense vector queries.
- **Richer FTS tokenization**: the standard tokenizer now implements Unicode 17 UAX #29 word-boundary rules (Lucene-style handling for alphanumeric, ideographic, hiragana/katakana/hangul, Southeast Asian scripts, and emoji), backed by utf8proc 2.11.3 for Unicode-aware lowercasing and a new ASCII-folding filter. A Snowball-based stemmer token filter (34+ languages, set via `stemmer_lang`) reduces words to their root form.
- **Complete DiskANN C API**: the C API now covers DiskANN end to end — index param getters/setters, query param CRUD, and query wiring for vector queries, group-by queries, and sub-queries — matching the existing HNSW/FTS C API patterns.
- **Faster FTS conjunction/phrase queries**: block-max skip plus score early-exit in the conjunction iterator skip non-competitive 128-doc blocks outright; benchmarked on a 500k-doc dataset this made AND queries 22-38% faster and phrase queries 33% faster.
- **Stability fixes**: assorted fixes to FTS correctness (segment stats on reopen, zero-match filter semantics, compaction doc-id gaps), index race conditions in DiskANN/HNSW/IVF, SQL engine group-by parameter handling, and collection LOCK-file behavior for read-only collections.

## Release Highlights (0.5.1)

- **External vector source**: ingest and query from external vector sources for more flexible data pipelines without first copying everything into the collection.
- **Zero-copy query path**: `VectorViewClause` establishes a zero-copy vector query path with unified query validation, lowering per-query memory overhead.
- **Search prefetch tuning**: pass prefetch settings (`PO`, `PL`) directly through search parameters for finer performance control.
- **Index/storage controls**: `is_dirty` is exposed on the core `Index` interface, and copy-on-write MMAP options (with a corrected `MMAP_POPULATE` placement) are configurable.
- **C API FTS sub-queries**: full-text search now works inside sub-queries via the C API.

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
- Release notes (0.8.0): https://github.com/alibaba/zvec/releases/tag/v0.8.0
- Issues: https://github.com/alibaba/zvec/issues
