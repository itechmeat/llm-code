# Models Reference

Pydantic AI is model-agnostic with 30+ providers.

## Built-in Providers

| Provider     | Model Class                            | Example                            |
| ------------ | -------------------------------------- | ---------------------------------- |
| OpenAI       | `OpenAIChatModel`                      | `openai:gpt-4o`                    |
| Anthropic    | `AnthropicModel`                       | `anthropic:claude-sonnet-4-5`      |
| Google       | `GoogleModel`                          | `google-gla:gemini-2.5-flash`      |
| Vertex AI    | `GoogleModel` + `GoogleVertexProvider` | `vertexai:gemini-pro`              |
| xAI          | `XaiModel`                             | `xai:grok-4-1-fast-non-reasoning`  |
| Groq         | `GroqModel`                            | `groq:llama-3.3-70b`               |
| Mistral      | `MistralModel`                         | `mistral:mistral-large`            |
| Bedrock      | `BedrockModel`                         | `bedrock:anthropic.claude-v2`      |
| Cohere       | `CohereModel`                          | `cohere:command-r-plus`            |
| OpenRouter   | `OpenRouterModel`                      | `openrouter:google/gemini-2.5-pro` |
| SambaNova    | `SambaNovaModel`                       | `sambanova:...`                    |
| Hugging Face | `HuggingFaceModel`                     | `huggingface:meta-llama/...`       |

## xAI (Grok)

Native xAI SDK provider (replaces deprecated `GrokProvider`):

```bash
pip install "pydantic-ai-slim[xai]"
export XAI_API_KEY='your-api-key'
```

```python
from pydantic_ai import Agent

# Via model string
agent = Agent('xai:grok-4-1-fast-non-reasoning')

# Explicit model
from pydantic_ai.models.xai import XaiModel
model = XaiModel('grok-4-1-fast-non-reasoning')
agent = Agent(model)

# Custom provider
from pydantic_ai.providers.xai import XaiProvider
provider = XaiProvider(api_key='your-api-key')
model = XaiModel('grok-4-1-fast-non-reasoning', provider=provider)

# With xai_sdk client
from xai_sdk import AsyncClient
xai_client = AsyncClient(api_key='your-api-key')
provider = XaiProvider(xai_client=xai_client)
model = XaiModel('grok-4-1-fast-non-reasoning', provider=provider)
```

## OpenAI-Compatible Providers

Use `OpenAIChatModel` with custom provider:

- Azure AI, DeepSeek, Fireworks AI
- GitHub Models, Heroku
- LiteLLM, Ollama, Perplexity
- Together AI, Vercel AI Gateway

## Model Identifiers

Format: `<provider>:<model>`

```python
from pydantic_ai import Agent

# Simple string identifier
agent = Agent('openai:gpt-4o')
agent = Agent('anthropic:claude-sonnet-4-5')
agent = Agent('google-gla:gemini-2.5-flash')
agent = Agent('xai:grok-4-1-fast-non-reasoning')

# Gateway prefix (if using AI gateway)
agent = Agent('gateway/openai:gpt-5')
```

## Explicit Model Configuration

```python
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel

# With custom configuration
model = OpenAIChatModel(
    'gpt-4o',
    api_key='sk-...',
    base_url='https://custom.endpoint.com',
)

agent = Agent(model)
```

## Custom Providers

```python
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# Azure example
provider = OpenAIProvider(
    api_key='azure-key',
    base_url='https://your-resource.openai.azure.com',
)
model = OpenAIChatModel('gpt-4o', provider=provider)
```

## Ollama (Local Models)

```python
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

provider = OpenAIProvider(base_url='http://localhost:11434/v1')
model = OpenAIChatModel('llama3.2', provider=provider)

agent = Agent(model)
```

## Fallback Models

Automatic failover between providers:

```python
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel

openai = OpenAIChatModel('gpt-4o')
anthropic = AnthropicModel('claude-sonnet-4-5')

fallback = FallbackModel(openai, anthropic)
agent = Agent(fallback)
```

### Per-Model Settings

