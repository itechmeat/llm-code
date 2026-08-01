# PostgreSQL 19

What changed in PostgreSQL 19 compared to 18, plus the full list of incompatible changes to plan for before upgrading.

> **Beta status.** PostgreSQL 19 is currently at **Beta 2 (2026-07-16)**. GA is expected **September/October 2026**, after further betas and release candidates. Behavior, feature details, and APIs may still change before GA — one feature (non-text output formats for `pg_dumpall`) was already reverted between Beta 1 and Beta 2. Do not run beta builds in production. Beta clusters may require `initdb` or a full `pg_upgrade` cycle if catalog contents change between beta releases, so treat every beta-to-beta step as a major version upgrade.

Latest stable line remains **18.4 (2026-05-14)**; use that for production until 19 goes GA.

## Migration to Version 19 — Incompatible Changes

A dump/restore or `pg_upgrade` is required from any earlier major version. Review each item below before scheduling the upgrade.

### Blocks pg_upgrade outright

- **`btree_gist` opclasses for `inet`/`cidr` are broken** and were replaced — the default index opclass for these types is now the GiST one. The old opclasses could omit rows that should have matched. `pg_upgrade` refuses to proceed while such indexes exist; drop and recreate them.
- **Carriage returns and line feeds are no longer allowed** in database, role, and tablespace names (a security fix). `pg_upgrade` blocks clusters containing such names; rename them first.
- **`MULE_INTERNAL` encoding removed.** Databases using it must be dumped and restored into a different encoding.

### Changed defaults

| Setting | Old | New | Impact |
|---|---|---|---|
| `max_locks_per_transaction` | 64 | 128 | Per-lock sizing also changed — to keep the same effective capacity, **double** any explicit value you carried over. |
| `default_toast_compression` | `pglz` | `lz4` | New TOASTed values compress with LZ4. Existing values stay readable; a build without LZ4 support keeps `pglz`. |
| `jit` | on | **off** | The costing model that decided when to JIT proved unreliable. Analytical workloads that benefited from JIT must now enable it explicitly. |
| `log_lock_waits` | off | **on** | Expect additional log volume on contended workloads. |

### Removed / forced settings

- **RADIUS authentication removed** entirely — it is UDP-only and inherently insecure. Migrate those `pg_hba.conf` entries to LDAP, GSSAPI, cert, or OAuth before upgrading.
- **`standard_conforming_strings` is permanently forced to `on`.** Dumps produced by a pre-19 `pg_dump` against a server running with it off will not load into 19+. Client applications can still talk to older servers.
- **`escape_string_warning` removed** as no longer meaningful.
- Optimizer hook **`get_relation_info_hook` removed**; extensions should move to the new `build_simple_rel_hook`, which fires at a better point.

### Behavior changes

- **`CREATE SCHEMA` no longer reorders objects** to satisfy dependencies. Objects are created in the order written, except foreign keys, which are still created last. Scripts that relied on the old reordering must be reordered by hand.
- **System columns cannot be referenced in `COPY FROM ... WHERE`** — their values were ill-defined during the copy.
- **`json_array()` over zero rows now returns `[]`** instead of `NULL`.
- **`postgres_fdw` now propagates `READ ONLY` and `DEFERRABLE`** to remote sessions. A `READ ONLY` transaction can no longer write through a foreign table.
- **`pg_stat_subscription_stats.sync_error_count` renamed to `sync_table_error_count`**, since sequence sync errors are now counted separately.
- **Wait event type `BUFFERPIN` renamed to `BUFFER`** — update any monitoring queries or dashboards that filter on wait event type.
- **MD5 password authentication now emits warnings** (deprecated since 18); control with the new `md5_password_warnings`.
- Index access method handlers now return a static `IndexAmRoutine` rather than a palloc'd one — relevant to out-of-tree index AMs.
- **C11 is now required** to build (was C99); Meson 0.57.2+, Visual Studio 2019+.

## SQL and DDL

### New query syntax

