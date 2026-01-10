# Storage (Qdrant Concepts) — practical notes

Source: https://qdrant.tech/documentation/concepts/storage/

## Segment model (what to remember)

- A collection’s data is split into **segments**.
- Each segment has its own:
  - vector storage
  - payload storage
  - vector + payload indexes
  - ID mapper (internal ↔ external IDs)
- Segments usually do not overlap; if a point ends up in multiple segments, Qdrant has **deduplication** in search.

Appendable vs non-appendable:
- Segments can be **appendable** or **non-appendable** depending on storage/index choices.
- Appendable segments allow add/delete/query.
- Non-appendable segments allow read/delete only.
- A collection must have at least one appendable segment.

Why this matters operationally:
- Many performance behaviors (optimizer, indexing, memmap) are segment-scoped.

## Vector storage: In-memory vs Memmap (on-disk)

Qdrant provides two main vector storage modes:

- **In-memory**: vectors live in RAM; fastest for search; disk mostly used for persistence.
- **Memmap (on-disk)**: vectors live in memory-mapped files; OS page cache controls what is resident.
  - With enough RAM, it can be close to in-memory performance.
  - Typically preferred for large collections when RAM is limited and disks are fast.

### How to enable memmap

Two main approaches:

1) Collection creation: set `vectors.on_disk=true`.
- Recommended when you know upfront you want memmap for the whole collection.

2) Threshold-based conversion: set `memmap_threshold`.
- Can be configured globally and/or per collection.
- Segments above the threshold are converted to memmap storage.

Rule of thumb (from docs):
- Balanced workload: set `memmap_threshold` ≈ `indexing_threshold` (default mentioned as 20000 in docs).
  - This helps avoid extra optimizer runs by aligning thresholds.
- High write load + low RAM: set `memmap_threshold` lower than `indexing_threshold` (e.g. 10000).
  - Converts to memmap earlier; indexing happens later.

### HNSW index on disk

- You can also store the HNSW index on disk using `hnsw_config.on_disk=true` (per collection create/update).

Practical implication:
- “Vectors on disk” and “HNSW on disk” are separate knobs; decide per workload and disk speed.

## Payload storage: InMemory vs OnDisk

Payload storage types:
- **InMemory payload**: payload data loaded into RAM on startup; persistent backing on disk (and Gridstore per docs).
  - Fast, but can consume a lot of RAM for large payload values (long text, images).
- **OnDisk payload**: payload read/write directly to RocksDB.
  - Lower RAM usage, but higher access latency.

Critical performance rule:
- If you filter/search using payload conditions and payload is on disk, create **payload indexes** for the fields used in filters.
- Once a payload field is indexed, Qdrant keeps values of that indexed field in RAM **regardless** of payload storage type.

How to choose (practical):
- Large payload values that you don’t filter on → consider on-disk payload.
- Any payload fields used in filters/scoring → index them.

## Versioning + WAL (crash safety)

Qdrant uses a two-stage write path for integrity:

1) Write to **WAL** (write-ahead log): orders operations and assigns sequential numbers.
2) Apply changes to segments.

Each segment tracks:
- the last applied version
- per-point version

If an operation’s sequence number is older than the current point version, it is ignored.

Operational implication:
- WAL enables safe recovery after abnormal shutdown.
- Versioning prevents out-of-order updates from corrupting point state.

## Operational guidelines

- Prefer memmap vectors + (optional) on-disk HNSW when collections grow beyond RAM.
- Keep filter-critical payload fields indexed; avoid "disk payload + unindexed filters".
- Bulk ingestion workflows should align `memmap_threshold` and indexing thresholds.
