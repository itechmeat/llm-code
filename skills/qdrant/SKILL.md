---
name: qdrant
description: "Qdrant vector database: collections, points, payload filtering, indexing, quantization, snapshots, and Docker/Kubernetes deployment. Use when managing Qdrant collections, performing vector searches with payload filters, configuring HNSW indexes or quantization, or deploying Qdrant clusters. Keywords: Qdrant, vector database, HNSW, quantization, semantic search."
metadata:
  version: "1.19.2"
  release_date: "2026-10-05"
---

# Qdrant (Skill Router)

This file is intentionally **introductory**.

It acts as a **router**: based on your situation, open the right note under `references/`.

## Release Highlights (1.19.0 → 1.19.2)

- **TurboQuant 4-bit as primary storage:** the `"turbo4"` datatype stores only 4-bit quantized vectors, sparing disk space on originals.
- **Per-component memory strategy:** collection components now take `"memory": "cold" / "cached" / "pinned"` for fine-grained control over memory vs performance. Deprecates `max_resident_memory_percent` of strict mode in favor of the new global quota API.
- **Keyword prefix match:** `{"match": {"prefix": "..."}}` in filters matches keywords by prefix; must be enabled in the keyword index.
- **Sparse search:** per-query IDF corpus for better per-tenant/sparse ranking.
- **Slice filtering:** sliced scroll / deterministic sampling via a slice filter condition.
- **Global quota API:** central place to cap cluster resource usage (supersedes the strict-mode memory ceiling).
- **Routing token:** deterministic read routes when the read affinity option is in use.
- **1.19.1:** 4-bit TurboQuant SIMD rework and batched HNSW searches (faster scoring), quantized scoring prefetch, plus input hardening — rejects empty dense vectors, vectors larger than 65536, and `.`/`..` in collection names (security).
- **1.19.2 snapshot storage:** collection snapshots can now be written to **GCS** or **Azure Blob Storage** next to S3, and every object-storage backend accepts an optional key `prefix` — see `references/snapshots.md`.
- **1.19.2 network boundary:** the internal (p2p) gRPC listener can bind to its own interface (`cluster.p2p.host`), and a distributed node now warns at startup when it runs without API keys — see `references/security.md` and `references/deployment.md`.
- **1.19.2 performance:** sparse upserts no longer rewrite the whole posting list, proxy segments persist their state (no WAL pinning, fast restarts), filter IDs resolve once per request, HNSW builds saturate all assigned threads, and blocking work (queue-proxy encoding, WAL reads, BM25 embedding) moved off the async runtime.
- **1.19.2 correctness:** filtered search no longer returns zero results when the HNSW entry point fails the filter, adding a named multivector to an indexed collection no longer breaks search, proxy segments propagate named-vector and payload-index changes, and write tearing is prevented in all Gridstore storages.

## Release Highlights (1.16.3 → 1.18.0)

- **Monitoring + ops:** new APIs for optimization progress/stages and cluster-wide telemetry, plus a dedicated HTTP port option for `/metrics`.
- **Security:** audit access logging and secondary API key support (rotation).
- **Retrieval:** relevance feedback and Weighted RRF for hybrid ranking.
- **Write semantics:** `update_mode` for upserts (`upsert` / `update` / `insert`).
- **1.18.0:** TurboQuant adds an aggressive vector-compression path, collections can add/delete named vectors in place, and operators get low-memory/strict-memory knobs plus deeper memory reporting.

## Patch Notes (1.18.1 → 1.18.2)

- **1.18.2 security:** fixes a REST auth whitelist bypass on specially crafted paths and a heap-read vulnerability with malformed snapshots. Upgrade promptly if Qdrant is exposed with auth/whitelisting or accepts uploaded snapshots.
- **1.18.2:** logs slow operations during shard WAL recovery and clears the ID-tracker cache after building segments.
- Filter behavior is corrected for indexed integer range filters that receive float values and for `{match: {except: []}}` on payload-indexed fields.
- Empty vector requests no longer trigger a panic path; treat them as invalid input and validate caller-side before sending them to Qdrant.
- TurboQuant heap-memory reporting is more accurate, so operators should trust current metrics over older baselines when checking compression impact.
- Snapshot upload authorization is tightened; do not assume restore/upload endpoints are safe without the same auth review you apply to the main API surface.

## Breaking / Upgrade Notes (1.17.0)

- **gRPC clients:** response format for vector fields changed in gRPC. Upgrade official Qdrant client libraries and validate any custom gRPC integrations.
- **Storage upgrades:** RocksDB is removed in favor of gridstore. If you are on v1.15.x, do not upgrade directly to v1.17.x — upgrade one minor version at a time.

## Additional Upgrade Notes (1.18.0)

- Internal gRPC endpoints now enforce API key/JWT authentication when auth is enabled; validate internal service-to-service traffic before upgrade if you previously relied on private-network-only trust.
- Snapshot restore from URL can now be disabled by config, which is relevant for hardened/self-hosted environments.

## Additional Upgrade Notes (1.19.2)

- The internal (p2p) gRPC API accepts **read-write keys only** (`service.api_key` / `service.alt_api_key`); a read-only key or a JWT is rejected there. Keep `service.enforce_internal_auth` off during a rolling upgrade and enable it only once every node is on 1.19.2+.
- No API surface changed; the release is additive apart from the internal-key rule above. Still re-run filtered-search and multivector tests, because the filter/multivector fixes change result sets that were previously wrong.

## Start here (fast)

- New to Qdrant? Read: `references/concepts.md`.
- Creating and configuring collections? Read: `references/collections.md`.
- Want the fastest local validation? Read: `references/quickstart.md` + `references/deployment.md`.
- Integrating with Python? Read: `references/api-clients.md`.

## Choose by situation

### Data modeling

- What should go into vectors vs payload vs your main DB? Read: `references/modeling.md`.
- Working with IDs, upserts, and write semantics? Read: `references/points.md`.
- Need to understand payload types and update modes? Read: `references/payload.md`.

### Retrieval (search)

- One consolidated entry point (search + filtering + explore + hybrid): `references/retrieval.md`.

### Performance & indexing

- Index types and tradeoffs: `references/indexing.md`.
- Storage/optimizer internals that matter operationally: `references/storage.md` + `references/optimizer.md`.
- Practical tuning, monitoring, troubleshooting: `references/ops-checklist.md`.

### Deployment & ops

- Installation/Docker/Kubernetes: `references/deployment.md`.
- Configuration layering: `references/configuration.md`.
- Security/auth/TLS boundary: `references/security.md`.
- Backup/restore: `references/snapshots.md`.

### API interface choice

- REST vs gRPC, Python SDK: `references/api-clients.md`.

## How to maintain this skill

- Keep `SKILL.md` short (router + usage guidance).
- Put details into `references/*.md`.
- Merge or reorganize references when it improves discoverability.

## Critical prohibitions

- Do not ingest/quote large verbatim chunks of vendor docs; summarize in your own words.
- Do not invent defaults not explicitly grounded in documentation; record uncertainties as TODOs.
- Do not design backup/restore without testing a restore path.
- Do not use NFS as the primary persistence backend (installation docs explicitly warn against it).
- Do not expose internal cluster communication ports publicly; rely on private networking.
- Do not use API keys/JWT over untrusted networks without TLS.
- Do not rely on implicit runtime defaults for production; record effective configuration.

## Links

- [Documentation](https://qdrant.tech/documentation/)
- [Releases](https://github.com/qdrant/qdrant/releases)
- [GitHub](https://github.com/qdrant/qdrant)