- **SQL/PGQ property graph queries.** Graph pattern syntax lands as a standards-based feature, implemented internally by rewriting into ordinary relational queries over views.
- **`FOR PORTION OF`** on `UPDATE` and `DELETE` — applies a change only to a slice of a row's validity period, the core write side of temporal tables. The docs gained a dedicated temporal tables section.
- **`GROUP BY ALL`** — groups by every target-list entry that is not an aggregate or window function, removing the need to restate long column lists.
- **`INSERT ... ON CONFLICT DO SELECT ... RETURNING`** — returns the conflicting rows instead of silently doing nothing, optionally locking them with `FOR UPDATE`/`FOR SHARE`.
- **`IGNORE NULLS` / `RESPECT NULLS`** for `lead()`, `lag()`, `first_value()`, `last_value()`, `nth_value()`.
- `GROUP BY` now handles target-list subqueries whose expressions reference non-subquery columns.

### New and extended commands

- **`REPACK`** replaces the confusingly named pair `VACUUM FULL` and `CLUSTER` with a single command. **`REPACK CONCURRENTLY`** rebuilds a table without holding an `ACCESS EXCLUSIVE` lock for the duration, which is the headline maintenance feature of this release. It uses replication slots internally, capped by the new `max_repack_replication_slots`.
- **`ALTER TABLE ... MERGE PARTITIONS` / `SPLIT PARTITIONS`** — restructure partition boundaries in place.
- **`WAIT FOR`** — blocks until a standby has written, flushed, or replayed a given LSN. Useful for read-your-writes patterns against replicas without polling.
- `CHECKPOINT` accepts an option list (`MODE`, `FLUSH_UNLOGGED`).
- `GRANT`/`REVOKE` accept `GRANTED BY` to name the effective grantor role.
- `CREATE FOREIGN DATA WRAPPER ... CONNECTION` names a function supplying connection parameters.
- `ALTER TABLE ALTER CONSTRAINT ... [NOT] ENFORCED` for `CHECK` constraints.
- `CREATE SCHEMA` can create more object kinds inline.

### COPY

- `ON_ERROR SET_NULL` stores `NULL` for values that fail input conversion, instead of aborting or skipping the whole row.
- `COPY TO` emits **JSON**, optionally wrapping all rows in one array via `FORCE_ARRAY`.
- `COPY TO` accepts a **partitioned table** directly, rather than requiring `COPY (SELECT ...)`.
- `COPY FROM` can skip **multiple** header lines.
- Text/CSV parsing uses SIMD instructions and is measurably faster.

### Data types and functions

- **`oid8`** — a 64-bit unsigned OID type; casts to and from database names via `regdatabase`.
- Casts between `bytea` and `uuid`.
- New `jsonpath` string methods: `ltrim()`, `rtrim()`, `btrim()`, `lower()`, `upper()`, `initcap()`, `replace()`, `split_part()`. `IS JSON` now works on domains over `text`, `json`, `jsonb`, `bytea`.
- `encode()`/`decode()` support `base64url` and `base32hex` (both ordering-preserving).
- `random(min, max)` overloads for `date`, `timestamp`, `timestamptz`.
- `range_minus_multi()` / `multirange_minus_multi()` return a set of ranges from a subtraction.
- `tid_block()` and `tid_offset()` decompose TID values.
- `error_on_null()` passes a value through or raises on `NULL`.
- `pg_get_role_ddl()`, `pg_get_tablespace_ddl()`, `pg_get_database_ddl()` reconstruct DDL for cluster-level objects.
- Full text search: new Polish and Esperanto stemmers; the Dutch stemmer was updated, with the previous behavior kept as `dutch_porter`.
- Unicode data updated to 17.0.0; GB18030 updated to the 2022 revision.
- Event triggers are now available in PL/Python.

## Performance

### Planner

