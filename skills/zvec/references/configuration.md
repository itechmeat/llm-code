# Configuration

Zvec exposes global configuration via an `init()` call.

## Key rule

- Call `init()` **once at application startup**, before creating/opening any collections.
- It is not intended for runtime reconfiguration.
- If you do not call `init()`, Zvec applies defaults tuned to the environment.

## What configuration is for (examples)

- Logging verbosity / output
- Concurrency controls (e.g., query thread count)

## Python example

```python
import zvec

zvec.init(
    log_type=zvec.LogType.CONSOLE,
    log_level=zvec.LogLevel.WARN,
    query_threads=4,
)
```

## Links

- Docs: https://zvec.org/en/docs/config/
- Python API reference: https://zvec.org/api-reference/python/config/
