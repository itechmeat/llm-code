# Benchmarks and Use Cases

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Benchmarks
- https://github.com/seaweedfs/seaweedfs/wiki/FAQ
- https://github.com/seaweedfs/seaweedfs/wiki/Applications

## Benchmarks

### What this page is about

- It explains what the built-in `weed benchmark` command measures and why benchmark numbers are highly dependent on topology and hardware.
- It provides a simple single-machine setup and describes the default benchmark workload.
- It frames benchmark output as a workload-specific data point rather than an absolute product claim.

### Actionable takeaways

- Use `weed benchmark` mainly as a repeatable comparative test for your own environment, not as proof of universal performance.
- Prefer multi-machine tests when evaluating a distributed deployment, because single-host benchmarks hide network and placement costs.
- Understand the default workload before reading the numbers: the built-in benchmark writes and then randomly reads roughly one million `1KB` files.
- Treat the default benchmark as a small-object, operations-per-second stress test because each file involves id assignment plus upload and later random read lookup.
- Change benchmark parameters when you need throughput-oriented validation for larger objects instead of tiny-file request rates.
- Inspect `weed benchmark -h` and record the exact flags used so benchmark runs are reproducible across hardware changes and release upgrades.

### Gotchas / prohibitions

- Do not quote the wiki's sample numbers as generally applicable production capacity.
- Do not benchmark a multi-node design on one machine and assume the result predicts cluster behavior.
- Do not compare results across environments unless file size, concurrency, hardware, and deployment topology are all documented.

### How to apply in a real repo

- Add a benchmark protocol that records topology, disk class, CPU, network shape, SeaweedFS version, and benchmark flags.
- Run at least two benchmark profiles: small-object IOPS and larger-object throughput.
- Keep benchmark output next to ops notes so performance claims stay tied to the tested environment.

## FAQ

### What this page is about

- It answers recurring operator questions around volume sizing, disk types, preallocation, data safety, large-file behavior, memory usage, and gRPC addressing.
- It clarifies the difference between SeaweedFS volumes and physical disks.
- It captures several practical failure patterns that commonly show up during early production adoption.

### Actionable takeaways

- Plan for many SeaweedFS volumes; replication, TTL, collection, disk type, and S3 bucket isolation all consume distinct volume pools.
- If you hit `no free volumes left`, first revisit `-volumeSizeLimitMB` on master and `-max` on volume servers rather than treating it as a generic capacity bug.
- Leave disk type empty on homogeneous all-SSD clusters unless you have a specific path-based policy reason to tag disks differently.
- Pre-create extra writable volumes with the master `vol/grow` endpoint when new collections, buckets, or replica classes are about to come online.
- Treat the master and volume web UIs as quick health surfaces, but not as substitutes for explicit monitoring and runbooks.
- Use filer-based HTTP access, gRPC APIs, or generated bindings according to the interface your application actually needs; the FAQ does not push one client language ecosystem.
- Count safety features in layers: CRC/Etag validation, replication or erasure coding, optional filer encryption, TLS, JWT, and S3 access control.
- Size chunking for large files deliberately because metadata growth is linear with chunk count; larger chunks reduce metadata pressure.
- Keep extra free disk space for compaction, especially when configuring many volumes on a server.
- Reduce memory pressure on older small-file-heavy volumes by moving suitable cold data into erasure-coded read-only form.
- Use `_large_disk` builds only when you need volumes above `30GB`, and treat them as a cluster-wide compatibility boundary.
- Expect deleted space to remain allocated until vacuum runs; schedule `weed shell` maintenance instead of assuming immediate reclaim.
- When overriding gRPC ports, propagate the `<host>:<httpPort>.<grpcPort>` form consistently to all dependent commands.
- For IPv6, set `-ip.bind` with the interface scope when using link-local addresses.

### Gotchas / prohibitions

- Do not equate a SeaweedFS volume with a physical disk; the system expects many volumes per environment.
- Do not mix standard and `_large_disk` binaries inside one cluster.
- Do not over-provision total volume capacity beyond real disk headroom, or compaction and growth will fail at the worst time.
- Do not expect deletions to free disk immediately without vacuum.
- Do not override gRPC ports on one component and forget to update all the clients that reference it.

### How to apply in a real repo

- Put volume-capacity math, `vol/grow` procedures, vacuum policy, and `_large_disk` compatibility rules into the operator guide.
- Treat disk-type naming and path-specific filer config as reviewed configuration, especially on SSD-only clusters.
- Capture large-file chunk sizing and memory tradeoffs in workload-specific architecture notes.
- Add a troubleshooting section for custom gRPC ports, IPv6 scope syntax, and mount cleanup after unclean restarts.

## Applications

### What this page is about

- It lists example applications and integrations that already use SeaweedFS.
- It is not a technical integration guide; it mainly shows which access patterns appear in real projects.
- The examples point to filer-backed sync tools, media storage, attachment storage, and Nginx-based processing flows.

### Actionable takeaways

- Expect SeaweedFS to appear behind several application styles: GUI file explorers and sync tools, media ingestion systems, attachment stores, and HTTP backends.
- Treat the filer interface as a common integration surface when applications need filesystem-like semantics rather than raw volume ids.
- Consider SeaweedFS a backend building block rather than a finished end-user product; most examples wrap it in application-specific logic or UI.
- Use this page as evidence that operator documentation should cover both direct application access and reverse-proxy-mediated access paths.

### Gotchas / prohibitions

- Do not treat this page as a compatibility matrix or support policy.
- Do not infer production architecture requirements from the examples alone; they are ecosystem signals, not reference designs.

### How to apply in a real repo

- Include a short "integration surfaces" section that maps application needs to filer HTTP, S3, WebDAV, FUSE, or custom gateways.
- Keep reverse-proxy, media-processing, and sync-client considerations visible in deployment reviews if the workload resembles the listed examples.
