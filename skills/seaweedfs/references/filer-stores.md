# Filer Stores

Sources:

- https://github.com/seaweedfs/seaweedfs/wiki/Filer-Stores
- https://github.com/seaweedfs/seaweedfs/wiki/Filer-Cassandra-Setup
- https://github.com/seaweedfs/seaweedfs/wiki/Filer-Redis-Setup
- https://github.com/seaweedfs/seaweedfs/wiki/Super-Large-Directories
- https://github.com/seaweedfs/seaweedfs/wiki/Path-Specific-Filer-Store
- https://github.com/seaweedfs/seaweedfs/wiki/Choosing-a-Filer-Store
- https://github.com/seaweedfs/seaweedfs/wiki/Customize-Filer-Store

## Filer Stores

### What this page is about

- It compares available filer metadata backends by lookup behavior, directory scaling, rename characteristics, TTL support, and operational notes.
- It also describes the save/load path for migrating metadata between stores.

### Actionable takeaways

- Treat filer store choice as an architecture decision that defines metadata HA, scaling, rename behavior, TTL support, and operational tooling.
- Start with the comparison table to narrow stores by required properties such as distributed HA, atomic renames, fast bucket deletion, or bucket-per-store isolation.
- Use `fs.meta.save` and `fs.meta.load` from `weed shell` when migrating filer metadata between stores.
- Stop writes or otherwise freeze metadata changes during save/load migrations so exported metadata stays consistent.
- Be conservative with concurrent metadata loads because the page warns that some stores, such as Redis, may not tolerate that path well.
- Treat `memory` as testing only and local embedded stores as operationally different from distributed stores even if performance looks attractive.

### Gotchas / prohibitions

- Do not switch stores in place without an explicit metadata export/import plan.
- Do not choose a store only by raw lookup speed; directory scale, rename semantics, HA, and deletion behavior matter too.
- Do not enable concurrent metadata loads blindly across all backends.

### How to apply in a real repo

- Record approved filer stores with the reasons they fit each deployment class.
- Add a migration runbook for `fs.meta.save`/`fs.meta.load`, including write freeze and validation steps.

## Postgres / PgBouncer note (4.20)

- Postgres-backed filer deployments using PgBouncer should revalidate simple-protocol compatibility after upgrading to 4.20, because the upstream fix moved to the `pgx v5` API path for that mode.

## Filer Cassandra Setup

### What this page is about

- It shows the Cassandra schema and minimal filer configuration for a Cassandra-backed metadata store.
- It positions Cassandra as one example of using an existing distributed datastore for filer metadata.

### Actionable takeaways

- Create the keyspace and `filemeta` table before starting filer against Cassandra.
- Increase Cassandra replication appropriately for production instead of keeping the one-node example.
- Use the `cassandra2` section in `filer.toml` with explicit hosts and keyspace settings.
- Keep filer startup simple once the schema and config are in place; the complexity is mostly in datastore provisioning.

### Gotchas / prohibitions

- Do not use the sample `replication_factor=1` outside single-node testing.
- Do not start filer against Cassandra before the keyspace and table exist.

### How to apply in a real repo

- Ship Cassandra schema creation as part of infrastructure provisioning, not as a manual post-step.
- Keep the chosen keyspace and host list under configuration management.

## Filer Redis Setup

### What this page is about

- It compares the `redis2` and `redis3` metadata-store implementations.
- It focuses on how Redis stores directory listings and why very large directories need a different structure.

### Actionable takeaways

- Use `redis2` when Redis speed is attractive and most directories stay within roughly hundreds of thousands to low millions of entries.
- Understand that `redis2` stores a directory's child names in one sorted set, which is simple and fast for many common cases.
- Use `redis3` when directories can grow into tens of millions or billions of entries, because it spreads names across skip-list-indexed sorted sets.
- Expect `redis3` writes and updates to cost extra Redis operations compared with `redis2`.
- Remember that simple file reads remain efficient because they do not need to scan sibling names.

### Gotchas / prohibitions

- Do not choose `redis2` blindly for extreme single-directory fanout.
- Do not assume Redis directory-list design is free; very large directory support trades some write/update simplicity for scale.

### How to apply in a real repo

- Match `redis2` versus `redis3` to directory cardinality, not only to latency preference.
- Document the loss or cost of directory-list behavior clearly if super-large directories are part of the workload design.

## Super Large Directories

### What this page is about

