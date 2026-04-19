# Overview

Zvec is an **in-process** vector database (library-style), intended to run inside your application process rather than as a separate server.

## What Zvec is for

- Similarity search over vectors for semantic search, RAG, and recommendations.
- Embedded / local deployments where a separate vector DB service is undesirable.
- Optionally acting as the “vector search component” alongside an existing system (e.g., SQL DB holding canonical records).

## Key capabilities (as described)

- Dense and sparse vectors.
- Hybrid search (vector similarity + structured filters).
- Multi-vector queries (retrieve with multiple embedding signals).
- Designed for low-latency similarity search.
- Official SDKs for Python and Node.js, plus a stable C API for broader language bindings.
- Official package coverage across Linux, macOS, and Windows.
- Official agent-facing integrations via MCP server and agent skills projects.

## Next reading

- Quickstart: https://zvec.org/en/docs/quickstart/
- Data modeling: https://zvec.org/en/docs/concepts/data-modeling/
- Indexing & quantization: `indexing.md`
- Embedding: https://zvec.org/en/docs/embedding/
- Reranker: https://zvec.org/en/docs/reranker/

## Ecosystem notes

- The upstream project now publishes an official MCP server for collection management, CRUD, vector search, and embedding-driven workflows.
- The upstream project also maintains official agent skills for LLM-assisted Zvec usage.
- Treat these as adjacent tooling around the embedded database, not as a replacement for understanding the core collection/index model.

## Link

- Page: https://zvec.org/en/docs/
