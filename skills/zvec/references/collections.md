# Collections

Collections are the primary containers for documents in Zvec (similar to tables). They define the schema (fields + vectors + indexes) and own the on-disk storage.

## Create

Use `create_and_open()` to create a new collection on disk and return a `Collection` handle.

- If a collection already exists at the path, creation errors (prevents accidental overwrite).
- As of `0.3.1`, upstream removed earlier collection path restrictions and fixed Windows cross-drive creation issues.

### Schema building blocks

- `CollectionSchema(name=..., fields=[...], vectors=[...])`
- `FieldSchema(name=..., data_type=..., nullable=..., index_param=...)`
- `VectorSchema(name=..., data_type=..., dimension=..., index_param=...)`

### Options

- `read_only` must be `False` during creation.
- `enable_mmap` enables memory-mapped I/O (docs indicate default `True`).

Python snippets (as shown):

```python
import zvec

collection_option = zvec.CollectionOption(read_only=False, enable_mmap=True)
```

```python
import zvec

collection = zvec.create_and_open(
	path="/path/to/my/collection",
	schema=collection_schema,
	option=collection_option,
)
```

## Open

Use `open()` to load an existing collection directory.

- `path` must point to a valid collection directory.
- Use `read_only=True` when multiple processes access the same collection.
- If you previously had Windows-specific workarounds for drive/path behavior, re-test them on `0.3.1`; path-related diagnostics also improved.

```python
import zvec

existing_collection = zvec.open(
	path="/path/to/my/collection",
	option=zvec.CollectionOption(read_only=False, enable_mmap=True),
)
```

## Inspect

Helpful for debugging and monitoring:

- `collection.schema` (and `.fields`, `.vectors`)
- `collection.stats`
- `collection.option`
- `collection.path`

```python
print(collection.schema)
print(collection.schema.fields)
print(collection.schema.vectors)
print(collection.stats)
print(collection.option)
print(collection.path)
```

## Optimize

`collection.optimize()` builds/merges buffered vectors into the configured vector index.

- Newly inserted vectors accumulate in a flat buffer for fast ingestion.
- As the buffer grows, searches get slower.
- Optimization runs without blocking other reads/writes.

```python
collection.optimize()
```

## Destroy

Destroying a collection deletes its on-disk directory and all contents (irreversible).

```python
import zvec

collection = zvec.open(path="/path/to/my/collection")
collection.destroy()
```

## Schema evolution (DDL)

Zvec supports dynamic schema evolution for scalar fields and indexes.

Limitations mentioned:

- Adding/dropping vector fields is not supported yet.
- `add_column()` currently supports numerical scalar fields only, and `expression` must evaluate to a number.

Add/drop/alter column:

```python
import zvec

new_field = zvec.FieldSchema(name="rating", data_type=zvec.DataType.INT32)
collection.add_column(field_schema=new_field, expression="5")

collection.drop_column(field_name="publish_year")

collection.alter_column(old_name="publish_year", new_name="release_year")
```

Index management:

```python
import zvec

collection.create_index(
	field_name="dense_embedding",
	index_param=zvec.FlatIndexParam(metric_type=zvec.MetricType.COSINE),
)

collection.create_index(
	field_name="publish_year",
	index_param=zvec.InvertIndexParam(),
)

collection.drop_index(field_name="publish_year")
```

Constraint:

- Vector indexes cannot be dropped; every vector field must have exactly one index.

## Links

- Section: https://zvec.org/en/docs/collections/
- Create: https://zvec.org/en/docs/collections/create/
- Open: https://zvec.org/en/docs/collections/open/
- Inspect: https://zvec.org/en/docs/collections/inspect/
- Destroy: https://zvec.org/en/docs/collections/destroy/
- Optimize: https://zvec.org/en/docs/collections/optimize/
- Schema evolution: https://zvec.org/en/docs/collections/schema-evolution/