- It explains how SeaweedFS keeps metadata scalable for directories with enormous direct-child counts.
- It covers the Cassandra and Redis strategies and the operational sacrifices required.

### Actionable takeaways

- Use `superLargeDirectories` only when direct-child counts are so high that the normal partitioning or directory-list structure becomes a bottleneck.
- Expect SeaweedFS to sacrifice direct listing of that configured directory in exchange for better distribution of metadata load.
- In Cassandra, large directories switch to a `full_path`-based partitioning strategy to spread entries across nodes.
- In Redis, SeaweedFS simply stops maintaining the full child-name list for the configured directory.
- Remember that deeper subdirectories under the large root can still be listed normally even if the top-level super-large directory itself cannot.
- Configure super-large directories before data lands there, while the target folder is still empty.

### Gotchas / prohibitions

- Do not enable `superLargeDirectories` if directory listing for that exact folder is still a hard requirement.
- Do not expect metadata import/export to work for the configured large root directory.
- Do not change or remove configured `superLargeDirectories` entries casually; the page warns this can lead to data loss.

### How to apply in a real repo

- Reserve this feature for identity-style namespaces such as users, UUIDs, IPs, or URL-based buckets where direct listing is already unnecessary.
- Document the irreversible nature and listing loss in architecture decisions before enabling it.

## Path-Specific Filer Store

### What this page is about

- It explains how different filer stores can be assigned to different path prefixes.
- It positions path-specific routing as a scaling and isolation mechanism for metadata workloads.

### Actionable takeaways

- Use path-specific stores when one metadata backend cannot serve all paths equally well because of consistency, tombstone, scale, or noisy-neighbor concerns.
- Configure path-specific stores by adding a named store section, setting `location`, and enabling it.
- Expect SeaweedFS to match incoming paths efficiently against configured locations and route metadata operations to the matched store.
- Understand that stored paths are trimmed relative to the configured location prefix, which makes the metadata portable across future mount points or filer instances.
- Use this feature for new directories or new updates only.

### Gotchas / prohibitions

- Do not apply a path-specific store to existing directories and expect old metadata to remain visible automatically; the page warns old data becomes effectively lost or invisible.
- Do not reuse identical config blocks carelessly when several path-specific stores use the same backend type.

### How to apply in a real repo

- Use path-specific routing to isolate hot prefixes, tenant-specific metadata, or special-consistency domains.
- Document which prefixes are backed by which stores and why, including migration constraints for existing data.

## Choosing a Filer Store

### What this page is about

- It adds workload-based guidance for choosing between Cassandra/Scylla-style stores and alternatives such as Redis.
- The concrete example focuses on update-heavy directories and tombstone buildup.

### Actionable takeaways

- Be wary of LSM-tree tombstone buildup in directories with very high churn.
- Consider Redis plus path-specific routing for hot staging folders or other prefixes that receive constant updates and deletions.
- Keep Cassandra or ScyllaDB attractive for distributed scale and native TTL, but not as a universal answer for every metadata hotspot.

### Gotchas / prohibitions

- Do not choose a filer store once and assume every path in the namespace has the same workload profile.
- Do not ignore high-churn directory tombstones when diagnosing slower metadata reads.

### How to apply in a real repo

- Profile metadata hot spots by path and switch only the problematic prefixes to a better-fitting store when needed.
- Treat store selection as workload-specific, not purely vendor- or feature-driven.

## Customize Filer Store

### What this page is about

- It documents the extension points required to add a new filer metadata backend to SeaweedFS itself.
- It highlights the `FilerStore` interface, registration, and server import wiring.

### Actionable takeaways

- Implement the full `FilerStore` interface if you need a custom metadata backend integrated directly into SeaweedFS.
- Include transactional methods and key-value helpers, not only basic entry CRUD, because the interface covers more than simple path lookups.
- Register the store in the supported-store list and ensure the filer server imports it so the backend becomes loadable.
- Treat a custom store as product-level integration work, not just external configuration.

### Gotchas / prohibitions

- Do not implement a partial backend that omits transaction, directory-listing, or KV methods expected by the filer.
- Do not forget the registration/import steps or the store will compile but never activate.

### How to apply in a real repo

- Prefer existing built-in stores unless a genuine missing backend or compliance requirement justifies code-level extension.
- If a custom store is necessary, keep the implementation and validation in the SeaweedFS fork or contribution workflow, not only in deployment docs.
