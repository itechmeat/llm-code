# Configuration

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Replication
- https://github.com/seaweedfs/seaweedfs/wiki/Store-file-with-a-Time-To-Live
- https://github.com/seaweedfs/seaweedfs/wiki/Failover-Master-Server
- https://github.com/seaweedfs/seaweedfs/wiki/Erasure-Coding-for-warm-storage
- https://github.com/seaweedfs/seaweedfs/wiki/Server-Startup-via-Systemd
- https://github.com/seaweedfs/seaweedfs/wiki/Environment-Variables

## Replication

### What this page is about

- It explains SeaweedFS replication as a volume-level placement policy defined by a three-digit string for cross-datacenter, cross-rack, and same-rack copies.
- It clarifies the write-consistency model and the fact that replication repair is manual rather than immediate.
- It adds practical guidance for changing replication and operating through disk failures or topology shifts.

### Actionable takeaways

- Treat replication as a property of volumes and write placement, not of individual file objects in isolation.
- Understand the three digits as additional copies across `data center`, `rack`, and `server` scopes; total copies are `1 + sum(digits)`.
- Use `-defaultReplication` on master or filer to set a sane default and override only when a workload truly needs different durability.
- Size topology labels (`dataCenter`, `rack`) correctly before relying on placement strings, because replication meaning depends on those labels being real.
- Expect SeaweedFS writes to require success on all intended replicas; failed replica creation fails the write.
- Use `volume.fix.replication` from `weed shell` as the explicit repair path for under-replicated readonly volumes.
- Use `volume.fix.replication -doDelete=false` during topology changes when you want to heal missing copies without deleting surplus ones mid-migration.
- After changing a volume's replication with `volume.configure.replication`, expect it to become readonly until repair is completed.
- Pair high replication factors with serious capacity planning; they multiply storage needs quickly.
- Consider erasure coding for warmer data when full replication would be too space-expensive.

### Gotchas / prohibitions

- Do not assume SeaweedFS automatically restores missing replicas during transient failures; the page explicitly says repair is manual.
- Do not configure replication strings that your real topology cannot satisfy.
- Do not change replication policies without a follow-up repair plan and capacity check.
- Do not confuse multiple volume processes on one host with true host-level fault isolation.

### How to apply in a real repo

- Record supported replication strings, the topology they require, and the business reason for each class.
- Make `volume.fix.replication` part of scheduled operations and failure-recovery procedures.
- Review rack and datacenter labels as part of every deployment change, because bad labels silently undermine durability assumptions.

## Store File with a Time To Live

### What this page is about

- It explains SeaweedFS TTL semantics for expiring files and the volume-level design used to reclaim space efficiently.
- It shows how TTL participates both in file-id assignment and in the actual upload.
- It adds deployment guidance for sizing TTL volumes and keeping them operationally separate.

### Actionable takeaways

- Treat TTL as both a placement concern and a file metadata concern: the assign step selects a matching TTL volume and the write step stores the file's own expiry.
- Keep the volume TTL equal to or longer than the per-file TTL when mixing values for operational simplification.
- Expect files to return `404` after expiry even before the underlying expired volume is physically deleted.
- Understand that SeaweedFS reclaims TTL space efficiently by grouping files into TTL-specific volumes and deleting the whole expired volume after it ages out.
- Reduce volume size limits for TTL-heavy workloads when disk space is tight, because active TTL volumes can still grow toward the normal maximum size.
- Use a small set of TTL classes instead of many unique TTL variations to avoid exploding the number of specialized volume pools.
- Consider using S3 lifecycle configuration when TTL behavior is needed through the S3 surface.

### Gotchas / prohibitions

- Do not forget to pass TTL during both id assignment and upload if you want deterministic placement and file expiry behavior.
- Do not mix many TTL variations casually; each distinct TTL creates its own operational pool.
- Do not mix TTL and non-TTL workloads in the same cluster without reviewing shared volume-size constraints.

### How to apply in a real repo

- Define an allowed TTL catalog and map application retention classes to it.
- Treat TTL clusters or pools as separate capacity domains when retention-heavy workloads differ from normal object storage.
- Document the lag between logical expiry and physical volume deletion so support teams understand disk-usage timing.

## Failover Master Server

### What this page is about

- It explains how SeaweedFS master HA works through a Raft-elected leader and follower forwarding.
- It shows bootstrap patterns for running multiple masters together with volume servers.
- It also clarifies the operational limitation around changing the master set later.

### Actionable takeaways

- Use an odd-sized master set such as `3` or `5` when you need control-plane failover.
- Keep the peer list identical across all masters and ensure the `-ip` value matches the hostname/IP used in `-peers`.
- Configure volume servers with as many master endpoints as possible so they can reconnect to another master after leader loss.
- Expect temporary write unavailability for some volumes during leader transition until all volume heartbeats reach the new leader.
- Treat the master set as relatively static infrastructure, similar to a consensus cluster, not something to scale up and down casually.

### Gotchas / prohibitions

- Do not assume master membership can be changed live; the page says adding a new master requires stopping the existing master set and restarting with the new list.
- Do not use inconsistent hostnames or IPs between `-ip` and `-peers`, or the cluster identity will break.
- Do not configure only one master endpoint on volume servers if failover is a requirement.

