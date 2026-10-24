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

1. **Recover from URL or local file** (`PUT /collections/{collection_name}/snapshots/recover`)

- `location` can be:
  - an HTTP(S) URL reachable from the restoring node, or
  - a `file:///...` URI to a local snapshot file.
- If the target collection does not exist, Qdrant will create it.
- Cloud note: restoring from a URL is not supported if outbound traffic is blocked; use file URI or upload.

`1.18.0` security note:

- Operators can now disable snapshot restore from URL entirely. Use that in locked-down/self-hosted environments where restore inputs should come only from local files or explicit uploads.

2. **Recover from uploaded snapshot** (`POST /collections/{collection_name}/snapshots/upload?priority=...`)

- Upload snapshot bytes as multipart; recommended for migrations.
- Consider setting `priority=snapshot` for migration use-cases.

`1.18.1` auth note:

- Treat snapshot upload like any other privileged restore path. The `1.18.1` patch line fixes an authorization gap here, so hardened environments should verify upload/restore endpoints require the expected auth before and after upgrade.

3. **Recover during start-up** (Qdrant CLI flags)

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

## Snapshot storage configuration (paths, temp, object storage)

Local filesystem defaults:

- Default snapshot dir: `./snapshots` (or `/qdrant/snapshots` inside the Docker image).

Config knobs:

- `storage.snapshots_path` (env: `QDRANT__STORAGE__SNAPSHOTS_PATH`)
- `storage.temp_path` (optional separate temp dir for snapshot creation; useful if the storage disk is slow or space-constrained)

### Object storage backends (`1.19.2`)

`storage.snapshots_config.snapshots_storage` selects the backend: `"local"` (default), `"s3"`, `"gcs"` (alias `"gcp"`), or `"azure"`.

Each backend has its own config block next to the selector:

| Backend | Config block | Required fields | Credential / endpoint fields |
| --- | --- | --- | --- |
| S3 / S3-compatible | `s3_config` | `bucket` | `region`, `access_key`, `secret_key`, `endpoint_url` |
| Google Cloud Storage | `gcs_config` | `bucket` | `service_account_path`, `service_account_key`, `application_credentials_path`, `endpoint_url` |
| Azure Blob Storage | `azure_config` | `account`, `container` | `access_key`, `sas_token`, or `client_id` + `client_secret` + `tenant_id`; `endpoint_url` |

```yaml
storage:
  snapshots_config:
    snapshots_storage: gcs
    gcs_config:
      bucket: "my-bucket"
      prefix: "team-a/qdrant"
```

Credential chains — leave the credential fields empty to use them:

- **S3:** `AWS_*` environment variables and the default AWS credential chain.
- **GCS:** Application Default Credentials — `GOOGLE_*` environment variables, the gcloud credentials file, or the metadata server on GCE/GKE.
- **Azure:** `AZURE_*` environment variables, managed identity, or the Azure CLI.

Operational notes:

- Plain `http://` endpoints are allowed only when `endpoint_url` is explicitly set (emulators such as MinIO, fake-gcs-server, Azurite). Real cloud endpoints always use TLS.
- `endpoint_url` also covers S3-compatible stores (MinIO and similar), so the same `s3_config` block works for both AWS and a local emulator.
- A config block for a backend **other than the selected one is ignored**, and Qdrant logs a warning about it — in practice this means a typo in `snapshots_storage`.
- A backend can be selected without its config block; the client then resolves everything from the environment, and fails at startup if the bucket/account cannot be resolved.

### Snapshot prefix for object storage (`1.19.2`)

Every object-storage backend takes an optional `prefix` (`s3_config.prefix`, `gcs_config.prefix`, `azure_config.prefix`):

- Objects are written as `<prefix>/snapshots/<collection>/<snapshot>.snapshot`.
- Leading, trailing and repeated slashes in the prefix are dropped; an empty (or slash-only) prefix leaves object keys exactly where they were.
- The prefix is invisible in the names Qdrant reports back — `GET /collections/{name}/snapshots` still returns plain file names, and downloads/deletes work with those names.
- Objects outside the prefix are invisible to the API: they are not listed, not downloaded, and not deleted.

Use it to run several Qdrant deployments in one bucket/container without collisions, and to keep backups under a dedicated, separately lifecycle-managed prefix.

## `1.19.2` snapshot changes

- Shard transfers over the snapshot method now report the transferred bytes and the transfer rate in the transfer `comment` (visible on the source peer and, during snapshot recovery, on the target peer), so throughput can be read instead of estimated.
- A stale snapshot transfer on a recovering peer no longer breaks the other peers of the cluster.
- Uploading a snapshot without a collection configuration no longer writes the server-side path into the logs (see `references/security.md`).

## Operational guidelines

- For multi-tenant setups (one collection per tenant), snapshots are naturally scoped per collection.
- Choose between collection-level snapshot (per-collection backup/restore) vs full storage snapshot (single-node only).
- For self-hosted clusters, plan per-node snapshot creation/restore behavior.
- In clustered recovery, `1.18.0` prefers faster snapshot-based shard transfers when WAL delta replay is insufficient; that improves recovery speed, but disk headroom on the receiver still matters because the receiver clears shard data first to avoid out-of-disk crashes.