```python
from pydantic_ai import ModelSettings

openai = OpenAIChatModel(
    'gpt-4o',
    settings=ModelSettings(temperature=0.7)
)
anthropic = AnthropicModel(
    'claude-sonnet-4-5',
    settings=ModelSettings(temperature=0.2)
)

fallback = FallbackModel(openai, anthropic)
```

### Exception Handling

```python
from pydantic_ai import ModelAPIError

try:
    result = agent.run_sync('Query')
except* ModelAPIError as exc_group:
    for exc in exc_group.exceptions:
        print(f"Model failed: {exc}")
```

## Key Concepts

| Term         | Description                           |
| ------------ | ------------------------------------- |
| **Model**    | Pydantic AI class wrapping vendor SDK |
| **Provider** | Authentication/connection handler     |
| **Profile**  | Request format for model family       |

## Testing Models

```python
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel

# Deterministic testing
test_model = TestModel()
agent = Agent(model=test_model)

# Custom function model
def my_model(messages, info):
    return ModelResponse(parts=[TextPart('test')])

agent = Agent(model=FunctionModel(my_model))
```

---

## HTTP Request Retries

Built on tenacity library with httpx transport integration.

### Installation

```bash
pip install 'pydantic-ai-slim[retries]'
```

### Basic Setup

```python
from httpx import AsyncClient, HTTPStatusError
from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.retries import AsyncTenacityTransport, RetryConfig, wait_retry_after

def create_retrying_client():
    def should_retry_status(response):
        if response.status_code in (429, 502, 503, 504):
            response.raise_for_status()

    transport = AsyncTenacityTransport(
        config=RetryConfig(
            retry=retry_if_exception_type((HTTPStatusError, ConnectionError)),
            wait=wait_retry_after(
                fallback_strategy=wait_exponential(multiplier=1, max=60),
                max_wait=300
            ),
            stop=stop_after_attempt(5),
            reraise=True
        ),
        validate_response=should_retry_status
    )
    return AsyncClient(transport=transport)

client = create_retrying_client()
model = OpenAIChatModel('gpt-4o', provider=OpenAIProvider(http_client=client))
agent = Agent(model)
```

### Key Components

| Component                | Purpose                                   |
| ------------------------ | ----------------------------------------- |
| `AsyncTenacityTransport` | Async HTTP transport with retries         |
| `TenacityTransport`      | Sync HTTP transport with retries          |
| `RetryConfig`            | Configuration for retry behavior          |
| `wait_retry_after`       | Smart wait respecting Retry-After headers |

### wait_retry_after

Respects HTTP `Retry-After` headers automatically:

```python
from tenacity import wait_exponential
from pydantic_ai.retries import wait_retry_after

wait_strategy = wait_retry_after(
    fallback_strategy=wait_exponential(multiplier=2, max=120),
    max_wait=600  # Max 10 minutes
)
```

### Common Patterns

**Rate Limit Handling:**

```python
transport = AsyncTenacityTransport(
    config=RetryConfig(
        retry=retry_if_exception_type(HTTPStatusError),
        wait=wait_retry_after(fallback_strategy=wait_exponential(multiplier=1, max=60)),
        stop=stop_after_attempt(10),
        reraise=True
    ),
    validate_response=lambda r: r.raise_for_status()
)
```

**Network Errors:**

```python
import httpx

transport = AsyncTenacityTransport(
    config=RetryConfig(
        retry=retry_if_exception_type((
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.ReadError
        )),
        wait=wait_exponential(multiplier=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
)
```

### AWS Bedrock Retries

Use boto3's built-in retry:

```python
from botocore.config import Config

config = Config(retries={'max_attempts': 5, 'mode': 'adaptive'})
```

### Best Practices

