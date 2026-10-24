---
name: pydantic-ai
description: "Pydantic AI Python agent framework. Covers typed tools, model providers, evals, MCP, UI adapters, and observability. Use when building Python AI agents with Pydantic AI, configuring model providers, implementing typed tools/dependencies, running evals, or integrating MCP servers. Keywords: pydantic-ai, agents, evals, MCP, Logfire."
metadata:
  version: "2.59.0"
  release_date: "2026-10-21"
---

# Pydantic AI

Python agent framework for building production-grade GenAI applications with the "FastAPI feeling".

## Quick Navigation

| Topic        | Reference                                     |
| ------------ | --------------------------------------------- |
| Agents       | [agents.md](references/agents.md)             |
| Capabilities | [agents.md](references/agents.md)             |
| Tools        | [tools.md](references/tools.md)               |
| Models       | [models.md](references/models.md)             |
| Embeddings   | [embeddings.md](references/embeddings.md)     |
| Evals        | [evals.md](references/evals.md)               |
| Integrations | [integrations.md](references/integrations.md) |
| Graphs       | [graphs.md](references/graphs.md)             |
| UI Streams   | [ui.md](references/ui.md)                     |
| Workspaces & Sandboxes | [workspaces-and-sandboxes.md](references/workspaces-and-sandboxes.md) |
| Realtime (speech-to-speech) | [realtime.md](references/realtime.md) |
| MCP Apps     | [mcp-apps.md](references/mcp-apps.md)         |
| Decision Models | [decision-models.md](references/decision-models.md) |
| Security     | [security.md](references/security.md)         |
| Installation | [installation.md](references/installation.md) |

## When to Use

- Building AI agents with structured output
- Need type-safe, IDE-friendly agent development
- Require dependency injection for tools
- Multi-model support (OpenAI, Anthropic, Gemini, etc.)
- Production observability with Logfire
- Complex workflows with graphs

## Installation

See `references/installation.md` for full/slim install options and optional dependency groups. Requires Python 3.10+.

## Release Highlights (2.49.0 -> 2.59.0)

