# Reranker (AI Extension)

Reranking is a second-stage step that re-orders retrieved candidates to improve relevance.

## When to use

- You want higher precision after a fast ANN retrieval stage.
- You combine multiple retrieval methods (dense + sparse) and need to fuse result lists.

## Built-in rerankers mentioned

- **DefaultLocalReRanker**: local cross-encoder model (`cross-encoder/ms-marco-MiniLM-L6-v2`, ~80MB).
- **QwenReRanker**: Dashscope API reranker (requires API key; subject to rate limits).
- **RrfReRanker**: Reciprocal Rank Fusion for **multi-result-list** fusion; uses ranks/positions (scores not required).
- **WeightedReRanker**: weighted fusion for **scored** multi-result-list retrieval.

## Pipeline patterns

- **Two-stage retrieval**:
  1. fast recall (vector search) → 2) rerank top-N for precision
- **Multi-vector fusion**:
  - Use RRF/Weighted when you have multiple retrieval lists (e.g., dense and sparse).
  - For single-vector retrieval results, prefer DefaultLocalReRanker or QwenReRanker.

## Operational notes

- Local rerankers download models on first use.
- Local models consume memory; call `clear_cache()` when appropriate.
- API rerankers are constrained by quotas/rate limits.
- Docs state reranking functions are thread-safe.

## Extending / custom rerankers

- Custom rerankers inherit from `RerankFunction` (exported as `ReRanker`).
- Docs mention building on base classes such as `QwenFunctionBase`.

## Links

- Docs: https://zvec.org/en/docs/reranker/
- Python API reference (ReRanker protocol): https://zvec.org/api-reference/python/extension/#zvec.extension.ReRanker
