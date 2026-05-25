---
name: seaweedfs
description: "SeaweedFS distributed storage. Covers filer, S3 API, replication, cloud tiers, and operations. Use when deploying SeaweedFS, configuring filer stores, exposing S3-compatible endpoints, or planning backup and security controls. Keywords: SeaweedFS, weed, filer, S3, object storage."
metadata:
  version: "4.28"
  release_date: "2026-05-22"
---

# SeaweedFS

This skill is a practical router for deploying and operating SeaweedFS from the upstream repository and wiki.

Prefer production guidance from multi-component setups over `weed mini` shortcuts.

## Quick Navigation

| Situation                                             | Open                                                               |
| ----------------------------------------------------- | ------------------------------------------------------------------ |
| Learn the system shape and bootstrap paths            | `references/getting-started.md`                                    |
| Stand up a local all-in-one sandbox                   | `references/quick-start-mini.md`                                   |
| Review control-plane, volume, and collection topology | `references/topology-and-setup.md`                                 |
| Check master, volume, filer, and client API surfaces  | `references/api-surfaces.md`                                       |
| Set replication, TTL, failover masters, and env vars  | `references/configuration.md`                                      |
| Work with performance notes, FAQ topics, and examples | `references/benchmarks-and-use-cases.md`                           |
| Work with filer metadata, uploads, JWT, and TUS       | `references/filer-core.md`                                         |
| Choose and scale filer metadata stores                | `references/filer-stores.md`                                       |
| Operate S3 buckets, auth, and IAM/OIDC                | `references/s3-gateway.md`                                         |
| Plan Cloud Drive and remote storage mounts            | `references/cloud-drive.md`                                        |
| Run backups, metrics, repairs, and shell workflows    | `references/backup-and-replication.md`, `references/operations.md` |
| Choose S3 encryption and client tooling               | `references/encryption.md`, `references/s3-client-tools.md`        |
| Review transport, JWT, TLS, and exposure controls     | `references/security.md`                                           |

## When to Use

- Planning a SeaweedFS deployment
- Running `weed` components in development or production
- Designing filer, S3, or cloud-tier topologies
- Choosing metadata stores and replication patterns
- Hardening SeaweedFS for public or multi-tenant use
- Operating backups, metrics, and cluster repair workflows

## Core Mental Model

- SeaweedFS separates volume management from file and object access paths.
- The filer layer adds directories, metadata stores, and higher-level protocols.
- S3, WebDAV, FUSE, and other interfaces are front doors on top of the same storage services.
- Production deployments should document topology, credentials, persistence, monitoring, and recovery paths explicitly.

## Release Highlights (4.25)

- **Security/admin path**: `4.24`-`4.25` tightens admin auth on destructive/admin endpoints and fixes Admin UI behavior under `security.toml` by attaching admin-signed auth on filer IAM gRPC calls.
- **Erasure coding / multi-disk ops**: the release line fixes several EC planner/recovery cases across multi-disk and cross-server layouts, including stale-shard cleanup and safer source-volume deletion.
- **S3/IAM hardening**: IAM users without policies are now denied instead of implicitly over-permitted, while OIDC/web-identity and audit surfaces continue to mature.

## Release Highlights (4.26 -> 4.28)

- **Erasure coding / multi-disk ops**: EC planning now packs shards across disks more reliably, includes `disk_id` in execution planning, and can rebuild lost `.ecx` / `.vif` metadata from local shards during recovery.
- **Integrity checks**: scrubbing/fsck paths now account for zero-sized volumes instead of silently skipping them, which matters for sparse or recently created topologies.
- **Filer backend reliability**: Redis3 avoids a skiplist-end panic path, and SQL-based filer stores no longer force-disable idle connection pooling.
- **S3 audit trail**: requester identity is populated more consistently for GET/HEAD/IAM operations, improving compliance and incident triage.
- **HA heartbeat path**: masters now accept volume-server ping targets on follower replicas, which improves failover visibility in multi-master deployments.

## Release Highlights (4.20)

- **S3/IAM**: embedded IAM flows gained `ListUserPolicies`, group inline policy actions, safer user-policy round trips, and bucket-scoped cleanup on `DeleteBucket`.
- **Mount/FUSE**: `weed mount` adds `-dlm` for cross-mount write coordination and improves POSIX metadata behavior, `nlink` accounting, and filer RPC efficiency.
- **Master placement**: volume assignment is more size-aware, readonly transitions drain pending size first, and a topology bug that could cause endless growth in some DC/rack layouts was fixed.
- **Filer reliability**: PgBouncer/Postgres compatibility improved, graceful shutdown corruption was fixed, and redundant filer disk reads that caused memory/CPU regressions were removed.
- **Ops surfaces**: `weed shell` gained group-management helpers, S3 user provisioning handles existing users more safely, and master/volume now export `start_time_seconds` metrics.

## Prohibitions

- Do not use `weed mini` for production.
- Do not treat single-binary defaults as production-safe configuration.
- Do not expose S3 or filer endpoints publicly before reviewing auth, TLS, and network boundaries.
- Do not choose a filer store without validating HA, scaling, and backup properties.
- Do not design backup or replication flows without restore validation.

## Links

- [Documentation](https://github.com/seaweedfs/seaweedfs/wiki/Getting-Started)
- [Releases](https://github.com/seaweedfs/seaweedfs/releases)
- [GitHub](https://github.com/seaweedfs/seaweedfs)
- [Docker Hub](https://hub.docker.com/r/chrislusf/seaweedfs)
- [Docker Hub](https://hub.docker.com/r/chrislusf/seaweedfs)
