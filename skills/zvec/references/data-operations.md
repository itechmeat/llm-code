# Data Operations

Zvec provides document-level operations for inserting, updating, deleting, fetching, and querying documents in a collection.

Docs note that writes (`insert`, `upsert`, `update`, `delete`) become visible to queries immediately (real-time workloads).

## Document shape (`Doc`)

- `id`: unique string identifier
- `fields`: scalar metadata (must match schema; nullable fields can be omitted)
- `vectors`: named dense/sparse vectors (must match schema type/dimension)

Schema mismatches (unknown field, wrong dimension/type) raise exceptions.

## Insert

- Adds new documents.
- Duplicate IDs fail; use upsert to overwrite.

```python
import zvec

result = collection.insert(
	[
		zvec.Doc(
			id="text_1",
			vectors={"text_embedding": [0.1, 0.2, 0.3, 0.4]},
			fields={"text": "This is a sample text."},
		),
		zvec.Doc(
			id="text_2",
			vectors={"text_embedding": [0.4, 0.3, 0.2, 0.1]},
			fields={"text": "This is another sample text."},
		),
	]
)

print(result)
```

## Upsert

- Insert-or-replace by `id`.
- After large upsert batches, run `collection.optimize()` to keep search fast.

```python
import zvec

result = collection.upsert(
	zvec.Doc(
		id="text_1",
		vectors={"text_embedding": [0.1, 0.2, 0.3, 0.4]},
		fields={"text": "Updated text."},
	)
)

print(result)
```

## Update

- Updates only the fields/vectors you provide; omitted content remains unchanged.
- IDs must already exist.

```python
import zvec

results = collection.update(
	[
		zvec.Doc(
			id="book_1",
			vectors={
				"sparse_embedding": {35: 0.25, 237: 0.1, 369: 0.44},
			},
			fields={
				"category": ["Romance", "Classic Literature", "American Civil War"],
			},
		),
		zvec.Doc(
			id="book_2",
			fields={
				"book_title": "The Great Gatsby",
			},
		),
	]
)

print(results)
```

## Delete

- Delete by IDs: `delete(ids=...)`.
- Bulk delete by scalar condition: `delete_by_filter(filter=...)`.

```python
result = collection.delete(ids=["doc_id_2", "doc_id_3"])
print(result)

collection.delete_by_filter(filter="publish_year < 1900")
```

## Query

`query()` supports vector similarity search, scalar filtering, or both.

- Single-vector: pass one `VectorQuery`.
- Multi-vector: pass a list of `VectorQuery` and fuse/rerank.

```python
import zvec

result = collection.query(
	vectors=zvec.VectorQuery(
		field_name="dense_embedding",
		vector=[0.1] * 768,
	),
	filter="publish_year < 1999",
	topk=10,
)
```

Multi-vector + weighted reranker example:

```python
import zvec

result = collection.query(
	topk=10,
	vectors=[
		zvec.VectorQuery(field_name="dense_embedding", vector=[0.1] * 768),
		zvec.VectorQuery(field_name="sparse_embedding", vector={1: 0.1, 37: 0.43}),
	],
	reranker=zvec.WeightedReRanker(
		topn=3,
		metric=zvec.MetricType.IP,
		weights={
			"dense_embedding": 1.2,
			"sparse_embedding": 1.0,
		},
	),
)
print(result)
```

## Fetch

Direct lookup by ID(s); missing IDs are omitted.

```python
result = collection.fetch(ids=["book_1", "book_2", "book_3"])
print(result)
```

## Links

- Section: https://zvec.org/en/docs/data-operations/
- Insert: https://zvec.org/en/docs/data-operations/insert/
- Upsert: https://zvec.org/en/docs/data-operations/upsert/
- Update: https://zvec.org/en/docs/data-operations/update/
- Delete: https://zvec.org/en/docs/data-operations/delete/
- Query: https://zvec.org/en/docs/data-operations/query/
- Fetch: https://zvec.org/en/docs/data-operations/fetch/
