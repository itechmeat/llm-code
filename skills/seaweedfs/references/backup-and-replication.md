# Backup and Replication

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Async-Backup
- https://github.com/seaweedfs/seaweedfs/wiki/Async-Filer-Metadata-Backup

## Async Backup

### What this page is about

- It explains continuous filer-driven backup to cloud or local sinks using change events.
- It documents `weed filer.backup`, sink configuration, and mirrored versus incremental strategies.

### Actionable takeaways

- Use `weed filer.backup` for near-real-time backup driven by filer metadata change logs.
- Generate `replication.toml` with `weed scaffold -config=replication` and keep only the sink sections you actually use.
- Expect backup state to resume across restarts because SeaweedFS stores progress offsets in filer metadata.
- Choose mirrored mode when deletes should propagate and path structure should stay the same.
- Choose incremental mode when point-in-time style daily snapshots are more valuable than delete mirroring.
- Consider cloud object storage as a practical backup sink because the page highlights low-ingest-cost economics.

### Gotchas / prohibitions

- Do not treat backup as restore-ready without separately validating recovery.
- Do not choose incremental mode if you expect deletions to be reflected in the backup.
- Do not run backup without a stable `replication.toml` shared across failover backup workers.

### How to apply in a real repo

- Define one backup strategy per dataset: mirrored DR copy or date-partitioned incremental retention.
- Keep backup process supervision and restart behavior under the same operational ownership as filer.

## Async Filer Metadata Backup

### What this page is about

- It describes continuous backup of filer metadata alone into a separate backup store.
- It is designed for cases where the primary filer store cannot be easily replicated or is embedded.

### Actionable takeaways

- Use `weed filer.meta.backup` when the metadata plane needs a separate protection strategy from content backup.
- Configure the backup store with the same store-style configuration concepts as `filer.toml`, but do not assume it must be the same backend type as the source.
- Expect metadata-backup progress to be resumable because the offset is tracked in the backup store itself.
- Consider cheap local or streamed secondary stores for metadata protection when the primary store is expensive or operationally awkward to replicate.

### Gotchas / prohibitions

- Do not confuse metadata backup with full content backup; this protects namespace and metadata state, not volume data by itself.
- Do not assume source and backup store must be identical; the page explicitly allows heterogenous pairs.

### How to apply in a real repo

- Keep metadata backup as a separate control in the recovery plan, especially when using embedded or hard-to-replicate filer stores.
- Validate restore paths from the backup store before trusting it as the only metadata fallback.
