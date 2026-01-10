# Qdrant Payload — overview (ingested: payload concept page)

Source: https://qdrant.tech/documentation/concepts/payload/

This note captures how payload (metadata) behaves, what types are filterable, and which update operations matter.

## What payload is

- Payload is JSON metadata stored alongside vectors.
- Payload is central to:
  - filtering (constraints)
  - faceting / aggregations (counts)
  - application-level semantics (e.g., access control fields, timestamps, categories)

## Filterable payload types (what Qdrant expects)

The page documents payload types that participate in filtering:
- integer (64-bit)
- float (64-bit)
- bool
- keyword (string)
- geo (lon/lat object)
- datetime (RFC 3339 variants; UTC assumed if timezone missing)
- uuid (functionally similar to keyword, but stored as parsed UUID internally and can reduce RAM in payload-heavy setups)

Array semantics (high value):
- if a payload field is an array, a filter succeeds if **any element** satisfies the condition.

Practical rule:
- Keep payload types consistent per field; mismatched type means the condition is treated as not satisfied.

## Write patterns: attach payload at upsert

- Payload can be included during point upsert.
- Arrays are supported for multi-valued metadata.

## Updating payload: choose the right operation

The page distinguishes:
- **Set payload**: update only provided fields, keep others unchanged.
- **Overwrite payload**: replace the entire payload.
- **Clear payload**: remove all payload keys.
- **Delete payload keys**: remove only specific keys.

Selection patterns:
- by explicit point IDs
- by filter selector (bulk updates without knowing IDs)

Nested update convenience:
- the guide mentions a `key` parameter that allows modifying only a nested object under a particular top-level key.

## Payload indexing (practical guidance)

- For efficient filtered search, create indexes for payload fields (type-specific).
- The page recommends indexing fields that constrain results the most (often high-cardinality identifiers), and using the most restrictive index first in compound filters.

## Facet counts (useful for UX and query planning)

- Faceting is a GROUP BY-like counting aggregation over a field.
- The page states a field must have a compatible index (e.g., keyword index for MatchValue) to facet on it.
- Result size is limited by default; can be increased with a limit.
- Counts may be approximate by default; there is an `exact` option when you need precision.