- **Eager aggregation** — aggregation can be pushed below joins so that fewer rows reach the join, a significant win for star-schema style queries.
- **`NOT IN` is converted to an anti-join** when the subquery cannot produce NULLs, removing the classic `NOT IN` performance trap. More `LEFT JOIN`s also convert to anti-joins, and Memoize can now be used for anti-joins with a unique inner side.
- Better hash join handling of NULL join keys, and improved semijoin planning.
- `Append` / `MergeAppend` can use explicit incremental sorts; startup costs of partial paths are now considered.
- Expression simplifications: `IS [NOT] DISTINCT FROM NULL` folds to `IS [NOT] NULL`; `IS [NOT] DISTINCT FROM` folds to `=`/`<>` on non-nullable inputs; earlier constant folding for `var IS [NOT] NULL`; optimizations for `COALESCE()` and `ROW(...) IS [NOT] NULL`; simplification of `IS [NOT] TRUE/FALSE/UNKNOWN`.
- Faster join selectivity computation with large statistics targets; optimizer statistics for boolean functions; extended statistics on virtual generated columns.
- `pg_restore_extended_stats()` and `pg_clear_extended_stats()` added; `pg_dump`/`pg_restore` can carry restorable extended statistics.

### Execution and storage

- **Foreign key constraint checks are substantially faster** (roughly up to 2x on FK-heavy write workloads).
- **Ordinary table scans can now set pages all-visible**, not just `VACUUM` and `COPY FREEZE` — index-only scans become effective sooner after a bulk load.
- **Asynchronous I/O** gained better read-ahead scheduling for large requests, and the `worker` `io_method` now manages its own worker pool automatically via `io_min_workers`, `io_max_workers`, `io_worker_idle_timeout`, `io_worker_launch_interval`.
- TID range scans can be parallelized.
- `NOTIFY` wakes only backends listening on the relevant channels rather than nearly all of them.
- Faster row deformation, faster UTF-8 case folding, radix sort for sorting, streaming reads for hash index bulk deletion, GIN vacuuming, `bloom`, and `pgstattuple`.
- Cheaper timing instrumentation (helps `EXPLAIN (ANALYZE, TIMING)`), with a new `timing_clock_source` GUC.
- AVX2 for page checksums, ARM Crypto Extension for CRC32C, SIMD for `hex_encode()`/`hex_decode()`.
- PL/pgSQL `SELECT simple-expression INTO` is optimized.
- Multixact members are now 64-bit.

## Autovacuum and Maintenance

### Parallel autovacuum

Autovacuum workers can now use parallel workers for the index phase, controlled globally and per table:

```sql
autovacuum_max_parallel_workers = ...   -- cluster-wide pool
ALTER TABLE big_table SET (autovacuum_parallel_workers = 4);
```

### Scoring system

Instead of first-come ordering, autovacuum now scores tables and processes the highest-scoring ones first. The weights are tunable:

```sql
autovacuum_freeze_score_weight
autovacuum_multixact_freeze_score_weight
autovacuum_vacuum_score_weight
autovacuum_vacuum_insert_score_weight
autovacuum_analyze_score_weight
```

The per-table scores are visible in the new `pg_stat_autovacuum_scores` view, which is the tool for understanding why a given table is or is not being picked up.

### Logging and progress

- `pg_stat_progress_vacuum` gained `started_by` and `mode`; `pg_stat_progress_analyze` gained `started_by`. These distinguish manual, autovacuum, and wraparound-driven runs.
- `log_autoanalyze_min_duration` splits autoanalyze logging away from `log_autovacuum_min_duration`.
- `VACUUM`/`ANALYZE` logging reports WAL full-page write bytes.
- Wraparound warnings now start at 100 million transactions remaining instead of 40 million.
- `pg_get_multixact_stats()` reports multixact activity.
- **Online data checksums** — checksums can be enabled and disabled while the cluster is running, no longer requiring an offline `pg_checksums` pass.

## Replication

### Logical replication

