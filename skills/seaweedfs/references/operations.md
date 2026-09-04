# Operations

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/System-Metrics
- https://github.com/seaweedfs/seaweedfs/wiki/weed-shell

## System Metrics

### What this page is about

- It explains SeaweedFS metrics export for Prometheus/Grafana in both push and pull modes.
- It shows how masters distribute push-gateway config to other components.

### Actionable takeaways

- Choose push mode when a Prometheus Pushgateway fits the environment and pull mode when Prometheus can scrape each service directly.
- Set the metrics address on all masters when using push mode so volume servers and filers can inherit the target.
- Restart filers and volume servers after changing master metrics settings because they need to re-read the configuration.
- Use dedicated metrics ports per process when exposing scrape endpoints directly.
- Reuse the upstream Grafana dashboard as a starting point instead of building panels from scratch.
- Master and volume processes now export `start_time_seconds`, which is useful for restart detection and rollout dashboards.
- `4.29` exposes Admin Server Prometheus metrics; scrape it separately from master/volume/filer metrics when the admin worker participates in EC placement or vacuum workflows.
- `4.30` adds `/healthz` and `/readyz` probes across S3, IAM, volume, filer, and master services. Prefer readiness probes for traffic admission and health probes for restart decisions in orchestrated deployments.
- `4.40` fixes master used-size statistics to cover all collections instead of undercounting a subset; rebuild or re-baseline capacity dashboards that trusted the old figure, since prior totals could read lower than actual usage.

### Gotchas / prohibitions

- Do not change master metrics configuration and assume other services pick it up live.
- Do not reuse the same pull metrics port across several services on one host.

### How to apply in a real repo

- Standardize one monitoring mode per environment to avoid half-configured push and pull setups.
- Keep metric-port and Pushgateway settings in the same deployment templates as service endpoints.

## weed shell

### What this page is about

- It presents `weed shell` as the main interactive maintenance surface for cluster, filer, volume, EC, S3, and remote-storage operations.
- It also shows the lock/unlock pattern for safe volume maintenance.

### Actionable takeaways

- Treat `weed shell` as the operator console for controlled maintenance and recovery rather than ad-hoc HTTP calls alone.
- Use `lock` and `unlock` around volume-changing operations so concurrent cluster activity does not interfere with repairs.
- Rely on `volume.fix.replication`, `volume.vacuum`, `volume.balance`, `ec.*`, `fs.meta.*`, `remote.*`, and `s3.*` commands as the canonical operational toolkit.
- Use dry-run or preview-style flags such as `-n` before performing replication repair when possible.
- Use `volume.check.disk`, `volume.fsck`, `fs.meta.cat`, and `fs.verify` when diagnosing missing chunks or filer-to-volume inconsistencies. The Rust volume server now verifies that a `.dat` file ends at the last indexed needle, catching truncated or corrupted data files during that check (`4.40`).
- Recent shell updates add group-management commands and make `s3.user.provision` idempotent for existing users by attaching policy instead of failing the whole flow.
- When scripting `weed shell`, prompt suppression on piped input reduces brittle non-interactive automation.
- The `4.24`-`4.25` line is operationally important for erasure coding on multi-disk servers: the planner now treats `(server, disk_id)` distinctly, stale shards are pruned more safely, and same-server multi-disk EC reads/recovery are fixed.
- The `4.26`-`4.28` line extends that EC story: execution plans now keep explicit `disk_id` attribution, lost `.ecx` / `.vif` metadata can be reconstructed from local shards, and zero-sized volumes are no longer skipped by scrub/fsck workflows.
- The `4.29`-`4.30` line moves EC encode/repair to shared `ecbalancer.Place` placement and snapshots placement once per detection cycle, which matters for large topologies that previously timed out. It also improves credible-replica metrics, removes empty stub replicas before distributing EC shards, preserves `.vif` metadata when a coexisting regular volume is deleted, and re-notifies writable volumes after worker vacuum.
- `volume.fsck` no longer halts purge on a stuck read-only volume, and `volume.merge` verifies output before overwriting replicas. Keep those checks in repair runbooks instead of bypassing shell safety.
- Revalidate admin scripts after `4.24`: several volume/admin RPCs and destructive operations now require admin auth.
- The `4.40` line adds `ec.check.replication` for verifying EC shard replication counts across the cluster, stops `ec.encode` from rebalancing against a topology snapshot that predates its own newly created shards, and removes stale `.ecsum` checksum sidecar files when a shard is destroyed, with Go and Rust cleanup now aligned. It also makes `volume.tier.upload` preserve existing volume replicas instead of leaving them orphaned after tiering, adds `-resurrectMissingNeedles` to `volume.check.disk` for restoring missing needles on replicas that were never vacuumed, and surfaces the current cluster lock holder in `weed shell` plus S3 servers in `cluster.ps` output, which helps diagnose a maintenance job stuck waiting on a lock.

