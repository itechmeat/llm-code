# Data Modeling & Inference

Best practices for structuring data in Qdrant and server-side embedding generation.

## What to Store Where

| Component | Purpose | Notes |
|-----------|---------|-------|
| **Vectors** | Similarity search | Dense, sparse, or multi-vector |
| **Payload** | Filtering/metadata | JSON-like, index for performance |
| **External DB** | Full content | Store IDs in payload for retrieval |

## Modeling Best Practices

- Keep payload lightweight; use for filtering, not full data storage
- Index payload fields used in filters (tags, timestamps, tenant IDs)
- Use named vectors for multiple embeddings per point (e.g., text + image)
- Balance vector dimensionality: higher for accuracy, lower for speed/memory

## Multi-Tenancy Patterns

1. **Separate collections**: One collection per tenant (simpler isolation)
2. **Shared collection + tenant ID**: Filter by tenant in payload (requires indexing)

## Common Patterns

| Pattern | Vectors | Payload |
|---------|---------|---------|
| **RAG** | Chunk embeddings | Source doc ID, chunk index |
| **Recommendations** | User/item vectors | Preferences, categories |
| **Hybrid Search** | Dense + sparse | Reranking scores |

---

## Inference (Server-Side Embeddings)

Qdrant can generate embeddings directly, avoiding external pipelines.

### Inference Objects

Replace raw vectors with inference objects in API calls:

```json
// Text embedding
{ "text": "search query", "model": "model-name" }

// Image embedding
{ "image": "https://example.com/image.jpg", "model": "clip-model" }
```

### BM25 Sparse Vectors

```json
{ "text": "document text", "model": "qdrant/bm25" }
```

### Inference Sources

| Source | Setup | Example Model |
|--------|-------|---------------|
| **Qdrant Cloud** | Built-in | Check console for models |
| **Local (fastembed)** | `cloud_inference=False` | Local models |
| **External (OpenAI/Cohere)** | Prepend provider, add API key | `openai/text-embedding-3-small` |

### Advanced Features

- **Multiple vectors**: Generate dense + sparse per point
- **Matryoshka reduction**: `"mrl": 64` for dimension reduction
- **Optimization**: Identical inference objects computed once per request

### Practical Notes

- Input text not stored unless explicitly added to payload
- For Cloud: Check model dimensionality/context window in console
