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
- Use `volume.check.disk`, `volume.fsck`, `fs.meta.cat`, and `fs.verify` when diagnosing missing chunks or filer-to-volume inconsistencies.
- Recent shell updates add group-management commands and make `s3.user.provision` idempotent for existing users by attaching policy instead of failing the whole flow.
- When scripting `weed shell`, prompt suppression on piped input reduces brittle non-interactive automation.
- The `4.24`-`4.25` line is operationally important for erasure coding on multi-disk servers: the planner now treats `(server, disk_id)` distinctly, stale shards are pruned more safely, and same-server multi-disk EC reads/recovery are fixed.
- The `4.26`-`4.28` line extends that EC story: execution plans now keep explicit `disk_id` attribution, lost `.ecx` / `.vif` metadata can be reconstructed from local shards, and zero-sized volumes are no longer skipped by scrub/fsck workflows.
- The `4.29`-`4.30` line moves EC encode/repair to shared `ecbalancer.Place` placement and snapshots placement once per detection cycle, which matters for large topologies that previously timed out. It also improves credible-replica metrics, removes empty stub replicas before distributing EC shards, preserves `.vif` metadata when a coexisting regular volume is deleted, and re-notifies writable volumes after worker vacuum.
- `volume.fsck` no longer halts purge on a stuck read-only volume, and `volume.merge` verifies output before overwriting replicas. Keep those checks in repair runbooks instead of bypassing shell safety.
- Revalidate admin scripts after `4.24`: several volume/admin RPCs and destructive operations now require admin auth.

### Gotchas / prohibitions

- Do not run invasive volume operations without a lock.
- Do not skip the diagnostic commands when chunk loss symptoms appear; the shell gives the actual repair workflow.
- Do not treat `4.23` as a safe stop on multi-disk EC deployments; upstream explicitly calls out the `4.24` / `4.25` line as the safe upgrade path there.

### How to apply in a real repo

- Build runbooks around `weed shell` commands instead of bespoke one-off admin scripts where practical.
- Keep copy-pastable repair sequences for under-replication, missing chunks, and remote-storage sync tasks.