### Gotchas / prohibitions

- Do not run invasive volume operations without a lock.
- Do not skip the diagnostic commands when chunk loss symptoms appear; the shell gives the actual repair workflow.
- Do not treat `4.23` as a safe stop on multi-disk EC deployments; upstream explicitly calls out the `4.24` / `4.25` line as the safe upgrade path there.

### How to apply in a real repo

- Build runbooks around `weed shell` commands instead of bespoke one-off admin scripts where practical.
- Keep copy-pastable repair sequences for under-replication, missing chunks, and remote-storage sync tasks.

## Admin, worker, and EC notes (4.41 -> 4.45)

- **Throughput limits (`4.42`)**: replicate, EC-shard, and worker-driven volume moves now honor throughput limits; configure them where background moves must not saturate the network or disks.
- **EC interrupted-operation cleanup (`4.41`/`4.42`)**: `ec.encode` rolls back a failed encode instead of leaving read-only volumes and orphan shards, and requires shards to agree on size before deleting the source volume; `ec.decode` finishes the cleanup an interrupted decode left behind and verifies the rebuilt `.dat` before shards can be deleted. The EC worker clears stale/interrupted shards at task start and on failure, confirms a surviving copy before deleting a duplicate shard, and handles zero-sized shard files uniformly across moves, rebuilds, and startup cleanup. `ec.balance` gains a `-volumeIds` filter. A lifecycle chaos harness exercises these paths, so upgrade-then-chaos-test EC clusters.
- **EC decode locality (`4.41`)**: decode reads shards with the encode-time block layout, fixes index locality under `-dir.idx`, and can stage a decoded volume onto a clean peer, skipping any disk that already holds shards and scanning on-disk EC shards when staging.
- **`ec.check.replication` and encode safety (`4.41`)**: EC encode counts shards wherever they landed before deleting the source, names the shard ids an aborted deletion found, and EC scrubbing lists shards for needles that fail scrubs in the result output; `4.45` refunds the cleared leftover shards' slots in the encode source health check.
- **Lance catalog and plugin workers (`4.43`/`4.45`)**: a Lance catalog (with S3 Tables maintained through it) and a Rust plugin worker to maintain it ship in `4.43`; `4.45` ships the Rust maintenance worker with the release and installs it via `install.sh`. The `seaweed-worker` serves health, readiness, and metrics endpoints, and worker metrics graph the plugin-runtime workers (`4.45` counts them in worker metrics).
- **Admin UI (`4.42`/`4.44`/`4.45`)**: the dashboard counts chunks (not files), shows capacity per storage tier, and stops counting remote-tiered bytes as local disk usage; bucket lifecycle rules are editable in the admin UI, the maintenance scanner no longer pins itself to one scan per second after a transient failure, and a persisted or `admin.toml` `maintenance.enabled=false` is honored. The admin UI also gains a visual IAM policy editor and bucket-policy management (see `references/s3-gateway.md`).
- **Volume server (`4.42`/`4.44`)**: leveldb corruption detection in offset loading is fixed, needle counts fit in `uint32`, volume strings are interned to cut memory at high volume counts, and read-only volumes that no longer exist stop being reported. `volume.merge` previously could corrupt every needle it copied; ensure the fix is present before relying on merge in place.
- **Shell (`4.42`)**: `volume.delete`/`volume.move` accept a `-timeout`, `volume.move` cleans up when aborted after the copy phase, the source stays read-only when an incomplete target copy cannot be deleted, `fs.mergeVolumes` and `volume.mark` gain multi-target/`-readonlyCanDelete` support, and volume balance moves parallelize.