- Start conservative: 3-5 retries, reasonable waits
- Use exponential backoff
- Set maximum wait times
- Respect `Retry-After` headers
- Monitor retry rates in production
- Disable HTTP retries when using Temporal (use Temporal's retry policy)

---

## OpenAI Provider Details

### Configuration

```python
# Environment variable (preferred)
export OPENAI_API_KEY='your-api-key'

# By name
agent = Agent('openai:gpt-4o')

# Explicit provider
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel('gpt-4o', provider=OpenAIProvider(api_key='your-api-key'))
```

### Custom Client

```python
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncOpenAI(max_retries=3)
model = OpenAIChatModel('gpt-4o', provider=OpenAIProvider(openai_client=client))
```

### Azure OpenAI

```python
from openai import AsyncAzureOpenAI

client = AsyncAzureOpenAI(
    azure_endpoint='...',
    api_version='2024-07-01-preview',
    api_key='your-api-key',
)
model = OpenAIChatModel('gpt-4o', provider=OpenAIProvider(openai_client=client))
```

### OpenAI Responses API

```python
# By name
agent = Agent('openai-responses:gpt-4o')

# Explicit
from pydantic_ai.models.openai import OpenAIResponsesModel
model = OpenAIResponsesModel('gpt-4o')
```

**Built-in Tools** (via Responses API):

- Web search
- Code interpreter
- Image generation
- File search
- Computer use

```python
from openai.types.responses import ComputerToolParam
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model_settings = OpenAIResponsesModelSettings(
    openai_builtin_tools=[ComputerToolParam(type='computer_use')]
)
```

### Previous Response ID (Context Continuity)

```python
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

# Manual
result = agent.run_sync('Secret is 1234')
model_settings = OpenAIResponsesModelSettings(
    openai_previous_response_id=result.all_messages()[-1].provider_response_id
)
result = agent.run_sync('What is the secret?', model_settings=model_settings)

# Auto (recommended)
model_settings = OpenAIResponsesModelSettings(openai_previous_response_id='auto')
result2 = agent.run_sync('Explain?', message_history=result1.new_messages(), model_settings=model_settings)
```

### OpenAI-Compatible Providers

```python
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel(
    'model_name',
    provider=OpenAIProvider(base_url='https://custom-api.com', api_key='...')
)
```

### Model Profile (Custom Schema Handling)

```python
from pydantic_ai.profiles.openai import OpenAIModelProfile

model = OpenAIChatModel(
    'model_name',
    provider=OpenAIProvider(base_url='https://custom-api.com', api_key='...'),
    profile=OpenAIModelProfile(openai_supports_strict_tool_definition=False)
)
```

---

## Anthropic Provider Details

### Configuration

```python
# Environment variable
export ANTHROPIC_API_KEY='your-api-key'

# By name
agent = Agent('anthropic:claude-sonnet-4-5')

# Explicit provider
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

model = AnthropicModel('claude-sonnet-4-5', provider=AnthropicProvider(api_key='...'))
```

### Cloud Platform Integrations

**AWS Bedrock:**

```python
from anthropic import AsyncAnthropicBedrock
from pydantic_ai.providers.anthropic import AnthropicProvider

bedrock_client = AsyncAnthropicBedrock()  # Uses AWS env credentials
provider = AnthropicProvider(anthropic_client=bedrock_client)
model = AnthropicModel('us.anthropic.claude-sonnet-4-5-20250929-v1:0', provider=provider)
```

**Google Vertex AI:**

```python
from anthropic import AsyncAnthropicVertex

vertex_client = AsyncAnthropicVertex(region='us-east5', project_id='your-project-id')
provider = AnthropicProvider(anthropic_client=vertex_client)
model = AnthropicModel('claude-sonnet-4-5', provider=provider)
```

**Microsoft Foundry:**

```python
from anthropic import AsyncAnthropicFoundry

foundry_client = AsyncAnthropicFoundry(
    api_key='your-foundry-api-key',
    resource='your-resource-name',
)
provider = AnthropicProvider(anthropic_client=foundry_client)
```

### Prompt Caching

Anthropic supports prompt caching to reduce costs. **Maximum 4 cache points per request.**

**Cache Methods:**

1. `anthropic_cache_instructions=True` — cache system prompt (5m or 1h TTL)
2. `anthropic_cache_tool_definitions=True` — cache tool definitions
3. `anthropic_cache_messages=True` — cache all messages automatically
4. `CachePoint()` — manual cache point marker

```python
from pydantic_ai import Agent, CachePoint
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-4-5',
    system_prompt='Detailed instructions...',
    model_settings=AnthropicModelSettings(
        anthropic_cache_instructions=True,      # 1 cache point
        anthropic_cache_tool_definitions='1h',  # 1 cache point with 1h TTL
        anthropic_cache_messages=True,          # 1 cache point
    ),
)

# Manual cache point
result = agent.run_sync([
    'Long context from documentation...',
    CachePoint(),  # Cache everything up to this point
    'Question'
])

# Check cache usage
usage = result.usage()
print(f'Cache write: {usage.cache_write_tokens}')
print(f'Cache read: {usage.cache_read_tokens}')
```

**Note:** When using `AsyncAnthropicBedrock`, TTL is automatically omitted (Bedrock doesn't support explicit TTL).

---

## Google Provider Details

### Configuration

```python
# Generative Language API
export GOOGLE_API_KEY='your-api-key'

# By name (GLA = Generative Language API)
agent = Agent('google-gla:gemini-2.5-pro')

# Vertex AI
agent = Agent('google-vertex:gemini-2.5-pro')
```

### Vertex AI Authentication

```python
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

# Application Default Credentials (recommended in GCP)
provider = GoogleProvider(vertexai=True)

# Service Account
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(
    'path/to/service-account.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform'],
)
provider = GoogleProvider(credentials=credentials, project='your-project-id')

# Custom location/project
provider = GoogleProvider(vertexai=True, location='asia-east1', project='your-gcp-project-id')
```

### Model Garden (Non-Gemini Models)

```python
# Access Llama, etc. from Model Garden
provider = GoogleProvider(project='your-project-id', location='us-central1')
model = GoogleModel('meta/llama-3.3-70b-instruct-maas', provider=provider)
```

### YouTube & File Upload

```python
from pydantic_ai import Agent, VideoUrl, DocumentUrl
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

# YouTube URLs directly
agent = Agent(GoogleModel('gemini-2.5-flash'))
result = agent.run_sync([
    'What is this video about?',
    VideoUrl(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
])

# File upload via Files API
provider = GoogleProvider()
file = provider.client.files.upload(file='document.pdf')
result = agent.run_sync([
    'Summarize this document',
    DocumentUrl(url=file.uri, media_type=file.mime_type),
])
```

### Model Settings

```python
from google.genai.types import HarmBlockThreshold, HarmCategory
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

settings = GoogleModelSettings(
    temperature=0.2,
    max_tokens=1024,
    google_thinking_config={'thinking_level': 'low'},  # or 'thinking_budget': 0 to disable
    google_safety_settings=[{
        'category': HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        'threshold': HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }]
)
```

---

## Groq Provider Details

Fast inference on open-source models.

```python
# Environment variable
export GROQ_API_KEY='your-api-key'

# By name
agent = Agent('groq:llama-3.3-70b-versatile')

# Explicit provider
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

model = GroqModel('llama-3.3-70b-versatile', provider=GroqProvider(api_key='...'))
```

---

## Mistral Provider Details

```python
# Environment variable
export MISTRAL_API_KEY='your-api-key'

# By name
agent = Agent('mistral:mistral-large-latest')

# Explicit provider
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

model = MistralModel('mistral-large-latest', provider=MistralProvider(api_key='...'))

# Custom endpoint
model = MistralModel(
    'mistral-large-latest',
    provider=MistralProvider(api_key='...', base_url='https://custom-endpoint')
)
```

---

## OpenRouter Provider Details

Multi-model routing service with unified API.

```python
# Environment variable
export OPENROUTER_API_KEY='your-api-key'

# By name (model format: provider/model)
agent = Agent('openrouter:anthropic/claude-3.5-sonnet')
agent = Agent('openrouter:openai/gpt-4o')

# Explicit provider
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

model = OpenRouterModel('anthropic/claude-3.5-sonnet', provider=OpenRouterProvider(api_key='...'))
```

### App Attribution

```python
provider = OpenRouterProvider(
    api_key='...',
    app_url='https://your-app.com',
    app_title='Your App',
)
```

### Model Settings

```python
from pydantic_ai.models.openrouter import OpenRouterModel, OpenRouterModelSettings

settings = OpenRouterModelSettings(
    openrouter_reasoning={'effort': 'high'},
    openrouter_usage={'include': True}
)
model = OpenRouterModel('openai/gpt-5', model_settings=settings)
```
