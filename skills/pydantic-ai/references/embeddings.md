# Embeddings Reference

Generate vector embeddings for semantic search, RAG, and similarity detection.

## Quick Start

```python
from pydantic_ai import Embedder

embedder = Embedder('openai:text-embedding-3-small')

async def main():
    # Embed a search query
    result = await embedder.embed_query('What is machine learning?')
    print(f'Dimensions: {len(result.embeddings[0])}')

    # Embed multiple documents
    docs = ['ML is AI subset.', 'Deep learning uses neural nets.']
    result = await embedder.embed_documents(docs)
    print(f'Embedded {len(result.embeddings)} documents')
```

## Providers

| Provider              | Install Group           | Model Example                            |
| --------------------- | ----------------------- | ---------------------------------------- |
| OpenAI                | `openai`                | `openai:text-embedding-3-small`          |
| Google                | `google`                | `google-gla:gemini-embedding-001`        |
| Cohere                | `cohere`                | `cohere:embed-v4.0`                      |
| VoyageAI              | `voyageai`              | `voyageai:voyage-3.5`                    |
| Bedrock               | `bedrock`               | `bedrock:amazon.titan-embed-text-v1`     |
| Sentence Transformers | `sentence-transformers` | `sentence-transformers:all-MiniLM-L6-v2` |

### OpenAI

```bash
pip install "pydantic-ai-slim[openai]"
export OPENAI_API_KEY='your-key'
```

```python
from pydantic_ai import Embedder

embedder = Embedder('openai:text-embedding-3-small')
result = await embedder.embed_query('Hello world')
# 1536 dimensions
```

### Google

```bash
pip install "pydantic-ai-slim[google]"
export GOOGLE_API_KEY='your-key'
```

```python
from pydantic_ai import Embedder

# Gemini API
embedder = Embedder('google-gla:gemini-embedding-001')

# Vertex AI
embedder = Embedder('google-vertex:gemini-embedding-001')
```

### Cohere

```bash
pip install "pydantic-ai-slim[cohere]"
export CO_API_KEY='your-key'
```

```python
from pydantic_ai import Embedder

embedder = Embedder('cohere:embed-v4.0')
```

### VoyageAI

Optimized for retrieval with specialized models for code, finance, legal.

```bash
pip install "pydantic-ai-slim[voyageai]"
export VOYAGE_API_KEY='your-key'
```

```python
from pydantic_ai import Embedder

embedder = Embedder('voyageai:voyage-3.5')
```

### Bedrock (AWS)

AWS Bedrock embeddings for Nova, Cohere, and Titan models.

```bash
pip install "pydantic-ai-slim[bedrock]"
# Uses AWS credentials from environment or ~/.aws/credentials
```

```python
from pydantic_ai import Embedder

# Amazon Titan
embedder = Embedder('bedrock:amazon.titan-embed-text-v1')

# Cohere via Bedrock
embedder = Embedder('bedrock:cohere.embed-english-v3')
```

### Sentence Transformers (Local)

Run embeddings locally without API calls.

```bash
pip install "pydantic-ai-slim[sentence-transformers]"
```

```python
from pydantic_ai import Embedder

# Downloaded from Hugging Face on first use
embedder = Embedder('sentence-transformers:all-MiniLM-L6-v2')
```

## Embedding Result

```python
result = await embedder.embed_query('Hello world')

# Access embeddings
embedding = result.embeddings[0]  # By index
embedding = result[0]  # Shorthand
embedding = result['Hello world']  # By input text

# Usage info
print(result.usage.input_tokens)

# Cost calculation (requires genai-prices)
cost = result.cost()
print(f'Cost: ${cost.total_price:.6f}')
```

## Settings

```python
from pydantic_ai import Embedder
from pydantic_ai.embeddings import EmbeddingSettings

# Reduce dimensions (OpenAI, Google, Cohere, VoyageAI)
embedder = Embedder(
    'openai:text-embedding-3-small',
    settings=EmbeddingSettings(dimensions=256),
)

# Per-call override
result = await embedder.embed_query(
    'Hello world',
    settings=EmbeddingSettings(dimensions=512),
)
```

### Provider-Specific Settings

**Google:**

```python
from pydantic_ai.embeddings.google import GoogleEmbeddingSettings

embedder = Embedder(
    'google-gla:gemini-embedding-001',
    settings=GoogleEmbeddingSettings(
        dimensions=768,
        google_task_type='SEMANTIC_SIMILARITY',
    ),
)
```

