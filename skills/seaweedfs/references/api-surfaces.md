# API Surfaces

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Master-Server-API
- https://github.com/seaweedfs/seaweedfs/wiki/Volume-Server-API
- https://github.com/seaweedfs/seaweedfs/wiki/Filer-Server-API
- https://github.com/seaweedfs/seaweedfs/wiki/Client-Libraries
- https://github.com/seaweedfs/seaweedfs/wiki/SeaweedFS-Java-Client

## Master Server API

### What this page is about

- It documents the master HTTP endpoints for id assignment, lookup, volume growth, collection deletion, health, and topology status.
- It explains how write placement, vacuum triggering, and writable-volume inventory are exposed operationally.
- It shows that the master API is the control-plane surface for capacity and placement decisions.

### Actionable takeaways

- Use `dir/assign` when clients or higher-level services need file ids with explicit placement constraints such as replication, collection, rack, TTL, or disk label.
- Reserve batches of file ids with `count` only when the client understands the suffix format (`_1`, `_2`, etc.) and can consume them safely.
- Use `dir/lookup` for current volume locations and for JWT-bearing file-specific lookups when update/delete authorization flows need them.
- Inspect `dir/status` and `vol/status` to confirm writable capacity, topology spread, disk tags, and actual volume state before changing placement policy.
- Pre-grow writable capacity with `vol/grow` ahead of bucket launches, TTL changes, or new replication classes so writes do not stall on empty pools.
- Trigger `vol/vacuum` manually only when you understand the compaction cost; it rewrites live data and swaps volume files rather than reclaiming space instantly.
- Use `cluster/status` and `cluster/healthz` for control-plane checks in load balancers, orchestrators, and readiness probes.
- Delete a collection with `col/delete` only when the lifecycle really intends to remove all corresponding volumes.
- Prefer `pretty=y` only for human inspection; keep machine integrations tolerant of compact JSON.

### Gotchas / prohibitions

- Do not treat master APIs as free of side effects; `vol/grow`, `vol/vacuum`, and `col/delete` materially change cluster state.
- Do not trigger vacuum aggressively on busy clusters without understanding IO impact and readonly transitions during compaction.
- Do not assume write placement will work unless matching writable volumes exist for the exact `<collection, replication, ttl, disk>` combination.
- Do not forget that disk labels and topology selectors narrow the eligible placement pool.

### How to apply in a real repo

- Separate read-only inspection endpoints from mutating admin endpoints in automation.
- Put `dir/status`, `vol/status`, `cluster/status`, and `cluster/healthz` into diagnostics and health dashboards.
- Add guarded runbooks for `vol/grow`, `vol/vacuum`, and `col/delete` with approval steps and expected blast radius.

## Volume Server API

### What this page is about

- It documents the data-plane HTTP interface for reading, writing, deleting, and inspecting file ids on volume servers.
- It includes practical request headers for authorization, conditional reads, gzip, ranges, and metadata.
- It exposes health and status endpoints suitable for orchestration and diagnostics.

### Actionable takeaways

- Treat direct volume URLs as the low-level object path for GET, HEAD, PUT/POST, and DELETE by file id.
- Require JWT authorization on direct read or write flows when security is enabled; the page documents bearer tokens issued by master.
- Use HTTP range requests and conditional headers (`If-Modified-Since`, `If-None-Match`) for efficient client downloads and cache validation.
- Use image resize/crop query parameters only when that server-side transformation behavior is intentionally part of the application contract.
- Send `Content-MD5` for integrity-sensitive uploads and `Seaweed-*` headers only for small, deliberate custom metadata.
- Use the direct master `/submit` convenience upload only for simple workflows; it trades placement control for convenience.
- Inspect `/status` for per-volume file counts, delete counts, and readonly state when debugging compaction, garbage, or capacity anomalies.
- Use `/healthz` for liveness and readiness probes because it reflects the local node's own health and master connectivity.

### Gotchas / prohibitions

- Do not use the master `/submit` shortcut for workflows that need explicit replication, TTL, collection, or disk placement choices.
- Do not rely on `readDeleted=true` after restarts or compaction; the page explicitly limits it.
- Do not attach unbounded custom metadata; the `Seaweed-*` payload is stored as JSON and intended to stay below `64KB`.
- Do not expose direct volume endpoints broadly if your security model expects clients to go through filer or S3 instead.

### How to apply in a real repo

- Decide explicitly which clients may talk to volume servers directly and which must use filer or S3 gateways.
- Put `/healthz` and `/status` into volume-server operational checks.
- Document upload integrity expectations, supported metadata headers, and any sanctioned image transformation behavior.

## Filer Server API

### What this page is about

