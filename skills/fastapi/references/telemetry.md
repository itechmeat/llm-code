# Telemetry

FastAPI has native OpenTelemetry support since `0.142.0`. HTTP requests produce traces, metrics, and logs; WebSocket connections produce traces and logs. No custom code is needed to collect them — only to export them.

Install the exporters with the standard extras:

```bash
pip install "fastapi[standard]"
```

## Automatic Exporter Setup Is Opt-In (0.143.0)

FastAPI does **not** configure exporters from `OTEL_*` environment variables on its own. Opt in to keep the pre-0.143.0 behavior:

```bash
export FASTAPI_OTEL_AUTO_CONFIGURE=true
export OTEL_SERVICE_NAME=my-api
export OTEL_EXPORTER_OTLP_ENDPOINT=https://collector.example.com
export OTEL_EXPORTER_OTLP_HEADERS=api-key=YOUR_API_KEY
```

Or in code:

```python
from fastapi import FastAPI

app = FastAPI(telemetry={"auto_configure": True})
```

Rules:

- `auto_configure` defaults to `True` only when `FASTAPI_OTEL_AUTO_CONFIGURE=true`, otherwise `False`.
- An explicit `auto_configure` value in the `telemetry` dictionary overrides the environment variable (`telemetry={"auto_configure": False}` disables it even when the env var is set).
- When automatic setup is enabled and an OTLP endpoint is set, FastAPI adds an exporter for that destination to each enabled provider. Existing exporters keep sending to their own destinations.
- If another library already exports to the same destination, leave `FASTAPI_OTEL_AUTO_CONFIGURE` unset (or `false`) to avoid duplicate telemetry.
- Applications that configure their own providers and exporters require no changes.

## Telemetry Settings

The `telemetry` dictionary accepts these settings:

| Setting           | Purpose                                                   | Default                                          |
| ----------------- | --------------------------------------------------------- | ------------------------------------------------ |
| `tracing`         | Record HTTP request and WebSocket connection spans       | `True`                                           |
| `metrics`         | Record HTTP request metrics                              | `True`                                           |
| `logs`            | Record validation failures and unhandled exceptions      | `True`                                           |
| `operation_spans` | Add spans for request operations                         | `True`                                           |
| `exclude`         | Skip requests when a function receiving the scope returns `True` | `None`                                  |
| `auto_configure`  | Add exporters for endpoints set in environment variables | `True` if `FASTAPI_OTEL_AUTO_CONFIGURE=true`, otherwise `False` |

```python
app = FastAPI(
    telemetry={
        "tracing": False,
        "exclude": lambda scope: scope["path"] == "/health",
    }
)
```

## Custom Providers

```python
from fastapi import FastAPI
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

app = FastAPI(telemetry={"tracer_provider": tracer_provider})
```

Use `meter_provider` or `logger_provider` in the same dictionary for metrics or logs. The application or library that creates a provider manages its shutdown; FastAPI manages only the export components it adds.

By default FastAPI uses whatever providers the OpenTelemetry libraries configure globally, without adding exporters of its own.

⚠️ OpenTelemetry uses global providers by default, so independent telemetry configuration for mounted sub-applications is not guaranteed.

## What Gets Recorded

- **Request traces**: spans for dependency resolution, the path operation function, response serialization, and each `BackgroundTasks` task. Background task spans stay part of the request trace but run after the HTTP response span ends, so they do not increase the measured response time. Set `operation_spans=False` to keep only the HTTP request span.
- **WebSocket traces**: one span per connection (e.g. `WS /ws/{room}`) covering the handler and dependency cleanup, using the same providers and `operation_spans` setting.
- **Metrics**: HTTP request metrics only. Normal WebSocket disconnects (codes 1000 or 1001) do not produce error logs.
- **Logs**: unhandled exceptions are recorded as OpenTelemetry logs linked to the request trace, and are recorded even when the trace is not sampled. Exception type, message, and stack trace are included — filter or redact them in the provider's log processors, or set `logs=False` to disable them. Request validation failures are recorded as warning logs with the route and the error count; the invalid input is not included.

## Failure Handling

- A failed automatic OpenTelemetry configuration no longer aborts application startup (`0.142.2`).
- Tracers are cached, so repeated configuration warnings are deduplicated (`0.142.3`).
- Telemetry is isolated for excluded requests (`0.142.4`).

## Prohibitions

- ❌ Don't log request bodies or credentials through telemetry processors
- ❌ Don't assume `auto_configure` is on — it is opt-in since `0.143.0`
