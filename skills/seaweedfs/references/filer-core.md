# Filer Core

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Filer-Setup
- https://github.com/seaweedfs/seaweedfs/wiki/Directories-and-Files
- https://github.com/seaweedfs/seaweedfs/wiki/File-Operations-Quick-Reference
- https://github.com/seaweedfs/seaweedfs/wiki/Data-Structure-for-Large-Files
- https://github.com/seaweedfs/seaweedfs/wiki/Filer-Data-Encryption
- https://github.com/seaweedfs/seaweedfs/wiki/Filer-Commands-and-Operations
- https://github.com/seaweedfs/seaweedfs/wiki/Filer-JWT-Use
- https://github.com/seaweedfs/seaweedfs/wiki/TUS-Resumable-Uploads

## Filer Setup

### What this page is about

- It shows where `filer.toml` can live and how to scaffold it.
- It is a minimal entry point rather than a full deployment guide.

### Actionable takeaways

- Keep `filer.toml` in the working directory, `$HOME/.seaweedfs/`, or `/etc/seaweedfs/` so filer starts with an explicit metadata-store configuration.
- Generate the current sample config with `weed scaffold -config=filer -output=.` instead of inventing filer store keys by hand.
- Use the scaffold output as the authoritative starting point before selecting or disabling stores.

### Gotchas / prohibitions

- Do not launch filer in production without reviewing the generated default store choice.
- Do not maintain hand-written stale config examples when `weed scaffold` can emit the current schema.

### How to apply in a real repo

- Keep a generated filer config template under configuration management and annotate only the settings that differ from defaults.
- Treat filer config generation as part of bootstrap docs and CI smoke tests.

## Directories and Files

### What this page is about

- It explains the filer path model, read/write flow, metadata-store complexity, and scaling behavior.
- It shows how filer combines path-oriented operations with chunk storage on volume servers.
- It clarifies the difference between filer-heavy HTTP/S3 workloads and mount-based workloads.

### Actionable takeaways

- Use filer when applications need directories, path listing, rename semantics, or filesystem-compatible access.
- Expect filer reads to resolve metadata first and then fetch content from volume servers.
- Expect filer writes to stream through filer, chunk large files, and then persist chunk metadata to the filer store.
- Choose the filer metadata store based on lookup/listing scale requirements; the page explicitly frames filer scalability around the backing store.
- Remember that file rename is metadata-only, while directory rename is proportional to the number of nested entries.
- Scale out multiple filer instances when HTTP or S3 traffic makes filer part of the content data path.
- Expect lower filer load when using `weed mount`, because content IO goes directly between mount clients and volume servers.

### Gotchas / prohibitions

- Do not assume directory rename is cheap on very large trees.
- Do not evaluate filer scalability without considering the behavior and limits of the selected metadata store.
- Do not size filer instances the same way for mount-only and HTTP/S3-heavy workloads; the traffic profile is different.

### How to apply in a real repo

- Map workload types to filer scaling plans: metadata-only mount traffic versus full content proxy traffic.
- Document rename cost expectations for large directory trees.
- Keep example flows for HTTP upload/download and paginated listing in operator references and integration tests.

## File Operations Quick Reference

### What this page is about

- It condenses common filer HTTP operations for upload, download, delete, move, copy, listing, and metadata.
- It serves as a quick operator and integration cheat sheet rather than a deeper protocol explanation.

### Actionable takeaways

- Use PUT for simple direct uploads and POST multipart uploads when the client or tooling already supports that form.
- Use recursive DELETE carefully for directory cleanup workflows.
- Treat `mv.from` as the fast path for rename/relocation and `cp.from` as the safe path for duplication or backup-before-change workflows.
- Use JSON directory listing with pagination for automation instead of scraping the HTML directory view.
- Use custom `Seaweed-*` headers and TTL query parameters only when the application contract actually needs them.

### Gotchas / prohibitions

- Do not mistake the quick-reference TTL example for the broader TTL volume-planning guidance; retention still affects storage pools and capacity.
- Do not reorganize large trees heavily without remembering directory moves are not the same cost profile as file moves.

### How to apply in a real repo

- Keep these operations in smoke tests and runbooks so operators can validate filer behavior quickly.
- Document when teams should prefer copy over move, especially for rollback-sensitive workflows.

## Data Structure for Large Files

### What this page is about

- It explains how SeaweedFS chunks large files and when manifest chunks are introduced to cap metadata growth.
- It distinguishes small files, medium files, and super-large files by metadata behavior rather than by a single hard size limit.

### Actionable takeaways

- Treat chunk size as a tuning parameter that affects both metadata volume and IO behavior.
- Expect medium-size large files to store chunk references directly in filer metadata along with per-chunk details such as offset, size, compression, and encryption markers.
- Expect very large files to switch to manifest chunks so the filer store does not need to hold an ever-growing flat list of chunk descriptors.
- Use larger chunk sizes when metadata scale becomes a concern for huge-file workloads, while balancing read/write behavior.
- Keep in mind that the practical size ceiling is driven by metadata design and access predictability, not only raw storage space.

