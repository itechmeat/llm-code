# Indexing

Zvec vector indexes control the trade-off between recall, latency, and memory. Choose the vector index per field when you design the collection schema.

## Index families

- `Flat` — exact/brute-force search. Best for tiny collections, correctness checks, and low-complexity baselines.
- `HNSW` — the general-purpose ANN choice when you want low latency with good recall.
- `HNSW-RaBitQ` — new in `0.3.0`; combines HNSW graph traversal with RaBitQ quantization to reduce memory while keeping strong recall.
- `IVF` — another approximate strategy supported by Zvec when you want a different latency/memory profile than HNSW.
- `DiskANN` — new in `0.5.0`; keeps the bulk of the index on disk instead of RAM, drastically cutting memory use for billion-scale datasets on memory-constrained hosts. As of `0.6.0` the C API covers DiskANN completely (index params, query params, vector/group-by/sub-query wiring), matching the HNSW/FTS C API, so C/C++ integrations no longer need workarounds for missing bindings. As of `0.7.0` it also runs on Linux ARM64 and macOS ARM64 (Apple Silicon), auto-selecting the best I/O backend (`io_uring`, `libaio`, or `pread`) with safe fallback; on macOS it uses `F_NOCACHE` and disables read-ahead for DiskANN files. As of `0.8.0` it runs on Windows too (asynchronous unbuffered reads through I/O completion ports) and on mobile (portable `pread` for Android and iOS).
- `FTS` — new in `0.5.0`; a full-text index attached to a string field (via `create_index()`), queried with natural-language or structured expressions for hybrid retrieval.

## Turbo module and pluggable quantizers (0.6.0+)

- Internally, quantization now lives behind a Quantizer abstraction in the Turbo module: index builders/searchers call a uniform interface instead of embedding quantization logic directly, so new quantizer implementations (int8 uniform, int8 record, PQ, RaBitQ, and more) can be added without touching index code. The first concrete implementation shipped is `Fp32Quantizer`, backed by scalar FP32 distance kernels. This is an internal architecture change; it does not add new Python-facing parameters by itself.
- INT8/INT4 quantization gained an optional `enable_rotate` flag that applies a random orthogonal rotation to vectors before quantizing, spreading variance evenly across dimensions and reducing quantization error. On the upstream cohere-1m benchmark this raised HNSW INT8 recall from 0.9285 to 0.9397, Flat INT8 from 0.9695 to 0.9881, and — most notably — HNSW INT4 recall from 0.2114 to 0.7117. Enable rotation whenever you use INT8/INT4 quantization; the recall gain (especially for INT4) is large enough that there is little reason to leave it off.

## Index and quantization additions (0.7.0+)

- **IVF RaBitQ** — RaBitQ quantization now also applies to `IVF` indexes, extending it beyond HNSW for more dense-vector retrieval scenarios; C and Python bindings are included.
- **Uniform uint7 / uint8 quantization** — exposed as new uniform quantizer options, giving more compression/recall trade-offs alongside INT8/INT4.
- **Turbo preprocessor framework** — quantizers can run a preprocessor before quantization; Fast Hadamard Transform (FHT) rotation is implemented now, and OPQ rotation shipped in `0.8.0` (dimensionality reduction is still not implemented).
- **Turbo PQ-INT8 quantizer** — PQ-based INT8 quantization in the Turbo framework covering L2, Cosine, and Inner Product metrics for higher compression.
- **Record quantizers in Turbo** — INT8/INT4 record quantization and FP16 quantizers migrated into the Turbo framework, with portable scalar distance kernels for non-SIMD targets; every quantization type now maps to exactly one explicit backend path.
- **RaBitQ runtime SIMD dispatch** — HNSW-RaBitQ selects AVX2 or AVX512 implementations at runtime from the host CPU, removing any need to hard-code the instruction set at build time.
- **Vamana two-pass graph build** — two-pass graph build path that improves graph quality on some datasets; optional in `0.7.0`, enabled by default since `0.8.0`.
- **HNSW build from original vectors** — the graph can be built from raw original vectors supplied by a provider while search still runs against the stored (lossy) vectors, improving graph quality when stored vectors are quantized/lossy.

## Index and quantization additions (0.8.0+)

- **Uniform `UINT4` quantization** — `UINT4` joins the `UINT7`/`UINT8` uniform quantizers, and all three are now wired into the database layer and HNSW, not just exposed as options. A shared quantization range means scores are no longer reconstructed per datapoint during queries. Trade-off: sharing min/max across all indexed points increases quantization error and reduces recall, so re-benchmark uniform-quantized indexes before switching an existing collection over.
- **Turbo PQ and FastScan** — `PQ-INT4` and a 4-bit PQ FastScan implementation with packed block scanning, plus SIMD and scalar distance kernels and precomputed residual distance tables for IVF.
- **OPQ preprocessing** — Optimized Product Quantization rotation in the Turbo framework; the training and serialization logic is consolidated across the PQ quantizers.
- **Shared page cache for vector indexes** — HNSW, IVF and DiskANN read through one buffer-backed cache with pinned reads and batched page access. DiskANN falls back to direct I/O under cache pressure, so a memory-constrained host degrades to uncached reads instead of failing.
- **Turbo distance kernels across index families** — Flat, HNSW, IVF and DiskANN distance computation migrated to Turbo with AVX2, AVX512, AVX512-FP16, SSE and ARM NEON kernels and runtime dispatch. The largest gains are on INT4 kernels and on Linux ARM workloads.
- **Refinement with FP16/UINT8 vectors** — HNSW and Vamana can refine candidates using FP16 or UINT8 vectors, with `scale_factor` controlling the candidate budget for that refinement pass.
- **RaBitQ on Windows `x86_64`** — RaBitQ indexes now work on Windows `x86_64`, in addition to the previously supported Unix `x86_64` hosts.

