# Indexing

Zvec vector indexes control the trade-off between recall, latency, and memory. Choose the vector index per field when you design the collection schema.

## Index families

- `Flat` — exact/brute-force search. Best for tiny collections, correctness checks, and low-complexity baselines.
- `HNSW` — the general-purpose ANN choice when you want low latency with good recall.
- `HNSW-RaBitQ` — new in `0.3.0`; combines HNSW graph traversal with RaBitQ quantization to reduce memory while keeping strong recall.
- `IVF` — another approximate strategy supported by Zvec when you want a different latency/memory profile than HNSW.

## When HNSW-RaBitQ is the right tool

Use `HNSW-RaBitQ` when all of the following are true:

- You run on `x86_64` hardware with `AVX2` (or better).
- HNSW-like recall matters, but the memory footprint of full-precision vectors is too large.
- Your vectors are between `64` and `4095` dimensions.

Avoid it on ARM hosts; the current upstream docs mark it unsupported there.

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

## Operator guidance

- Keep one clear reason for each vector index choice; vector indexes cannot be dropped later without redesigning the collection.
- After heavy ingestion, run `collection.optimize()` so the configured vector index catches up with buffered writes.
- For memory-sensitive production deployments on supported x86_64 servers, `HNSW-RaBitQ` is the new first thing to evaluate before overprovisioning RAM.

## Links

- Vector index overview: https://zvec.org/en/docs/db/concepts/vector-index/
- HNSW-RaBitQ: https://zvec.org/en/docs/db/concepts/vector-index/hnsw-rabitq-index/
- Python API params: https://zvec.org/api-reference/python/params/