### Gotchas / prohibitions

- Do not design huge-file workloads as if filer metadata cost were constant regardless of chunk count.
- Do not assume recursive manifest indirection exists by default for arbitrarily deep large-file trees.

### How to apply in a real repo

- Document chosen chunk-size defaults for each workload class.
- Include manifest-chunk behavior in large-file architecture reviews so metadata-store sizing stays realistic.

## Filer Data Encryption

### What this page is about

- It explains file-content encryption for data written through filer while metadata remains in the filer store.
- It positions encryption as protection for data stored on volume servers and potentially in cloud tiers.

### Actionable takeaways

- Use `weed filer -encryptVolumeData` when the threat model includes compromised volume servers or remote storage tiers.
- Expect SeaweedFS to generate a random `AES256-GCM` key per file chunk during writes.
- Protect the filer store aggressively because it holds the metadata needed to recover per-chunk encryption keys.
- Treat encrypted chunk storage as a useful control for cloud-tier or untrusted-storage placements.
- Remember that deleting the relevant metadata effectively renders encrypted chunk data unreadable, which can help with data-forgetting workflows.

### Gotchas / prohibitions

- Do not enable filer data encryption and then treat the filer store as low-sensitivity infrastructure.
- Do not assume volume servers themselves manage or understand plaintext encryption context; the protection boundary is above them.

### How to apply in a real repo

- Pair `-encryptVolumeData` with strict filer-store access control and backup policy.
- Document clearly which paths write through filer and therefore benefit from this encryption model.

## Filer Commands and Operations

### What this page is about

- It documents CLI and API-side copy workflows around filer.
- It distinguishes local-to-filer bulk copy from filer-internal file duplication.

### Actionable takeaways

- Use `weed filer.copy` for efficient local filesystem to filer ingestion because data goes straight to volume servers and filer only registers metadata.
- Use filer HTTP `cp.from` for server-side copies within the filer namespace when you want to avoid download/re-upload cycles.
- Use gRPC `CreateEntry()`-style registration patterns only when building custom ingestion or integration tooling that needs direct filer metadata registration.
- Prefer `weed filer.copy` when directory trees from local disk need to be preserved into filer paths automatically.

### Gotchas / prohibitions

- Do not assume filer-internal copy shares chunks; the docs describe independent chunk copies.
- Do not funnel large local imports through naive client-side GET+POST workflows when `weed filer.copy` exists.

### How to apply in a real repo

- Document separate ingestion paths for local bulk import and in-cluster duplication.
- Keep `weed filer.copy` in operational migration and bootstrap playbooks.

## Filer JWT Use

### What this page is about

- It explains how filer accepts JWTs and where token generation must happen.
- It is a narrow usage note that complements the broader security documentation.

### Actionable takeaways

- Generate filer JWTs in an external trusted service using the same signing key and timeout settings configured in `security.toml`.
- Send filer JWTs through one of three supported channels: `Authorization: Bearer`, `jwt=` query parameter, or the HTTP-only `AT` cookie.
- Keep token issuance and expiry aligned with filer-side configuration so apparently valid tokens do not fail due to mismatched TTL assumptions.

### Gotchas / prohibitions

- Do not expect filer itself to mint JWTs for clients.
- Do not leave token transport ambiguous; standardize one delivery mode per application surface where possible.

### How to apply in a real repo

- Put filer JWT issuance behind the same identity boundary that already manages application auth.
- Prefer header or cookie transport for browser and API clients unless query-string usage is unavoidable.

## TUS Resumable Uploads

### What this page is about

- It documents SeaweedFS support for the TUS resumable-upload protocol on filer.
- It covers endpoint layout, enable/disable flags, supported protocol extensions, and example client flows.

### Actionable takeaways

- Use the default `/.tus` endpoint when applications need resumable uploads over unstable networks.
- Customize or disable the endpoint with `-tusBasePath` on `weed filer` or `-filer.tusBasePath` on `weed server`.
- Expect support for `creation`, `creation-with-upload`, and `termination`, but not concatenation.
- Standardize clients on TUS `1.0.0` headers and offset-based resume flows.
- Validate upload-size and session-expiration limits against application expectations; the page lists a `5GB` default max size and temporary session retention.

### Gotchas / prohibitions

- Do not expose TUS paths without the same auth and path-governance review applied to normal filer uploads.
- Do not assume multi-file concatenation support exists.
- Do not forget to test resume behavior through proxies and load balancers if uploads span long durations.

### How to apply in a real repo

- Offer TUS as the preferred upload path for browser and mobile workloads that need resumability.
- Keep direct TUS capability checks, resume tests, and cancellation tests in integration coverage.
