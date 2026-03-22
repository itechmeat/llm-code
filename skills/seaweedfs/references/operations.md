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

### Gotchas / prohibitions

- Do not run invasive volume operations without a lock.
- Do not skip the diagnostic commands when chunk loss symptoms appear; the shell gives the actual repair workflow.

### How to apply in a real repo

- Build runbooks around `weed shell` commands instead of bespoke one-off admin scripts where practical.
- Keep copy-pastable repair sequences for under-replication, missing chunks, and remote-storage sync tasks.
