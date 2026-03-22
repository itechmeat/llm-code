---
name: seaweedfs
description: "SeaweedFS distributed storage. Covers filer, S3 API, replication, cloud tiers, and operations. Use when deploying SeaweedFS, configuring filer stores, exposing S3-compatible endpoints, or planning backup and security controls. Keywords: SeaweedFS, weed, filer, S3, object storage."
metadata:
  version: "4.17"
  release_date: "2026-03-11"
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