### How to apply in a real repo

- Treat the master peer list as immutable cluster metadata managed through infrastructure code.
- Add a brief operator note that leader failover can temporarily reduce writable capacity until fresh heartbeats arrive.
- Include master peer-list validation in deployment reviews and cluster bootstrap scripts.

## Erasure Coding for Warm Storage

### What this page is about

- It explains SeaweedFS's `RS(10,4)` erasure coding model for warm or cold data.
- It positions EC as a space-saving alternative to high replica counts while keeping recovery at the whole-volume level.
- It describes the admin/worker plugin flow, detection thresholds, shard balancing, and read-path tradeoffs.

### Actionable takeaways

- Use EC for data that is no longer hot enough to justify in-memory indexes and full-replica overhead.
- Expect the open-source default to be `10+4`, which tolerates up to four lost shards with roughly `1.4x` storage overhead.
- Start the admin service and worker so the `erasure_coding` plugin can detect eligible volumes and perform encoding.
- Tune encoding thresholds deliberately: fullness ratio, quiet period, minimum size, and optional collection filter.
- Keep collections capable of holding both normal writable volumes and erasure-coded warm volumes; new writes still land on normal volumes.
- Run EC balancing so shards spread across disks, servers, and racks instead of accumulating risky concentration.
- Expect an extra network hop for normal EC reads and slower recovery reads when shards are missing.
- Use EC repair when losing shards, but plan for whole-volume data transfer during reconstruction.

### Gotchas / prohibitions

- Do not use EC for workloads that still need frequent updates; the page says deletion is supported but update is not.
- Do not forget that compaction requires converting EC volumes back to normal volumes first.
- Do not enable EC and ignore shard-balancing hygiene; uneven placement can make recovery impossible after a host failure.
- Do not present EC as a write-path optimization; it is a warm-storage cost and memory optimization with read tradeoffs.

### How to apply in a real repo

- Define a warm-data policy that says when volumes transition from replicated writable state into EC-managed storage.
- Pair EC enablement with admin/worker deployment, threshold tuning, and balancing procedures.
- Document the operational difference between normal-volume repair and EC shard repair so recovery expectations stay realistic.

## Server Startup via Systemd

### What this page is about

- It provides sample `systemd` unit files for master, volume, and filer services.
- It highlights mount ordering and startup delays for data directories that depend on separate filesystems.
- It shows a simple pattern rather than a hardened production unit template.

### Actionable takeaways

- Create separate unit files for master, volume, and filer when you want OS-native service management outside containers or Kubernetes.
- Add mount dependencies in `After=` when the SeaweedFS data directory lives on a filesystem that is mounted later in boot.
- Use `ExecStartPre=/bin/sleep ...` only as a simple guard when mount timing is unreliable; prefer explicit mount dependencies where possible.
- Set `WorkingDirectory` intentionally when filer config files such as `filer.toml` are resolved relative to that directory.
- Enable services explicitly so nodes recover after reboots.

### Gotchas / prohibitions

- Do not copy the sample units verbatim into production without replacing IPs, directories, user/group, and service flags.
- Do not rely on arbitrary sleep alone if proper systemd dependencies can model the required storage ordering.
- Do not run everything as `root` unless the environment truly requires it.

### How to apply in a real repo

- Provide hardened systemd units with explicit users, restart policy, mount ordering, and absolute config paths.
- Keep bootstrap templates separate for master, volume, filer, and optional S3/admin/worker processes.
- Document which directories must exist and which config files are expected in the working directory.

## Environment Variables

### What this page is about

- It explains how SeaweedFS command flags and configuration-file keys map to environment variables.
- It covers `WEED_` prefix rules, security-related variables, Docker usage, and filer store configuration through env vars.
- It also highlights store-selection constraints and migration caveats.

### Actionable takeaways

- Use plain uppercase flag names for many command options and `WEED_`-prefixed variables for global logging/config flags and config-file settings.
- Translate dotted config keys to `WEED_` environment variables by replacing dots with underscores.
- Prefer environment variables for secrets such as JWT keys, TLS material, and filer-store credentials when config files live in version control.
- For S3 credentials, follow the dedicated precedence rules and keep environment variables as one supported source rather than the only one.
- Disable `WEED_LEVELDB2_ENABLED` when switching filer metadata to an external store; only one filer store should be enabled.
- Use comma-separated values for array-like settings such as cluster addresses.
- Run `weed scaffold -config=filer` to discover the current set of store configuration keys instead of guessing them.
- Treat environment-based store changes as configuration for new deployments or planned migrations, not in-place metadata migration.

### Gotchas / prohibitions

- Do not enable multiple filer stores at once.
- Do not assume changing environment variables migrates existing filer metadata.
- Do not hardcode secrets in committed `filer.toml` or `security.toml` when env vars can externalize them cleanly.

### How to apply in a real repo

- Publish one env-var naming guide for flags, `WEED_` config keys, and secret injection.
- Keep container examples explicit about disabling `leveldb2` when an external metadata store is chosen.
- Separate immutable non-secret config from secret-bearing env vars in deployment manifests.
