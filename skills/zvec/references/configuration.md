# Configuration

Zvec exposes global configuration via an `init()` call.

## Key rule

- Call `init()` **once at application startup**, before creating/opening any collections.
- It is not intended for runtime reconfiguration.
- If you do not call `init()`, Zvec applies defaults tuned to the environment.

## What configuration is for (examples)

- Logging verbosity / output
- Concurrency controls (e.g., query thread count)

## Removed in 0.8.0: global Jieba dictionary directory

The global Jieba dictionary configuration is gone, because the default dictionary and HMM model are embedded in the native libraries:

- `zvec.init(jieba_dict_dir=...)` — removed
- `zvec.set_default_jieba_dict_dir(...)` / `zvec.get_default_jieba_dict_dir()` — removed
- The matching C configuration accessors, C default-directory APIs, and the C++ global configuration field plus its registration APIs — removed

To point Zvec at a different main dictionary, configure the indexed FTS field (`FtsIndexParam.extra_params.jieba_dict_dir`) or set `ZVEC_JIEBA_DICT_DIR`; the field configuration takes precedence. See `references/fts-chinese-dictionaries.md` for the full migration.

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
- Chinese FTS dictionaries: `fts-chinese-dictionaries.md`