- **Sequences are replicated.** Subscriber sequence values can be synchronized with the publisher during `CREATE SUBSCRIPTION`, `ALTER SUBSCRIPTION ... REFRESH PUBLICATION`, and the new `ALTER SUBSCRIPTION ... REFRESH SEQUENCES`. Publishers can declare `ALL SEQUENCES`; `pg_get_sequence_data()` inspects sync status. This closes the long-standing gap that made logical replication unusable as a full failover path.
- `CREATE`/`ALTER PUBLICATION ... EXCEPT` excludes specific tables, which pairs naturally with `ALL TABLES`.
- `retain_dead_tuples` keeps the information needed for conflict resolution, bounded by `max_retention_duration` (which rejects negative values as of Beta 2).
- `CREATE SUBSCRIPTION ... SERVER` can reuse `postgres_fdw` connection parameters instead of a duplicated connection string.
- With `wal_level = replica`, logical replication turns itself on when actually needed; the new read-only `effective_wal_level` reports what is in force.

### Physical replication and recovery

- `WAIT FOR` lets a session block until a standby reaches a target LSN.
- `pg_sync_replication_slots()` now waits for synchronization to finish rather than returning early.
- `wal_sender_shutdown_timeout` bounds how long shutdown waits for replicas to catch up.
- `wal_receiver_timeout` is settable per subscription and per user.
- `pg_replication_origin_session_setup()` takes an optional pid, enabling SQL-level parallel apply.

## Monitoring

New views and functions:

- **`pg_stat_lock`** and `pg_stat_get_lock()` — statistics broken down per lock type.
- **`pg_stat_recovery`** — recovery progress and status.
- **`pg_stat_autovacuum_scores`** — per-table autovacuum scoring detail (see above).
- `pg_dsm_registry_allocations` — dynamic shared memory allocations.

Extended existing views:

- `pg_stat_replication_slots`: `mem_exceeded_count`, `slotsync_skip_count`, `slotsync_last_skip`, `slotsync_skip_reason`; `pg_replication_slots` also reports sync-skip information.
- `pg_stat_subscription_stats`: `update_deleted`, `sync_seq_error_count` (and the `sync_error_count` rename noted above).
- `stats_reset` added to `pg_stat_all_tables`, `pg_stat_all_indexes`, `pg_statio_all_sequences`, `pg_stat_user_functions`, `pg_stat_database_conflicts`.
- `pg_stat_progress_basebackup.backup_type` distinguishes full from incremental.
- `pg_stat_wal_receiver.status` gained a `connecting` state; `pg_stat_wal` reports full-page image bytes.
- `pg_available_extensions` and `pg_available_extension_versions` gained `location`.
- `pg_stats`, `pg_stats_ext`, `pg_stats_ext_exprs` gained OID columns.

Logging:

- `log_min_messages` accepts per-process-type levels using `type:level` syntax.
- New IO wait events for `COPY FROM`/`COPY TO` and for WAL write/flush LSNs.
- `debug_print_raw_parse` logs raw parse trees; `debug_exec_backend` reports parameter passing to new backends.
- Messages from remote servers are formatted consistently in the log.

## Security and Authentication

- **RADIUS removed** (see breaking changes).
- **MD5 warnings** via `md5_password_warnings`; MD5 remains deprecated.
- **`password_expiration_warning_threshold`** (default 7 days) warns clients about upcoming password expiry.
- **Server-side SNI** — a new `PGDATA/pg_hosts.conf` maps hostnames to certificate/key pairs, so one instance can serve TLS for multiple hostnames.
- **OAuth improvements**: a revised flow hook `PQAUTHDATA_OAUTH_BEARER_TOKEN_V2` carrying the issuer identifier and error message; custom validators can register their own `pg_hba.conf` options and return `error_detail` on failure; `oauth_ca_file` connection parameter plus `PGOAUTHCAFILE` and `PGOAUTHDEBUG` environment variables.
- `pg_read_all_data` and `pg_write_all_data` now cover large objects.
- Background workers can be configured to terminate before database-level operations.
- List-valued server variables can be emptied by setting them to `NULL`.

## Client Tooling and Extensions

### libpq and psql

