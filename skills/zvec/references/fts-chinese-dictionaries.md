# Chinese FTS dictionaries (Jieba)

Chinese full-text search in Zvec relies on Jieba-style word segmentation. As of `0.8.0` the default Jieba dictionary and the HMM model are **embedded in the native libraries**, so a working Chinese FTS index needs no dictionary download and no directory setup.

This page covers the breaking `0.8.0` removal of the global dictionary configuration, the supported ways to point Zvec at a different main dictionary, and how to add business vocabulary.

## What changed in 0.8.0 (breaking)

The **global** Jieba dictionary configuration was removed. The following APIs no longer exist:

- Python: `zvec.init(jieba_dict_dir=...)`
- Python: `zvec.set_default_jieba_dict_dir(...)`
- Python: `zvec.get_default_jieba_dict_dir()`
- C: the Jieba configuration accessors and the C default-directory APIs
- C++: the global configuration field and its registration APIs

Reason: with the default dictionary and HMM model embedded in the library, there is no global default dictionary directory left to point at. The setting moved down to the individual FTS field, where the dictionary is actually used.

Nothing changes for users who never configured a dictionary directory — segmentation behaviour comes from the embedded defaults.

## Migration

### Python — old way (0.7.x and earlier)

```python
import zvec

# Removed in 0.8.0 — this call now fails.
zvec.init(jieba_dict_dir="/opt/jieba/dict")
```

### Python — new way (0.8.0+)

Set the directory on the FTS index parameter of the field being indexed:

```python
import zvec

collection.create_index(
    field_name="text",
    index_param=zvec.FtsIndexParam(
        extra_params={"jieba_dict_dir": "/opt/jieba/dict"},
    ),
)
```

The option key inside `extra_params` is the contract; check the upstream Python API reference for the exact constructor signature of `FtsIndexParam`.

### Environment-variable route

When the same dictionary applies to every FTS field in the process, set `ZVEC_JIEBA_DICT_DIR` in the environment instead of touching each index:

```bash
export ZVEC_JIEBA_DICT_DIR=/opt/jieba/dict
```

### C / C++

The global registration APIs are gone; configure the directory on the FTS index parameter for the indexed field instead. The C configuration accessors and the C default-directory APIs are removed as well, so a binding that still calls them will not compile.

## Resolution order

The main dictionary is resolved in this order:

1. `FtsIndexParam.extra_params.jieba_dict_dir` on the indexed field — **highest precedence**
2. the `ZVEC_JIEBA_DICT_DIR` environment variable
3. the embedded default dictionary plus the embedded HMM model — fallback

Field configuration takes precedence over the environment variable. A per-field setting therefore wins even when the environment variable points at a different dictionary.

## Adding business vocabulary

Use `user_dict_path` in the FTS index `extra_params` to point at an additional user dictionary that adds domain terms, product names, or person names on top of the main dictionary:

```python
collection.create_index(
    field_name="text",
    index_param=zvec.FtsIndexParam(
        extra_params={
            "jieba_dict_dir": "/opt/jieba/dict",
            "user_dict_path": "/opt/jieba/user_dict.txt",
        },
    ),
)
```

- `jieba_dict_dir` replaces the **main** dictionary.
- `user_dict_path` **adds** to whatever main dictionary is in effect; it does not replace it.
- The two options combine: a custom main dictionary plus an extra user dictionary is a valid configuration.

## Isolation rules

- The parsed default dictionary and HMM model are **shared**: they are decoded and parsed once and reused across tokenizer instances, so creating many FTS indexes does not repeat that cost.
- Custom user dictionaries stay **isolated** between tokenizer instances. A `user_dict_path` configured on one index does not leak into another index or another collection.

## Operational notes

- The embedded resources are shipped LZ4-compressed in the Python wheels and the native SDKs; there is no first-run download step and no filesystem cache to manage.
- Because the defaults are embedded, container images need no extra dictionary layer — but a custom `jieba_dict_dir` or `user_dict_path` must still be readable by the process at index creation time.
- Keep dictionary paths outside the collection directory: the collection directory is a self-contained, relocatable unit and should not depend on external paths.
- Re-index after changing the dictionary: an FTS index built with one dictionary does not automatically pick up a changed `jieba_dict_dir` or `user_dict_path`.

## Operator checklist

- Grep the codebase for `jieba_dict_dir`, `set_default_jieba_dict_dir`, and `get_default_jieba_dict_dir` before upgrading; all three are gone.
- Decide per collection whether one shared dictionary (env var) or per-field dictionaries fit better.
- Verify segmentation on real domain text after the upgrade — a different main dictionary changes token boundaries and therefore recall and highlighting.

## Links

- FTS overview: https://zvec.org/en/docs/db/concepts/fts-index/
- Python API params: https://zvec.org/api-reference/python/params/
- Release notes (0.8.0): https://github.com/alibaba/zvec/releases/tag/v0.8.0