**Cohere:**

```python
from pydantic_ai.embeddings.cohere import CohereEmbeddingSettings

embedder = Embedder(
    'cohere:embed-v4.0',
    settings=CohereEmbeddingSettings(
        dimensions=512,
        cohere_truncate='END',
        cohere_max_tokens=256,
    ),
)
```

**VoyageAI:**

```python
from pydantic_ai.embeddings.voyageai import VoyageAIEmbeddingSettings

embedder = Embedder(
    'voyageai:voyage-3.5',
    settings=VoyageAIEmbeddingSettings(
        dimensions=512,
        voyageai_input_type='document',
    ),
)
```

**Sentence Transformers:**

```python
from pydantic_ai.embeddings.sentence_transformers import (
    SentenceTransformersEmbeddingSettings,
)

embedder = Embedder(
    'sentence-transformers:all-MiniLM-L6-v2',
    settings=SentenceTransformersEmbeddingSettings(
        sentence_transformers_device='cuda',
        sentence_transformers_normalize_embeddings=True,
    ),
)
```

## Token Counting

```python
embedder = Embedder('openai:text-embedding-3-small')

# Count tokens
token_count = await embedder.count_tokens('Hello world, this is a test.')
print(f'Tokens: {token_count}')

# Check max input
max_tokens = await embedder.max_input_tokens()
print(f'Max: {max_tokens}')
```

## Query vs Documents

Use appropriate method based on input type:

- `embed_query()` — for search queries
- `embed_documents()` — for content being indexed

Some models optimize differently for queries vs documents.

## Testing

```python
from pydantic_ai import Embedder
from pydantic_ai.embeddings import TestEmbeddingModel

async def test_rag():
    embedder = Embedder('openai:text-embedding-3-small')
    test_model = TestEmbeddingModel()

    with embedder.override(model=test_model):
        result = await embedder.embed_query('test')
        # Returns deterministic [1.0] * 8
        assert result.embeddings[0] == [1.0] * 8
```

## Instrumentation

```python
import logfire
from pydantic_ai import Embedder

logfire.configure()

# Instrument specific embedder
embedder = Embedder('openai:text-embedding-3-small', instrument=True)

# Or instrument all globally
Embedder.instrument_all()
```

## OpenAI-Compatible Providers

```python
from pydantic_ai import Embedder
from pydantic_ai.embeddings.openai import OpenAIEmbeddingModel
from pydantic_ai.providers.openai import OpenAIProvider

# Azure OpenAI
from openai import AsyncAzureOpenAI

azure_client = AsyncAzureOpenAI(
    azure_endpoint='https://your-resource.openai.azure.com',
    api_version='2024-02-01',
    api_key='your-azure-key',
)
model = OpenAIEmbeddingModel(
    'text-embedding-3-small',
    provider=OpenAIProvider(openai_client=azure_client),
)
embedder = Embedder(model)

# Any OpenAI-compatible API
model = OpenAIEmbeddingModel(
    'your-model-name',
    provider=OpenAIProvider(
        base_url='https://your-provider.com/v1',
        api_key='your-api-key',
    ),
)
embedder = Embedder(model)

# Shorthand for known providers
embedder = Embedder('azure:text-embedding-3-small')
embedder = Embedder('ollama:nomic-embed-text')
```

## Custom Embedding Model

```python
from collections.abc import Sequence
from pydantic_ai.embeddings import EmbeddingModel, EmbeddingResult, EmbeddingSettings
from pydantic_ai.embeddings.result import EmbedInputType

class MyEmbeddingModel(EmbeddingModel):
    @property
    def model_name(self) -> str:
        return 'my-model'

    @property
    def system(self) -> str:
        return 'my-provider'

    async def embed(
        self,
        inputs: str | Sequence[str],
        *,
        input_type: EmbedInputType,
        settings: EmbeddingSettings | None = None,
    ) -> EmbeddingResult:
        inputs, settings = self.prepare_embed(inputs, settings)

        # Call your API here
        embeddings = [[0.1, 0.2, 0.3] for _ in inputs]

        return EmbeddingResult(
            embeddings=embeddings,
            inputs=inputs,
            input_type=input_type,
            model_name=self.model_name,
            provider_name=self.system,
        )
```
