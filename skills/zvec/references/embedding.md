# Embedding (AI Extension)

Zvec provides embedding functions to convert text into vectors for similarity search. It ships built-in implementations and supports custom embedding function integrations.

## Scope / current limitations

- Current support is **text modality only**.

## Built-in embedding function options

### Dense embeddings

- **Local dense** (`DefaultLocalDenseEmbedding`): Sentence Transformers-based.
  - Uses `all-MiniLM-L6-v2` by default (384 dimensions) and downloads the model on first use.
- **Qwen dense** (`QwenDenseEmbedding`): Dashscope API (requires API key; dimension must be set explicitly).
- **OpenAI dense** (`OpenAIDenseEmbedding`): OpenAI API (requires API key; follow provider limits).
- **Jina dense** (`JinaDenseEmbedding`): Jina Embeddings API (requires API key). Supports Jina Embeddings v5.
  - Docs mention task-specific embeddings and Matryoshka-style dimension reduction support.

### Custom HTTP embeddings

- **Custom HTTP** (`CustomHTTPEmbedding`): call any OpenAI-compatible embedding endpoint (LM Studio, Ollama, self-hosted models). Configure `base_url`, `model`, and optional `api_key`.

### Sparse embeddings

- **Local sparse** (`DefaultLocalSparseEmbedding`): SPLADE-based, outputs a sparse dictionary.
- **BM25** (`BM25EmbeddingFunction`): local BM25 encoder (no API key).
  - Built-in encoder option supports at least English/Chinese.
  - Custom encoder option can be trained on your corpus and uses BM25 parameters (e.g., `b`, `k1`).
- **Qwen sparse** (`QwenSparseEmbedding`): Dashscope API (requires API key).

## Choosing an approach

- Prefer **local** functions when you want offline/embedded behavior and predictable costs.
- Prefer **API-based** functions when you want managed model serving and can accept network + quota constraints.
- Consider **hybrid retrieval** (dense + sparse) when you need stronger relevance across both semantic and lexical signals.

## Operational notes

- **Model download**: local models are downloaded on first use; ensure network access.
- **Memory**: local models consume RAM; call `clear_cache()` to release model memory when appropriate.
- **Rate limits**: API providers can throttle; plan retries/backoff in your app.
- **Thread safety**: docs state embedding functions are thread-safe.

## Extending / custom embedding functions

Docs mention protocol base classes:

- `DenseEmbeddingFunction[T]`
- `SparseEmbeddingFunction[T]`

And framework-oriented base classes:

- `SentenceTransformerFunctionBase`
- `QwenFunctionBase`

## Links

- Docs: https://zvec.org/en/docs/embedding/
- Python API reference (extension protocols):
  - DenseEmbeddingFunction: https://zvec.org/api-reference/python/extension/#zvec.extension.DenseEmbeddingFunction
  - SparseEmbeddingFunction: https://zvec.org/api-reference/python/extension/#zvec.extension.SparseEmbeddingFunction
