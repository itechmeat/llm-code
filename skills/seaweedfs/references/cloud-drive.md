# Cloud Drive and Remote Storage

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Cloud-Drive-Benefits
- https://github.com/seaweedfs/seaweedfs/wiki/Configure-Remote-Storage
- https://github.com/seaweedfs/seaweedfs/wiki/Mount-Remote-Storage
- https://github.com/seaweedfs/seaweedfs/wiki/Cache-Remote-Storage

## Cloud Drive Benefits

### What this page is about

- It distinguishes SeaweedFS Cloud Drive from Cloud Tier and explains why operators use Cloud Drive.
- It frames Cloud Drive as a mounted remote-object namespace with local caching and optional write-back.

### Actionable takeaways

- Use Cloud Drive when you need the cloud provider's object layout to remain directly usable outside SeaweedFS.
- Use Cloud Tier instead when you want SeaweedFS-native volume movement and transparent filer data encryption.
- Expect Cloud Drive to cache remote content locally with effectively unbounded capacity design rather than classic eviction-first proxy caching.
- Use Cloud Drive when workloads need local-latency reads, explicit cache warming/uncaching, and the ability to detach from the cloud later.
- Remember that Cloud Drive can serve multiple access methods on top of remote data once mounted into SeaweedFS.

### Gotchas / prohibitions

- Do not assume Cloud Drive encrypts provider-visible files the way Cloud Tier plus filer encryption can.
- Do not confuse Cloud Drive with a simple proxy; the docs explicitly describe different caching and write-back behavior.

### How to apply in a real repo

- Decide early whether a dataset needs provider-native readability (Cloud Drive) or SeaweedFS-native cold-volume movement (Cloud Tier).
- Document cache warmup, uncache, and write-back policy for each mounted remote dataset.

## Configure Remote Storage

### What this page is about

- It documents how remote cloud backends are registered for Cloud Drive and related remote-storage features.
- It lists supported provider types and the `remote.configure` workflow.

### Actionable takeaways

- Register remote backends first with `remote.configure` before mounting or using them elsewhere in SeaweedFS.
- Use the logical remote name as the stable reference and rotate credentials behind it as needed.
- For S3-compatible providers beyond AWS, be ready to tune endpoint, path-style, and signature-version flags.
- Treat provider-specific auth sources, such as GCS service-account JSON versus ADC, as part of the environment design.
- Use the shell command to inspect current remote configs, update them, or delete stale entries.

### Gotchas / prohibitions

- Do not assume every S3-compatible vendor works with AWS defaults only.
- Do not hardcode credentials into many places when a named remote configuration can centralize them.

### How to apply in a real repo

- Keep one inventory of remote names, provider types, and endpoint quirks.
- Validate provider-specific signature and path-style behavior before production cutover.

## Multipart Transfer Concurrency (4.48)

Multipart transfer concurrency for remote storage and tiered volumes is configurable instead of hard-coded.

- **Per remote storage**: `remote.configure` accepts `-upload_concurrency` and `-download_concurrency`, which are persisted into the remote's `RemoteConf` and honored by the S3 and Azure remote storage clients. Before `4.48` the S3 client uploaded with 1 concurrent part and downloaded with 5.
- **Per S3 backend**: the same keys (`upload_concurrency`, `download_concurrency`) can be set in the backend scaffold configuration in `master.toml`. An empty or invalid value falls back to the backend default rather than failing.
- **Per operation**: the shell tier commands `volume.tier.upload`, `volume.tier.download`, `volume.tier.move` and `volume.tier.evict` accept a `-concurrent` flag that is forwarded through the volume-server gRPC handlers into the backend, so one-off moves can be tuned without reconfiguring the remote.
- `0` or unset always means "backend default", so existing configurations behave identically after the upgrade.

```bash
weed shell -master=localhost:9333
> remote.configure -name=my-s3 -type=s3 -bucket=b -region=r -access_key=k -secret_key=s -upload_concurrency=5 -download_concurrency=10
> volume.tier.move -volumeId=3 -collection=cloud -concurrent=8
```

Why it matters: with a single concurrent upload part, most of the available bandwidth to a high-latency object store goes unused; with too many, the pipe saturates and small parts thrash. Tune per remote, not globally.

## Mount Remote Storage

### What this page is about

- It documents how a configured remote backend is mounted into filer paths and how metadata pull strategies work.
- It covers eager versus lazy metadata loading, listing cache TTL, metadata refresh, and write-back choices.

### Actionable takeaways

- Mount remotes with `remote.mount` after remote configuration is in place, targeting either a whole bucket or a remote subdirectory.
- Choose `eager` metadata pull for small or medium buckets that need instant local listing after mount.
- Choose `lazy` metadata strategy for very large buckets when you want fast mount time and on-demand metadata fetch.
- Use `listingCacheTTL` when you need automatic remote listing refresh without remounting.
- Use `remote.meta.sync` on eager mounts without TTL when remote-side changes must be refreshed locally.
- Use `weed filer.remote.sync` for continuous write-back of local changes to the mounted remote.
- Use `remote.copy.local` for batch or recovery-style synchronization of local-only files.
- Expect `remote.unmount` to drop local metadata and cached file content.

### Gotchas / prohibitions

- Do not choose lazy mode if empty directory listings would confuse users or applications that expect `ls` to work immediately.
- Do not rely on eager metadata forever without refresh if the remote source changes externally.
- Do not assume write-back happens automatically unless `filer.remote.sync` or a batch copy path is actually running.

### How to apply in a real repo

- Define one of four standard mount profiles: eager, eager+TTL, lazy, or lazy+TTL.
- Pair writable mounts with an explicit sync strategy and monitoring for sync lag or failures.

## Cache Remote Storage

### What this page is about

- It documents explicit cache warming and cache eviction for mounted remote paths.
- It focuses on the `remote.cache` and `remote.uncache` shell commands.

### Actionable takeaways

- Use `remote.cache` for proactive warmup instead of waiting for lazy reads.
- Filter caching by directory, name pattern, size, or age so local storage is spent on the files that matter.
- Use `remote.uncache` to reclaim local capacity while keeping metadata and remote source-of-truth intact.
- Schedule both commands regularly when workloads need predictable local residency rules.
- Expect SeaweedFS to skip already synchronized or unsafe-to-uncache files to avoid unnecessary copying or data loss.

### Gotchas / prohibitions

- Do not uncache files that are not yet synchronized to remote.
- Do not assume Cloud Drive caching policy is automatic enough for all workloads; explicit warmup/uncache jobs may still be necessary.

### How to apply in a real repo

- Define cache/uncache cron policies by directory, age, and size class.
- Monitor local-capacity consumption and sync health alongside Cloud Drive usage.