- It documents the path-based HTTP interface for file and directory reads, writes, appends, metadata, moves, copies, listing, tagging, and deletion.
- It clarifies how filer parameters map to placement, chunking, TTL, and metadata behavior.
- It captures several important operational caveats around retries, append chunk growth, and recursive deletion.

### Actionable takeaways

- Use filer APIs when applications want path semantics, automatic directory creation, or protocol-friendly file operations instead of raw volume ids.
- Set placement fields (`collection`, `replication`, `dataCenter`, `rack`, `dataNode`) on writes only when the workload truly needs them; otherwise keep routing simple.
- Enable write retries at the client layer because the page explicitly recommends them for filer writes.
- Keep append sizes reasonably large, because every append creates another chunk reference in metadata.
- Use `metadata=true` for inspection tooling and JSON directory listing with pagination (`lastFileName`, `limit`) for scalable browsing.
- Prefer file tagging through `Seaweed-*` headers when you need lightweight custom attributes stored with filer metadata.
- Use `mv.from` for metadata-only renames and relocations; use `cp.from` when you need an independent copy and accept size-dependent cost for chunked files.
- Treat empty-folder creation as an explicit POST only when the workload needs directory placeholders.
- Use `skipChunkDeletion=true` only for expert workflows that intentionally leave chunks behind, such as special migration or metadata repair scenarios.

### Gotchas / prohibitions

- Do not build a small-append-heavy workload without chunk-growth controls; metadata can fragment badly.
- Do not assume `cp.from` is metadata-only for large files; chunked copies duplicate data.
- Do not use recursive delete or `skipChunkDeletion` casually, because they can create large blast radius or orphaned data.
- Do not skip parent directory checks blindly for latency gains unless the calling workflow guarantees directory correctness.

### How to apply in a real repo

- Offer filer as the default integration surface for file-oriented applications and document when S3 is a better fit.
- Standardize write retry policy, append sizing, tagging conventions, and recursive delete safeguards.
- Expose directory listing pagination and metadata-read patterns in application integration notes.

## Client Libraries

### What this page is about

- It lists community client libraries across multiple languages.
- It also points to the upstream gRPC proto files and the Java gRPC client maintained in the SeaweedFS repository.
- It signals that SeaweedFS does not enforce one canonical application SDK for every language.

### Actionable takeaways

- Treat most language libraries on the page as ecosystem integrations rather than guaranteed first-party SDKs.
- Prefer protocol-level choices first: filer HTTP, S3 API, or internal gRPC, then pick the client library that matches that surface.
- Review the upstream proto definitions in `weed/pb` when you need strongly typed internal integrations or custom code generation.
- Use the repository-hosted Java gRPC client as the closest thing to an upstream-maintained client reference.

### Gotchas / prohibitions

- Do not assume every listed library is current, equally maintained, or feature-complete.
- Do not choose a library purely by language fit without checking whether it targets filer HTTP, raw volume access, S3, or gRPC.

### How to apply in a real repo

- Document approved client paths per language and protocol instead of presenting the entire ecosystem list to operators.
- For critical integrations, prefer direct protocol testing against SeaweedFS endpoints even when a wrapper library is used.

## SeaweedFS Java Client

### What this page is about

- It describes the upstream Java gRPC client extracted from SeaweedFS's Hadoop-compatible file system work.
- It covers build coordinates, direct read/write behavior, replication control, metadata event watching, and basic filesystem operations.
- It positions the Java client as a filer-centric gRPC integration rather than a blob/S3 client.

### Actionable takeaways

- Use the Java client when a JVM application needs efficient filer-backed filesystem semantics rather than S3 compatibility.
- Connect to the filer's gRPC port (`18888` by default when filer HTTP runs on `8888`) instead of the HTTP port.
- Expect data reads and writes to go directly to volume servers while filer handles metadata, which reduces the data-path overhead compared with plain filer HTTP.
- Use the client when recursive metadata event watching is valuable; the page highlights it as stronger than single-directory local file-watch semantics.
- Set replication explicitly on writes when the application, not only the filer default, owns durability decisions.
- Use the standard stream abstractions and filesystem helpers for JVM code that wants normal `InputStream`/`OutputStream` style access.

### Gotchas / prohibitions

- Do not assume this Java client covers blob-storage or S3 APIs; the page says blob storage APIs are not included.
- Do not point the client at the filer HTTP port by mistake; the examples use gRPC.
- Do not rely on example dependency versions blindly; align them with the tracked SeaweedFS release and artifact availability in Maven Central.

### How to apply in a real repo

- Document filer gRPC endpoints separately from HTTP endpoints for JVM teams.
- Reserve the Java client for workloads that benefit from direct volume reads/writes, recursive metadata subscriptions, or stream-like filesystem access.
- Keep S3 integrations and filer gRPC integrations as separate guidance paths so application teams do not mix the abstractions.
