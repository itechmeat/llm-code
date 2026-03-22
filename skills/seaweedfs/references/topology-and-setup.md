# Topology and Setup

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Components
- https://github.com/seaweedfs/seaweedfs/wiki/Production-Setup

## Components

### What this page is about

- It defines the core SeaweedFS services and how they combine into object, file, and S3 access paths.
- It explains the master quorum model, volume responsibilities, and the role of the optional filer and S3 layers.
- It introduces volume and collection concepts that directly affect sizing and bucket design.

### Actionable takeaways

- Treat SeaweedFS as two layers: the core object store (`master` plus `volume`) and the higher-level access layer (`filer`, `s3`, WebDAV, FUSE, and related front doors).
- Run an odd number of master servers so Raft can form a majority; `1` or `3` stable masters are the practical defaults the page emphasizes.
- Keep the master set small and reliable instead of scaling the quorum broadly; more unstable masters weaken the control plane rather than improving it.
- Expect the elected leader to assign file ids, place writes onto volumes, and maintain the authoritative cluster view.
- Plan volume servers around capacity and redundancy at the volume level rather than at the individual object level.
- Use filer when applications need path semantics, directories, or filesystem-like access patterns instead of only object ids.
- Use the S3 service as an optional access layer on top of filer semantics when AWS-compatible buckets are required.
- Model storage growth around volumes, not individual files: a volume is a large container file that packs many smaller objects together.
- Revisit the default volume sizing (`30GB`) and auto-created volume count (`8`) before deploying small-disk or bucket-heavy environments.
- Use collections to separate datasets, lifecycle requirements, or S3 buckets; bucket deletion is fast because it maps to removing the collection's volumes.
- Lower the volume size limit if many collections or buckets would otherwise reserve too much disk headroom.

### Gotchas / prohibitions

- Do not deploy an even number of masters; quorum behavior depends on an odd-sized set.
- Do not assume more masters automatically improve reliability; the page recommends a small stable quorum.
- Do not size capacity per file or per bucket alone; replication and TTL apply per volume.
- Do not forget that each S3 bucket gets its own collection, which can amplify disk planning mistakes when default volume sizes stay large.

### How to apply in a real repo

- Document the topology explicitly: control plane masters, data plane volume servers, metadata plane filer store, and any protocol gateways.
- Include a bucket and collection sizing rule in runbooks so operators evaluate volume size limits before creating many tenants.
- Separate application-facing endpoints by protocol and note which ones depend on filer being present.
- Treat master quorum count, volume size limit, and collection strategy as first-class architecture decisions rather than bootstrap defaults.

## Production Setup

### What this page is about

- It assembles the production deployment from the bottom up: masters, volume servers, filer store, filer, then optional S3 or FUSE access.
- It adds practical port, IP, and multi-disk guidance for single-node and distributed clusters.
- It explains how SeaweedFS expects operators to handle balancing and maintenance in real environments.

### Actionable takeaways

- Build production incrementally: stabilize object storage first, then add filer-backed file services, then add S3, FUSE, metrics, and security.
- Open and document the default service ports explicitly: master `9333/19333`, volume `8080/18080`, filer `8888/18888`, and S3 `8333`.
- Set `-ip` carefully on multi-homed hosts so inter-node communication uses the intended network path.
- If a service should listen on one address but advertise another, combine `-ip` and `-ip.bind` intentionally instead of relying on interface defaults.
- For single-node setups that still need filer and S3, `weed server -filer -s3` is the compact starting point, but volume sizing still needs manual review.
- Reduce `-master.volumeSizeLimitMB` on smaller hosts so one server can keep several writable volumes instead of exhausting space on a few oversized defaults.
- When running multiple masters, define the full `-peers` list consistently on every node and keep the master data directory persistent.
- Add `-metrics.address` in production if Prometheus scraping or push-based metrics collection is part of the environment.
- On volume servers, use `-dataCenter` and `-rack` deliberately because replication placement depends on this topology metadata.
- If one host has several physical disks, either provide a comma-separated `-dir` list with matching `-max` values or run multiple volume servers on different ports.
- Use `-index=leveldb` on very large volume servers to reduce memory pressure from index handling.
- Throttle maintenance impact on hot nodes with `-compactionMBps` rather than letting compaction consume unbounded disk bandwidth.
- Expect new capacity to receive new writes but not automatic rebalance of existing data; manual `weed shell` commands are the explicit maintenance path.
- Generate `filer.toml` with `weed scaffold -config=filer` and choose the filer store according to HA and scale needs instead of accepting `leveldb2` blindly.
- Treat a shared filer store plus multiple peer filer processes as the recommended production model because it makes filers stateless.
- Start S3 alongside filer when possible so the S3 endpoint follows the same filer-backed metadata view and multi-filer setup stays simpler.
- Use `weed mount -volumeServerAccess=filerProxy` when clients sit outside the internal cluster and only filer should be exposed publicly.
- Prefer scheduled balancing and replication repair during off-hours instead of continuous aggressive rebalancing.

### Gotchas / prohibitions

- Do not build a two-master cluster; the page explicitly says two nodes cannot reach consensus safely.
- Do not use multiple `-dir` values on the same physical disk, because the automatic volume accounting will overestimate usable capacity.
- Do not assume replication placement across multiple volume processes on one host equals physical host redundancy.
- Do not rely on the default local filer store when you need multiple filers or shared metadata.
- Do not expect new volume servers to backfill old data automatically; rebalance is manual by design.

### How to apply in a real repo

- Separate deployment recipes into layers: masters, volumes, filer store, filer, S3/FUSE, and maintenance jobs.
- Make network advertisement, rack/datacenter labels, and volume sizing mandatory config inputs in templates.
- Treat filer store selection and shared metadata design as an architecture review item, not a post-deploy tweak.
- Put manual balancing and replication repair into scheduled ops procedures rather than assuming background self-healing.
