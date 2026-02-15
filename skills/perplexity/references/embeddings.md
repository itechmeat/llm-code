# Embeddings API

Perplexity Embeddings API generates text embeddings for semantic search, RAG, and clustering. Use standard embeddings for independent texts and contextualized embeddings for document chunks that share context.

## Models

- Standard: `pplx-embed-v1-0.6b` (1024 dims), `pplx-embed-v1-4b` (2560 dims)
- Contextualized: `pplx-embed-context-v1-0.6b` (1024 dims), `pplx-embed-context-v1-4b` (2560 dims)

All models use mean pooling and accept up to 32K tokens per input.

## Similarity Rules

- Embeddings are unnormalized. Compare `base64_int8` with cosine similarity.
- Compare `base64_binary` with Hamming distance.

## Standard Embeddings (Independent Texts)

```python
from perplexity import Perplexity

client = Perplexity()
response = client.embeddings.create(
    input=["Query text", "Document text"],
    model="pplx-embed-v1-4b"
)

for item in response.data:
    print(item.index, item.embedding)
```

## Contextualized Embeddings (Document Chunks)

Use contextualized embeddings when chunks belong to the same document and their meaning depends on surrounding context.

```python
from perplexity import Perplexity

client = Perplexity()
response = client.contextualized_embeddings.create(
    input=[
        ["Doc1 chunk 1", "Doc1 chunk 2"],
        ["Doc2 chunk 1", "Doc2 chunk 2"]
    ],
    model="pplx-embed-context-v1-4b"
)

for doc in response.data:
    for chunk in doc.data:
        print(doc.index, chunk.index, chunk.embedding)
```

## Parameters and Limits

- Standard inputs: up to 512 texts per request, 32K tokens per text, 120K tokens total.
- Contextualized inputs: up to 512 documents, 16,000 total chunks, 32K tokens per document, 120K tokens total.
- `encoding_format`: `base64_int8` (default) or `base64_binary`.
- `dimensions`: Matryoshka dimension reduction (range depends on model).

## When to Use Which

- Standard embeddings: queries, short sentences, independent documents.
- Contextualized embeddings: document chunks (paragraphs, PDF sections, code file segments).

## References

- Embeddings Quickstart: https://docs.perplexity.ai/docs/embeddings/quickstart
- Standard Embeddings: https://docs.perplexity.ai/docs/embeddings/standard-embeddings
- Contextualized Embeddings: https://docs.perplexity.ai/docs/embeddings/contextualized-embeddings
