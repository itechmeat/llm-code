# Qdrant Points — overview (ingested: points concept page)

Source: https://qdrant.tech/documentation/concepts/points/

This note summarizes the **Points** concept page, focusing on how point writes/updates behave in practice.

## What a point is

- A point is the central record in Qdrant.
- It contains:
  - an ID
  - one or more vector representations
  - optional payload (metadata)

## IDs (design choice)

- The docs state Qdrant supports point IDs as:
  - 64-bit unsigned integers
  - UUIDs (multiple string formats are accepted)

Practical guidance:
- Prefer UUIDs if IDs come from outside your system or you need low collision risk.
- Prefer integers for compactness when you control ID assignment.

## Write path semantics (important)

- Point modification operations are described as **asynchronous** and written to a write-ahead log first.
- This implies a “durable but not immediately visible” window depending on whether you wait for completion.

### `wait` / eventual consistency (high value)

- If you do not request waiting, you can receive an acknowledgment before the update is fully applied.
- If you need the update to be searchable immediately after the call returns, you must use the “wait for completion” mode.

Practical rule:
- For ingestion pipelines that can tolerate lag, async is fine.
- For request/response flows where the user expects immediate retrieval, use wait mode.

## Upsert / idempotence

- The docs describe APIs as idempotent: re-sending the same upsert leads to the same final state.
- Points with the same ID are overwritten when re-uploaded.

Practical rule:
- Safe for “at-least-once” delivery pipelines (queues) as long as overwrites are acceptable.

## Vectors model

- A point can have multiple vectors, including different types; Qdrant supports:
  - dense vectors
  - sparse vectors
  - multivectors
- Multiple vectors per point are referred to as named vectors.

### Named vectors replacement vs partial updates

- Uploading a point with an existing ID replaces the whole point (unspecified vectors can be removed).
- There is a dedicated “update vectors” operation to update only the specified vectors while keeping the others unchanged.

## Batch ingestion

- The page describes two batch formats:
  - record-oriented (list of points)
  - column-oriented (ids/payloads/vectors arrays)

Practical rule:
- Choose whichever fits your ETL shape; they’re equivalent internally.

## Python client ingestion helpers

- The page highlights Python client helpers that can:
  - parallelize uploads
  - retry
  - batch lazily (useful for streaming from disk)

## Conditional updates (optimistic concurrency)

- Update operations can include a filter-based precondition.
- This can implement optimistic concurrency control (e.g., only update if payload `version` matches).

Practical rule:
- Use conditional updates for background re-embedding jobs to prevent overwriting fresh application writes.

## Retrieval patterns (useful for apps)

- Retrieve by IDs (selective fetch)
- Scroll (iterate by ID order; filterable)
  - Ordering by payload key exists but requires an appropriate payload index; pagination changes when using order_by.
- Count by filter (useful for analytics and pagination sizing)

## Next ingestion targets (one URL at a time)

- Payload page (to connect “update payload / overwrite payload” semantics)
- Vectors page (to cover vector storage and optimization)
