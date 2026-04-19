# Migration to 1.0

Pipecat `1.0.0` is not a routine upgrade. It removes many deprecated shims and finishes several architectural migrations that started in the `0.0.x` line.

## Highest-impact changes

- `OpenAIResponsesLLMService` is now WebSocket-based by default; use `OpenAIResponsesHttpLLMService` if you explicitly need the older HTTP request model.
- Universal `LLMContext` and `LLMContextAggregatorPair` replace older service-specific context classes and `create_context_aggregator(...)` helpers.
- Turn detection, interruption behavior, and user mute logic now belong to `LLMUserAggregator` strategies instead of transport parameters and older filter/helper classes.
- Deprecated module aliases and compatibility packages were removed across services, transports, RTVI, and frames.
- Some long-deprecated APIs are gone entirely: `TTSService.say()`, `FrameProcessor.wait_for_task()`, older beta realtime services, `OpenPipeLLMService`, and single-argument tool calls.

## Upgrade checklist

1. Audit imports for removed aliases before changing runtime behavior.
2. Replace service-specific context classes with `LLMContext` and `LLMContextAggregatorPair`.
3. Review transport config for removed VAD/turn/interruption parameters.
4. Re-test function calling if you rely on background work, sequential tools, or custom tool schemas.
5. Re-test OpenAI Responses integrations under persistent WebSocket behavior.
6. Re-test TTS and interruption behavior under the current frame and user-turn APIs.

## Migration hotspots to search for

- `OpenAILLMContext`, `AnthropicLLMContext`, `AWSBedrockLLMContext`
- `create_context_aggregator(`
- `vad_enabled`, `vad_audio_passthrough`, `vad_analyzer`, `turn_analyzer`
- `allow_interruptions`, `interruption_strategies`, `STTMuteFilter`
- `TTSService.say(`
- `FrameProcessor.wait_for_task(`
- deprecated alias packages like `pipecat.services.openai_realtime`, `pipecat.services.google.gemini_multimodal_live`, `pipecat.transports.services`, `pipecat.transports.network`

## Practical rule

Do the mechanical migration first (imports, class names, config fields), then validate runtime behavior for context flow, interruptions, tool execution, and transport startup.

## Links

- Release: https://github.com/pipecat-ai/pipecat/releases/tag/v1.0.0
- Changelog: https://github.com/pipecat-ai/pipecat/blob/main/CHANGELOG.md
- Docs: https://docs.pipecat.ai/getting-started/introduction