- **Security (upgrade)**: three advisories landed in this window - the local `web_fetch` HTML conversion stall (High, GHSA-4whf-38hw-pxxh, fixed in `2.59.0`/`v1.107.9`), MCP server URLs/tokens/custom headers leaking into OpenTelemetry traces and URL-derived credential exposure (Medium, GHSA-xv4x-g8mx-ch56, fixed in `2.58.0`/`v1.107.8`), and client-triggered tool execution through the Vercel AI/AG-UI adapters with server-side `message_history` (Medium, GHSA-5pfm-2g3g-gh85, fixed in `2.58.0`). Rotate MCP credentials when upgrading from below `2.58.0`. Details in `references/security.md`.
- **Workspaces and sandboxes** (`2.52.0`+): `ctx.workspace` gives `Coder`, `Shell` and `FileSystem` one API for files and commands, running locally or in a sandbox with durable execution. New providers: `SpritesSandbox` (Fly.io Sprite), `E2BSandbox`, `SSHWorkspace`, `BubblewrapSandbox`, and `DaytonaSandbox` (`2.59.0`); `ModalSandboxBackend` replaces `ModalSandboxSession`. `Coder` file tools get a retry budget of 5 and keep scratch files out of the project. See `references/workspaces-and-sandboxes.md`.
- **Realtime** (`2.49.0` - `2.59.0`): OpenAI GPT-Live via `OpenAILiveModel` (`2.51.0`) with browser WebRTC (`2.52.0`), `ElevenLabsRealtimeModel` (`2.58.0`), `azure_voice_live_voice` (`2.52.0`), `gemini-3.8-live` (`2.50.0`), `RealtimeSession.wait_for_reply()` (`2.49.0`), `context_window_used` (`2.51.0`), the `async_tool_call_mode` profile setting (`2.52.0`), and the `AnswersRevised` / `OutputItemCut` lifecycle events (`2.59.0`). See `references/realtime.md`.
- **Provider-neutral errors** (`2.59.0`): `ModelRateLimitError`, `ModelUnavailableError`, `ModelServerError`, `ModelContextWindowExceededError`, plus `ModelHTTPError.for_category` to map a raw provider error onto them.
- **MCP Apps** (`2.57.0`): tool results can carry resources and app surfaces, forwarded to the AG-UI and Vercel AI frontends. `MCPToolset.read_resource_contents` and `MCPToolset.call_tool_for_app` read a resource or call an app-producing tool; `ToolKind` typed tool parts (`2.58.0`) let any module emit a typed tool part. See `references/mcp-apps.md`.
- **Decision models** (`2.49.0` - `2.50.0`): `DecisionModel` (the base `TypeSafeModel` builds on) answers several questions in one call and routes from the answers, with route fields, `decision_route_threshold`, `ModelSelectionContext.prompt` and `RunContext.in_durable_context`. `TypeSafeModel` gained "none of these" semantics and whole-number `Choice` options; `BoolCriteria` types boolean answers. See `references/decision-models.md`.
- **Providers and models** (`2.49.0` - `2.59.0`): Claude Sonnet 5.5 (`claude-sonnet-5-5`) with `AnthropicModel` default `max_tokens` raised from 4096 to 16384 on Sonnet 4.5+ (and defaulting to the model's maximum output); `MetaProvider` for Meta Muse (`2.57.0`); OpenAI `gpt-6-sol`/`gpt-6-luna`/`gpt-6-astra` on Bedrock Converse with `temperature`/`top_p` dropped for GPT-5.6/GPT-6 there; `GitHubCopilotProvider` can send a configurable `copilot-integration-id`; shut-down Groq models (`playai-tts`, `playai-tts-arabic`, `meta-llama/llama-guard-4-12b`, `meta-llama/llama-4-maverick-17b-128e-instruct`) were removed.
- **Agent control** (`2.57.0` - `2.59.0`): `DelegationTasks.steer` steers a running delegated task; `ModelSettings['max_retries']`, whole-agent `timeout=` and `RunContext.deadline`; `ApprovalReviewer` lets a model approve low-risk tool calls before a person sees them; `on_change='append'` for dynamic instruction prefixes (also opt-in on `FunctionToolset.instructions`); `tool_calls_limit` is checked before each `CodeMode` nested call; `BackgroundTools` results are framed as `<tool_result>` tool output; `read_file` can return images and PDFs; `SqliteStepStore` stores each message once.
- **Breaking change** (`2.52.0`): `SubAgents` no longer load agent files by default, and `inherit_tools` is deprecated.

## Release Highlights (2.40.0 -> 2.48.0)

- **Security (upgrade)** (`2.44.0`, backported to `1.107.6`): four fixes reached through `web_fetch_tool` or OTel instrumentation — IPv6 zone-identifier bypass of the private-IP blocklist when local URLs are opted in, superlinear `web_fetch` HTML/charset processing that could stall the event loop, domain blocklists compared without resolver normalization, and span content leaks with `include_content=False` (GHSA-vmxc-h2x2-jmf3, GHSA-fpf4-vwcp-v4hp, GHSA-22h6-qm39-v87j, GHSA-4x9p-g9wm-8q7f).
- **Realtime session control** (`2.40.0`/`2.46.0`): `handle_barge_in=True` with `interrupt(played_bytes=...)`, `RealtimeSession.enqueue()` for out-of-band prompts, `respond=` on `send()`, `wait_for_playback()`, and `@agent.on_event` listeners.
- **Image generation** (`2.41.0`): direct `ImageGenerator` API alongside the built-in tool; `fallback_model` on `ImageGeneration`/`XSearch` deprecated in favor of `fallback_subagent_model`.
- **Providers and models** (`2.41.0`/`2.42.0`/`2.48.0`): `openai-codex` provider for ChatGPT/Codex subscription auth, `GitHubCopilotProvider`; OpenAI `gpt-6-sol`/`gpt-6-luna` and Claude Opus 5.5 (`claude-opus-5-5`).
- **Pricing** (`2.40.0`): `pydantic_ai.prices.update_in_background()` refreshes `genai-prices` data in the background.
- **Temporal** (`2.46.0`): `event_stream_topic` on `TemporalDurability` streams agent events via Workflow Streams.

## Release Highlights (2.23.0 -> 2.39.0)

- **Realtime speech-to-speech** (`2.28.0`): `Agent.realtime()` with browser WebRTC plus server sideband support; Azure AI Voice Live via the `azure_voice_live` setting (`2.29.0`); `RealtimeSession.send_audio()` accepts async iterables (`2.36.0`).
- **Run cancellation** (`2.26.0`): `AgentRun.cancel()`, `RunContext.cancel()`, and `RunCancelled`; `stream_run_events()` returns a public `AgentRunEvents` handle with `cancel()` and run-state access.
- **Deferred tool reveal** (`2.23.0`/`2.26.0`/`2.30.0`): `ToolAvailabilityDeltaPart` with native `tool_addition`/`additional_tools`; tools can stay hidden until revealed via tool search, `load_capability`, or `ToolReturn.tools`, on each provider's native deferral/addition channel; a deferred tool must be revealed before it can be called.
- **Cost tracking** (`2.23.0`): `cost` on `RunUsage` and `cost_limit` on `UsageLimits`. **Context window** (`2.38.0`): `context_window` on `ModelProfile` and `context_window_used` on `RunContext`.
- **Typed events** (`2.38.0`): application code and capabilities can emit typed `CustomEvent`/`CapabilityEvent` into the run event stream and subscribe with `@on_event`. **Durable execution** (`2.36.0`): `@durable_operation` for capabilities plus a public backend API for third-party durable execution engines.
- **Providers and models**: Crusoe (`2.28.0`), Snowflake Cortex (`2.27.0`), and vLLM (`2.38.0`) providers; `gemini-3.7-flash` (`2.30.0`), `gemini-3.8-flash` (`2.38.0`), Claude Fable 5.1 / Mythos 5.1 (`2.38.0`), OpenAI `gpt-6-astra` (`2.39.0`), GLM-5.3 on `ZaiModel` (`2.34.0`), DeepSeek V4 Flash (`2.26.0`).
- **MCP and HTTP clients**: `MCPToolset` supports FastMCP 4 and MCP SDK v2 alongside FastMCP 3 (`2.29.0`). Builds moved to `httpx2` clients; `pydantic-ai[anthropic]` requires `anthropic>=1.0.0` and a custom `AnthropicProvider` `http_client` must be an `httpx2.AsyncClient` (`2.32.0`/`2.33.0`).
- **`clai` CLI** (`2.36.0`): `--mcp-config` support and tool-call streaming. **OpenRouter** (`2.30.0`/`2.32.0`): `openrouter:web_search` for web search and web-search sources in `provider_details["annotations"]`.
- **Security (upgrade)**: `2.24.0` fixes unbounded memory in the local `web_fetch` tool / `FileUrl` media downloads (GHSA-v2xh-2vp8-57h8); `2.27.1` fixes a low-severity retry-prompt redaction leak when `include_content=False` (GHSA-3gh4-cghq-f8v4); `2.28.0` fixes a high-severity missing content-type check on the dev web chat UI so arbitrary cross-origin requests no longer run the agent (GHSA-h4xc-3qfq-jf93); `2.30.0` fixes DNS-rebinding via `Host`-header validation on the dev web chat UI, with an opt-in `allowed_hosts` for non-loopback deployments (GHSA-q2xc-rrxj-58x9).

## Release Highlights (2.13.0 -> 2.22.0)

- **Durability capabilities replace wrapper agents**: `TemporalDurability`, `DBOSDurability`, and `PrefectDurability` (`2.14.0`) attach to a regular `Agent` via `capabilities=[...]`, replacing the deprecated `TemporalAgent` / `DBOSAgent` / `PrefectAgent` wrapper classes (removed in v3). Existing wrapper-based workflows keep replaying correctly after switching. See `integrations.md` for the updated Temporal/DBOS/Prefect examples.
- **New models/providers**: Claude Opus 5 (`2.20.0`), `gemini-3.6-flash`/`gemini-3.5-flash-lite` (`2.16.0`), Mistral `reasoning_effort` (`2.14.0`) and `mistral_prompt_cache_key` (`2.16.0`), OpenAI explicit prompt caching for `gpt-5.6` (`2.15.0`), `BedrockMantleProvider` (`2.18.0`), and the `AdvisorTool` builtin tool for Anthropic/OpenRouter (`2.18.0`).
- **Usage & limits**: `cache_hit_ratio` on `RequestUsage`/`RunUsage` (`2.13.0`), `ToolFailed` for model-visible failures that don't consume a retry (`2.16.0`), optional `run_id=` on runs (`2.16.0`), tool-retry budget overrides at `run`/`iter`/`override` time (`2.15.0`), and `per_request_input_tokens_limit` on `UsageLimits` (`2.21.0`).
- **Error handling & instrumentation**: `ModelHTTPError` now carries `headers` and a parsed `retry_after` from every provider SDK (`2.19.0`); `RaiseContentFilterError` capability and `include_model_request_parameters` instrumentation setting (`2.13.0`); per-message OTel serialization is cached to avoid `O(n^2)` cost (`2.17.0`).
- **Dependencies**: the `fastmcp` optional group now constrains `fastmcp<4` (`2.19.0`).

## Release Highlights (2.0.0 -> 2.12.0)

- **V2 stable (`2.0.0`)**: harness-first design with **capabilities** as the core primitive, a single composable unit bundling an agent's tools, hooks, instructions, and model settings. Migrating from V1 requires the official upgrade guide; the capability-based paths deprecated across the 1.9x line are now the default.
- **Message history & processing**: `message_history` is provider-valid with repaired tool-call pairing, `HistoryProcessor` is exported, and deferred tool-call events plus `EnqueuedMessagesEvent` are available (`2.10.0` to `2.12.0`).
- **New models/providers**: Moonshot AI `kimi-k3`, OpenAI background mode, and Anthropic `stop_reason=pause_turn` support; standardized reasoning-effort handling across Groq, DeepSeek, and Cerebras.
- **Embeddings & tokens**: Gemini 2 text-prefix conditioning for embeddings and output audio-token accumulation in usage tracking.
- **Fixes**: `ToolReturnPart` serialization uses field aliases, Anthropic/Bedrock native output schema handling, and actionable hints on usage-limit and tool-retry errors.

## Release Highlights (1.96.1)

- **V2 preparation**: `Agent(..., prepare_tools=..., prepare_output_tools=..., event_stream_handler=...)` is now the deprecated path; capability-based migration is the new direction.
- **Capability migration**: use `PrepareTools`, `PrepareOutputTools`, and `ProcessEventStream` capabilities instead of wiring those behaviors through constructor sugar.
- **OpenAI fixes**: the latest patch line also tightens `OpenAIResponsesModel` system-prompt-role handling and image-generation request shaping.

## Release Highlights (1.97.0 -> 1.102.0)

- **MCP migration**: prefer `MCPToolset` for new MCP integrations. `FastMCPToolset` and the older `MCPServer*` client surface are now on the deprecation path.
- **Google provider split**: `GoogleProvider` and `GoogleCloudProvider` are now distinct, and model ids move from `google-gla:` / `google-vertex:` to `google:` / `google-cloud:`.
- **Streaming migration**: move from `stream_responses()` to `stream_response()`; the newer API yields `ModelResponse` objects directly.
- **Retry configuration**: prefer `Agent(retries=...)` or `AgentRetries(...)` over older constructor-level retry knobs.
- **New runtime tools**: `ctx.enqueue()` and MCP background tasks make it easier to queue follow-up work without forcing it into the current response turn.

## Release Highlights (1.105.0 -> 1.107.0)

- **New models**: Claude Fable 5 and Claude Mythos 5 are supported (1.107.0), alongside Grok 4.3 `reasoning_effort` and updated xAI model names (1.105.0).
- **Deferred loading**: instructions, tools, model settings, and hooks can now be loaded on demand instead of eagerly at agent construction (1.105.0).
- **Model introspection**: `known_model_names()` enumerates `KnownModelName` members (1.107.0).
- **OpenRouter caching**: `CachePoint` and prompt caching are implemented for OpenRouter (1.107.0).
- **xAI config**: `XaiProvider` gains `api_host` and `timeout`, plus `seed` parameter mapping (1.106.0).
- **Security**: `VercelAIAdapter` `UploadedFile` handling was hardened against a confused-deputy file-read vulnerability (GHSA-h7p7-w5gc-xj3w, 1.106.0).
- **Fixes**: incomplete streamed responses when `event_stream_handler` doesn't consume the stream, `from_data_uri` on non-base64 data URIs, Temporal `gateway/` model construction, `GoogleModelSettings.google_cached_content` request shaping, Anthropic Bedrock `message=None` start events, and `AnthropicModel.count_tokens` with native tools.

## Release Highlights (1.103.0 -> 1.104.0)

- **MCP prompts**: maintained `McpServer` integrations can now list and fetch prompts with `list_prompts` and `get_prompt`; still prefer `MCPToolset` for new client code unless legacy wrappers are required.
- **UI adapters**: `VercelAIAdapter` round-trips message timestamps through `UIMessage.metadata`, and `UIAdapter.sanitize_messages` strips client-submitted `force_download` from `FileUrl` parts.
- **Provider/model updates**: Claude Opus 4.8 is supported, `OpenRouterModel` can use `anthropic_eager_input_streaming`, and hybrid OpenRouter/xAI/Bedrock routes now forward `thinking=False` consistently.
- **Bedrock/toolset fixes**: Bedrock maps malformed model/tool output to `FinishReason.error`, recognizes adaptive thinking, preserves single-tool `tool_choice` cache behavior, and toolset prepare callbacks warn when they accidentally return `None`.

## Release Highlights (1.75.0 -> 1.84.1)

- **Capabilities**: `CapabilityOrdering` adds explicit wrapping/ordering control (`innermost`, `outermost`, `wraps`, `wrapped_by`, `requires`) for complex capability stacks.
- **Compaction**: new server-side compaction capabilities for OpenAI and Anthropic; OpenAI adds stateful compaction mode.
- **Models**: Claude Opus 4.7 support and a native `OllamaModel` path with corrected Ollama capability flags for structured output.
- **Tools**: tool hooks now consistently receive dict-shaped validated args for single-`BaseModel` tools, and internal output tools skip hook execution.
- **Hardening**: Google `FileSearchTool` parsing received regex hardening in the `1.83/1.84` line.

## Release Highlights (1.71.0 → 1.74.0)

- **Capabilities**: composable, reusable units of agent behavior that bundle tools, lifecycle hooks, instructions, and model settings into a single class. Plug into any agent for maximum reuse.
- **AgentSpec**: load agents from YAML/JSON files via `Agent.from_file`. Supports `TemplateStr` for templated instructions referencing deps.
- **Hooks capability**: define hooks using decorators (`@hooks.on_model_request`, etc.).
- **Thinking capability**: cross-provider `thinking` model setting for reasoning.
- **Provider-adaptive tools**: `WebSearch`, `WebFetch`, `MCP`, `ImageGeneration` — automatically fall back from builtin (provider) tools to local tools.
- **Online evaluation**: evaluation infrastructure in `pydantic-evals`.
- **`TextContent`**: user prompts with `metadata` not sent to model.
- **CaseLifecycle hooks**: hooks for `Dataset.evaluate` lifecycle.
- **Model swapping in hooks**: `before_model_request` / wrap hooks can swap models via `ModelRequestContext`.
- **`ModelRetry` from hooks**: hooks can raise `ModelRetry` for retry control flow.
- Sync tool preparation functions supported. `MCP` capability no longer requires explicit `url=`.

## Release Highlights (1.69.0 → 1.70.0)

- Agents: `Agent(description=...)` adds a human-readable description to the run span as `gen_ai.agent.description` when instrumentation is enabled.
- Models: `FallbackModel` now supports response-based fallback handlers for semantic failures in non-streaming runs.
- Tools: multimodal tool results are passed directly to provider APIs instead of always being split into extra user-message parts.
- Bedrock: `bedrock_inference_profile` is available on model and embedding settings for routing requests through an inference profile ARN.
- Stability: provider fixes landed for OpenRouter Anthropic model matching, Cohere embeddings, Google image sizes, Bedrock tool-name sanitization, and malformed tool-call retry handling.

## Quick Start

### Basic Agent

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    instructions='Be concise, reply with one sentence.'
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
```

### With Structured Output

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class CityInfo(BaseModel):
    name: str
    country: str
    population: int

agent = Agent('openai:gpt-4o', output_type=CityInfo)
result = agent.run_sync('Tell me about Paris')
print(result.output)  # CityInfo(name='Paris', country='France', population=2161000)
```

### With Tools and Dependencies

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class Deps:
    user_id: int

agent = Agent('openai:gpt-4o', deps_type=Deps)

@agent.tool
async def get_user_name(ctx: RunContext[Deps]) -> str:
    """Get the current user's name."""
    return f"User #{ctx.deps.user_id}"

result = agent.run_sync('What is my name?', deps=Deps(user_id=123))
```

## Key Features

| Feature              | Description                     |
| -------------------- | ------------------------------- |
| Type-safe            | Full IDE support, type checking |
| Model-agnostic       | 30+ providers supported         |
| Dependency Injection | Pass context to tools           |
| Structured Output    | Pydantic model validation       |
| Embeddings           | Multi-provider vector support   |
| Logfire Integration  | Built-in observability          |
| MCP Support          | External tools and data         |
| Evals                | Systematic testing              |
| Graphs               | Complex workflow support        |

## Supported Models

| Provider  | Models                                |
| --------- | ------------------------------------- |
| OpenAI    | GPT-4o, GPT-4, o1, o3                 |
| Anthropic | Claude Opus 5, Claude Opus 4.8, Claude 4, Claude 3.5 |
| Google    | Gemini 2.0, Gemini 1.5                |
| xAI       | Grok-4 (native SDK)                   |
| Groq      | Llama, Mixtral                        |
| Mistral   | Mistral Large, Codestral              |
| Azure     | Azure OpenAI                          |
| Bedrock   | AWS Bedrock + Nova 2.0                |
| SambaNova | SambaNova models                      |
| Ollama    | Local models                          |

## Best Practices

1. **Use type hints** — enables IDE support and validation
2. **Define output types** — guarantees structured responses
3. **Use dependencies** — inject context into tools
4. **Add tool docstrings** — LLM uses them as descriptions
5. **Enable Logfire** — for production observability
6. **Use `run_sync` for simple cases** — `run` for async
7. **Override deps for testing** — `agent.override(deps=...)`
8. **Set usage limits** — prevent infinite loops with `UsageLimits`

## Prohibitions

- Do not expose API keys in code
- Do not skip output validation in production
- Do not ignore tool errors
- Do not use `run_stream` without handling partial outputs
- Do not forget to close MCP connections (`async with agent`)
- Do not assume capability order is arbitrary once multiple wrappers/hooks are involved; define it explicitly when composition matters.
- Do not run below `2.59.0` with the local `web_fetch` tool, and do not run below `2.58.0` with native MCP servers - see `references/security.md`.
- Do not export MCP traces before checking for leaked server URLs, tokens and headers; rotate any credential that was exposed before the `2.58.0` upgrade.
- Do not treat server-side `message_history` as a security boundary behind a Vercel AI or AG-UI endpoint.

## Common Patterns

### Streaming Response

```python
async with agent.run_stream('Query') as response:
    async for text in response.stream_text():
        print(text, end='')
```

### Fallback Models

```python
from pydantic_ai.models.fallback import FallbackModel

fallback = FallbackModel(openai_model, anthropic_model)
agent = Agent(fallback)
```

### MCP Integration

```python
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset(command='python', args=['mcp_server.py'])
agent = Agent('openai:gpt-4o', toolsets=[toolset])
```

### Testing with TestModel

```python
from pydantic_ai.models.test import TestModel

agent = Agent(model=TestModel())
result = agent.run_sync('test')  # Deterministic output
```

### Embeddings

```python
from pydantic_ai import Embedder

embedder = Embedder('openai:text-embedding-3-small')

# Embed search query
result = await embedder.embed_query('What is ML?')

# Embed documents for indexing
docs = ['Doc 1', 'Doc 2', 'Doc 3']
result = await embedder.embed_documents(docs)
```

See [embeddings.md](references/embeddings.md) for providers and settings.

### xAI Provider

```python
from pydantic_ai import Agent

agent = Agent('xai:grok-4-1-fast-non-reasoning')
```

See [models.md](references/models.md#xai-grok) for configuration details.

### Exa Neural Search

```python
import os
from pydantic_ai import Agent
from pydantic_ai.common_tools.exa import ExaToolset

api_key = os.getenv('EXA_API_KEY')
toolset = ExaToolset(api_key, num_results=5, include_search=True)
agent = Agent('openai:gpt-4o', toolsets=[toolset])
```

See [tools.md](references/tools.md#exa-neural-search) for all Exa tools.

## Links

- [Documentation](https://ai.pydantic.dev/)
- [Releases](https://github.com/pydantic/pydantic-ai/releases)
- [GitHub](https://github.com/pydantic/pydantic-ai)
- [PyPI](https://pypi.org/project/pydantic-ai/)
