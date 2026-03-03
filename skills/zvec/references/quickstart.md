# Quickstart

This page walks through the minimal workflow: create a collection with a schema, insert documents with vectors + metadata, and query by vector (optionally with filters).

If you still need installation steps, see `installation.md`.

## Minimal workflow (conceptual)

1. **Create a collection**
   - Define a schema with scalar fields + one or more vector fields.
2. **Add documents**
   - Insert/upsert documents containing `id`, scalar `fields`, and `vectors`.
3. **(Optional) Optimize**
   - Run an optimization step to improve performance (the page shows `collection.optimize()`).
4. **Retrieve by ID**
   - Fetch a document directly by its immutable `id`.
5. **Vector search**
   - Basic similarity search uses a `query()` operation (the docs highlight `query()` as the main entry).
   - Filtered similarity search combines vector search with a filter expression so only matching documents are considered.
6. **Inspect**
   - Print schema and stats (examples shown as `print(collection.schema)` and `print(collection.stats)`).
7. **Delete**
   - Delete by ID (example: `collection.delete(ids="book_1")`).
   - Delete by filter (example: `collection.delete_by_filter(filter="publish_year < 1900")`).

## Notes

- If the code examples on the site don’t show up in text extraction (client-rendered), open the page in a browser to copy exact snippets.

## Link

- Page: https://zvec.org/en/docs/quickstart/
