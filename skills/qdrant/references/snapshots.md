# Snapshots (Qdrant Concepts) — practical notes

Source: https://qdrant.tech/documentation/concepts/snapshots/

## What a snapshot is (and what it is not)

- A snapshot is a **tar archive** containing the **data + collection configuration** for a specific collection **on a specific node** at a specific time.
- In a **distributed** deployment, you must create snapshots **per node** for the same collection (each node only has its local shard data).
- Collection-level snapshots **do not include aliases**; handle aliases separately.
- Qdrant Cloud has “Backups” as a disk-level alternative; snapshots are still useful for OSS/self-hosted workflows.

## Collection snapshots: create / list / delete / download

Core endpoints:
- Create: `POST /collections/{collection_name}/snapshots` (synchronous; generates a `.snapshot` file in `snapshots_path`).
- List: `GET /collections/{collection_name}/snapshots`
- Delete: `DELETE /collections/{collection_name}/snapshots/{snapshot_name}`
- Download: `GET /collections/{collection_name}/snapshots/{snapshot_name}` (REST-only per docs).

Practical implications:
- Treat snapshot creation as an **IO-heavy operation**; plan disk space and timing.
- In a cluster, coordinate per-node snapshot creation if you need a consistent point-in-time capture.

## Restore constraints (version + topology)

- A snapshot can only be restored into a cluster that shares the **same minor version**.
  - Example from docs: `v1.4.1` → `v1.4.x` with `x >= 1`.

## Restore methods (and when to use which)

Qdrant supports three restoration paths:

1) **Recover from URL or local file** (`PUT /collections/{collection_name}/snapshots/recover`)
- `location` can be:
  - an HTTP(S) URL reachable from the restoring node, or
  - a `file:///...` URI to a local snapshot file.
- If the target collection does not exist, Qdrant will create it.
- Cloud note: restoring from a URL is not supported if outbound traffic is blocked; use file URI or upload.

2) **Recover from uploaded snapshot** (`POST /collections/{collection_name}/snapshots/upload?priority=...`)
- Upload snapshot bytes as multipart; recommended for migrations.
- Consider setting `priority=snapshot` for migration use-cases.

3) **Recover during start-up** (Qdrant CLI flags)
- Single-node only (not multi-node, not Cloud).
- Start Qdrant with repeated `--snapshot <path>:<target_collection>` pairs.
- The target collection must be **absent**, otherwise Qdrant exits with an error.
- `--force_snapshot` overwrites existing collections; treat as a dangerous operation.

## Snapshot recovery priority (critical gotcha)

When restoring onto a non-empty node, conflicts are resolved by `priority`:

- `replica` (default): prefer existing data over snapshot.
- `snapshot`: prefer snapshot over existing data.
- `no_sync`: restore without extra synchronization (advanced; easy to break the cluster).

Important gotcha:
- To recover a **new collection** from a snapshot, you typically need `priority=snapshot`.
  - With the default `replica` priority, the docs note you can end up with an **empty collection** if the system prefers the “existing” (empty) state.

## Full storage snapshots (single-node only)

- Full storage snapshots capture **whole storage**, including **collection aliases**.
- They are **not suitable for distributed mode**.
- They can be created/downloaded in Cloud, but Cloud cannot be restored from a full storage snapshot because that requires the CLI.

Endpoints:
- Create: `POST /snapshots`
- List: `GET /snapshots`
- Delete: `DELETE /snapshots/{snapshot_name}`
- Download: `GET /snapshots/{snapshot_name}` (REST-only per docs)

Restore:
- CLI at startup: `./qdrant --storage-snapshot /path/to/full.snapshot`

## Snapshot storage configuration (paths, temp, S3)

Local filesystem defaults:
- Default snapshot dir: `./snapshots` (or `/qdrant/snapshots` inside the Docker image).

Config knobs:
- `storage.snapshots_path` (env: `QDRANT__STORAGE__SNAPSHOTS_PATH`)
- `storage.temp_path` (optional separate temp dir for snapshot creation; useful if the storage disk is slow or space-constrained)

S3 support (S3-compatible):
- Configure `storage.snapshots_config` with `snapshots_storage: s3` and `s3_config` (bucket/region/access_key/secret_key/endpoint_url).

## Operational guidelines

- For multi-tenant setups (one collection per tenant), snapshots are naturally scoped per collection.
- Choose between collection-level snapshot (per-collection backup/restore) vs full storage snapshot (single-node only).
- For self-hosted clusters, plan per-node snapshot creation/restore behavior.
