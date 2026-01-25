# Qdrant Quickstart — overview (ingested: local quickstart)

Source: https://qdrant.tech/documentation/quickstart/

This note summarizes the **Local Quickstart** page. The goal is not to mirror code samples, but to capture the practical workflow and gotchas.

## High-value warning (repeatable)

- Quickstart explicitly warns: by default Qdrant can start **without encryption or authentication**.
- Practical rule: treat a default quickstart instance as **local-only** unless you’ve applied the Security guidance (API keys + TLS + network isolation).

## Minimal local run (what matters)

- Run Qdrant in Docker with:
  - REST endpoint (HTTP)
  - gRPC endpoint
  - persistent storage mounted to `/qdrant/storage`

The quickstart calls out that on some platforms (notably Windows setups) a named Docker volume may be safer than host folder mounts.

## Local endpoints you can rely on

- REST API is available on the HTTP port.
- Web UI dashboard is served on the same HTTP endpoint under `/dashboard`.
- gRPC API is exposed on its own port.

## Minimal sanity-check workflow (portable)

1) Create a collection
- Requires specifying vector dimensionality and a distance function.

2) Upsert points
- Points include an ID, vector values, and optional payload.

3) Query / search
- Basic similarity query returns scored point IDs.
- Payload is not always returned by default; request it explicitly if you need it.

4) Filtered search
- Filtering is applied over payload fields.
- Quickstart recommends: create payload indexes for performance on real datasets.

## Next ingestion targets (one URL at a time)

- Payload indexing page (to capture what “payload index” means and how to design it)
- Filtering page (operators, types, and performance implications)