## When HNSW-RaBitQ is the right tool

Use `HNSW-RaBitQ` when all of the following are true:

- You run on `x86_64` hardware with `AVX2` (or better).
- HNSW-like recall matters, but the memory footprint of full-precision vectors is too large.
- Your vectors are between `64` and `4095` dimensions.

Avoid it on ARM hosts; the current upstream docs mark it unsupported there. Windows `x86_64` is supported since `0.8.0`.

## Practical tuning order

1. Start with the documented defaults: `total_bits=7`, `num_clusters=16`.
2. Tune query-time `ef` first for the recall/latency trade-off.
3. Lower `total_bits` only when you explicitly need more compression and can accept some recall loss.
4. Increase `sample_count` only when the training sample quality is the bottleneck for very large datasets.

## Main parameters

### Index build parameters

- `metric_type` — choose the same distance metric your embeddings were trained for.
- `m` — more graph links improve recall but increase memory/build cost.
- `ef_construction` — larger build-time candidate pool improves graph quality and slows indexing.
- `total_bits` — main memory/accuracy control for RaBitQ.
- `num_clusters` — clustering granularity for the quantization training step.
- `sample_count` — training sample size (`0` means use all vectors).

### Query parameters

- `ef` — main recall/latency control at query time.
- `radius` — optional score threshold for range-style filtering.
- `is_linear` — bypass the index for brute-force verification or tiny datasets.
- `is_using_refiner` — re-score top candidates with exact distances when precision matters more than latency.

## FTS tokenizer and stemmer (0.6.0)

- The standard tokenizer now implements Unicode 17 UAX #29 word-boundary rules (replacing the earlier general-category tokenizer), giving Lucene-style token selection for alphanumeric, numeric, ideographic, hiragana, katakana, hangul, Southeast Asian scripts, regional indicators, and common emoji sequences.
- Text analysis is backed by utf8proc 2.11.3, adding Unicode-aware word boundary detection and codepoint-aware lowercasing, plus a new ASCII-folding token filter that maps accented/Unicode characters to their ASCII equivalents (useful for accent-insensitive matching).
- A Snowball-based stemmer token filter reduces words to their root form and covers 34+ languages; select the language via `stemmer_lang` in the index's `extra_params`. A typical English filter chain is `["lowercase", "stemmer"]`, with `ascii_folding` added when diacritics need to be normalized.
- An **ngram tokenizer** (`0.7.0+`) is available for character-level matching, useful for short text, code, or pinyin; configure it via the index's `extra_params`.
- **Chinese segmentation** uses Jieba. Since `0.8.0` the default dictionary and HMM model are embedded in the native libraries and the global dictionary configuration was removed; see `references/fts-chinese-dictionaries.md`.
- FTS conjunction (AND) and phrase queries got a block-max skip plus score early-exit optimization in the conjunction iterator: entire non-competitive 128-document blocks are skipped by checking block-max score upper bounds, and scoring short-circuits once the remaining upper bound cannot beat the current threshold. On a 500k-document benchmark this made AND queries 22-38% faster and phrase queries 33% faster, with no query-syntax changes required.

## Operator guidance

- Keep one clear reason for each vector index choice; vector indexes cannot be dropped later without redesigning the collection.
- After heavy ingestion, run `collection.optimize()` so the configured vector index catches up with buffered writes.
- For memory-sensitive production deployments on supported x86_64 servers, `HNSW-RaBitQ` is the new first thing to evaluate before overprovisioning RAM.
- `0.4.0` fixes an SQ8 quantizer recall regression caused by incorrect int8 rounding metadata handling. Re-benchmark quantized indexes before keeping older compensating thresholds or fallback logic.
- Sparse vector indices are now sorted before reaching the core engine, so custom pipelines should not rely on preserving caller-provided sparse-index order as implicit behavior.
- Group-by search (0.6.0+) is supported on Flat, HNSW, HNSW-RaBitQ, and sparse indexes; see `references/data-operations.md` for the query-side parameters.
- `0.8.0` uniform quantizers (`UINT4`/`UINT7`/`UINT8`) use one shared quantization range instead of reconstructing scores per datapoint. Sharing min/max across all indexed points increases quantization error and lowers recall, so re-benchmark before converting an existing collection.
- `0.8.0` enables Vamana two-pass graph construction by default; expect a longer build in exchange for better graph quality.
- `0.8.0` routes HNSW, IVF and DiskANN through one shared page cache. On memory-constrained hosts DiskANN falls back to direct I/O under cache pressure, which shows up as latency spikes rather than errors.

## Links

- Vector index overview: https://zvec.org/en/docs/db/concepts/vector-index/
- HNSW-RaBitQ: https://zvec.org/en/docs/db/concepts/vector-index/hnsw-rabitq-index/
- Python API params: https://zvec.org/api-reference/python/params/
