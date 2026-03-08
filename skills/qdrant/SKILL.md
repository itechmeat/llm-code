---
name: qdrant
description: "Qdrant vector database: collections, points, payload filtering, indexing, quantization, snapshots, and Docker/Kubernetes deployment. Use when managing Qdrant collections, performing vector searches with payload filters, configuring HNSW indexes or quantization, or deploying Qdrant clusters. Keywords: Qdrant, vector database, HNSW, quantization, semantic search."
metadata:
  version: "1.17.0"
  release_date: "2026-02-20"
---

# Qdrant (Skill Router)

This file is intentionally **introductory**.

It acts as a **router**: based on your situation, open the right note under `references/`.

## Release Highlights (1.16.3 → 1.17.0)

- **Monitoring + ops:** new APIs for optimization progress/stages and cluster-wide telemetry, plus a dedicated HTTP port option for `/metrics`.
- **Security:** audit access logging and secondary API key support (rotation).
- **Retrieval:** relevance feedback and Weighted RRF for hybrid ranking.
- **Write semantics:** `update_mode` for upserts (`upsert` / `update` / `insert`).

## Breaking / Upgrade Notes (1.17.0)

- **gRPC clients:** response format for vector fields changed in gRPC. Upgrade official Qdrant client libraries and validate any custom gRPC integrations.
- **Storage upgrades:** RocksDB is removed in favor of gridstore. If you are on v1.15.x, do not upgrade directly to v1.17.x — upgrade one minor version at a time.

## Start here (fast)

- New to Qdrant? Read: `references/concepts.md`.
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