- libpq: `servicefile` connection parameter; `PQgetThreadLock()`; protocol version 3.9999 reserved for version negotiation testing.
- psql prompts: `%S` shows the search path (against 18+ servers), `%i` shows hot standby status.
- psql `\pset display_true` / `display_false` control boolean rendering; `SERVICEFILE` variable; comments shown in `\dRp+`, `\dRs+`, `\dX+`; smarter pager invocation and broad tab completion improvements.

### Utilities

- `vacuumdb`: `--analyze-only` and `--analyze-in-stages` now cover partitioned tables; `--dry-run` prints the commands it would run.
- `pg_verifybackup` and `pg_waldump` can read WAL from tar archives; `pg_verifybackup --wal-path` replaces the deprecated `--wal-directory`.
- `pg_upgrade`: much faster large object metadata copying; supports non-default tablespaces located inside `PGDATA`.
- `pgbench --continue-on-error` keeps going after SQL errors.
- `pg_test_timing` reports nanoseconds with histogram and exact-timing output and an optional `--cutoff`.
- `pg_createsubscriber` can ignore named existing publications, store recovery parameters in `pg_createsubscriber.conf`, and redirect output with `-l`/`--logdir`.
- `oid2name --extended` reports relation file paths.

### Contrib modules

- **`pg_plan_advice`** — a new module for stabilizing and steering planner decisions, and **`pg_stash_advice`**, which stores advice per query id and applies it automatically. Together these are the in-core answer to plan regression pinning.
- `pg_stat_statements`: `FETCH` sizes are normalized to constants so different sizes group together; generic and custom plan counts are reported.
- `pg_buffercache`: `pg_buffercache_os_pages()` with optional NUMA detail, plus `pg_buffercache_mark_dirty()`, `pg_buffercache_mark_dirty_relation()`, `pg_buffercache_mark_dirty_all()` for testing.
- `postgres_fdw`: array comparison pushdown in prepared statements; `restore_stats` option to fetch statistics from foreign servers.
- `auto_explain`: `auto_explain.log_io` adds IO reporting; `auto_explain.log_extension_options` permits extension-specific EXPLAIN options.
- `btree_gin` supports all btree cross-type comparisons; `file_fdw` reads multi-line headers; `fuzzystrmatch` `dmetaphone()` handles non-ASCII single-byte encodings.

### Platform notes

AIX support is restored (gcc, 64-bit only). Solaris uses unnamed POSIX semaphores. MSVC supports AArch64 and can build PL/Python against the Python Limited API; Windows gained stack backtraces via DbgHelp. New extension hooks: `planner_setup_hook`, `planner_shutdown_hook`, `joinrel_setup_hook`, `join_path_setup_hook`, plus the ability to replace set-returning functions in `FROM`.

## Upgrade Checklist

1. Scan for `btree_gist` indexes on `inet`/`cidr`, CR/LF in database, role, or tablespace names, and `MULE_INTERNAL` databases — each blocks `pg_upgrade`.
2. Replace any RADIUS entries in `pg_hba.conf`.
3. Double any explicit `max_locks_per_transaction`; decide whether to re-enable `jit`; confirm LZ4 TOAST compression is acceptable; budget for `log_lock_waits` log volume.
4. Update monitoring for `BUFFERPIN` → `BUFFER` and `sync_error_count` → `sync_table_error_count`.
5. Regenerate any pre-19 dumps taken with `standard_conforming_strings = off`.
6. Audit `CREATE SCHEMA` scripts that relied on automatic dependency reordering, and `COPY FROM ... WHERE` clauses referencing system columns.
7. Check for `READ ONLY` transactions that write through `postgres_fdw`, and for code depending on `json_array()` returning `NULL` on empty input.

## Links

- [PostgreSQL 19 release notes](https://www.postgresql.org/docs/19/release-19.html)
- [PostgreSQL 19 Beta 2 announcement](https://www.postgresql.org/about/news/postgresql-19-beta-2-released-3350/)
- [Beta testing information](https://www.postgresql.org/developer/beta/)
- [PostgreSQL 19 open items](https://wiki.postgresql.org/wiki/PostgreSQL_19_Open_Items)
