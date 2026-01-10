# Optimizer (Qdrant Concepts) — practical notes

Source: https://qdrant.tech/documentation/concepts/optimizer/

## Why optimizer exists (mental model)

Qdrant stores data in **segments**. Many changes are more efficient in **batches** than “in-place per point”, so Qdrant periodically **rebuilds** internal structures at segment level.

Key availability property:
- The segment being optimized remains **readable** during rebuild.
- Writes/updates during optimization go into a **copy-on-write** segment (proxy layer), which takes priority for reads and subsequent updates.

Practical implication:
- Optimization is expected background work. Plan for CPU/Disk IO spikes and don’t treat it as an outage.

## Vacuum optimizer (garbage of deleted points)

Deletion is logical first:
- Qdrant marks records as deleted and ignores them in queries.
- This minimizes disk IO, but over time deleted records accumulate → memory usage and performance can degrade.

Vacuum optimizer triggers when a segment accumulates “too many” deletions.

Relevant config knobs:
- `storage.optimizers.deleted_threshold`: minimal fraction of deleted vectors in a segment to start vacuum.
- `storage.optimizers.vacuum_min_vector_number`: minimal vectors in a segment before vacuum makes sense.

Operational guidance:
- If you do frequent deletes (e.g., reingestion, dedup), watch for vacuum activity and disk usage.

## Merge optimizer (too many small segments)

Too many small segments hurt search performance.
Merge optimizer tries to reduce segment count:
- Target segment count: `storage.optimizers.default_segment_number` (defaults to CPU count when 0).
- It merges (at least) the smallest segments.
- It avoids creating overly large segments via `storage.optimizers.max_segment_size_kb`.

Tradeoff note from docs:
- Lower `max_segment_size_kb` can prioritize faster indexation.
- Higher `max_segment_size_kb` can prioritize search speed (fewer segments), but risks long index build times per segment.

Practical guidance:
- Treat segment count as a performance lever: fewer segments typically helps search parallelism overhead, but “too large” segments make rebuilds expensive.

## Indexing optimizer (when to turn on indexes / memmap)

Qdrant can switch storage/index modes based on dataset size. Small datasets can be faster with brute-force scan.

Indexing optimizer enables:
- vector indexing
- memmap storage
…when thresholds are reached.

Relevant config knobs:
- `storage.optimizers.memmap_threshold` (kB per segment): above this, vectors become read-only **memmap**. Set to `0` to disable.
- `storage.optimizers.indexing_threshold_kb` (kB per segment): above this, enables vector indexing. Set to `0` to disable.

Practical implication:
- These thresholds strongly affect memory vs latency behavior; choose them intentionally for your workload.

## Per-collection optimizer overrides + dynamic tuning

In addition to global config, optimizer parameters can be set **per collection**.

Docs highlight a common production pattern:
- During bulk initial load, disable indexing / expensive rebuild behavior.
- After ingestion finishes, enable indexing so the index is built once (instead of rebuilding repeatedly during upload).

## Operational guidelines

- Collections can have different lifecycles (churny vs append-only).
- Bulk backfills / re-embeddings should use the "disable indexing during upload, re-enable after" pattern to save compute.
