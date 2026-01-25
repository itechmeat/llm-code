# PostgreSQL Replication Settings

Runtime configuration for streaming replication and standbys.

## Primary Server Settings

### WAL Level

```sql
wal_level = replica    -- Default (PG10+), required for replication
wal_level = minimal    -- No replication support
wal_level = logical    -- Required for logical replication
```

### WAL Senders

```sql
max_wal_senders = 10   -- Max concurrent replication connections
```

**Sizing:** Number of standbys + pg_basebackup + buffer

### WAL Retention

```sql
wal_keep_size = 0           -- MB of WAL to retain (PG13+)
max_slot_wal_keep_size = -1 -- Max WAL size per slot (-1 = unlimited)
```

### Replication Slots

```sql
max_replication_slots = 10  -- Max slots
```

**Warning:** Slots prevent WAL removal. Monitor for inactive slots.

### Synchronous Replication

```sql
synchronous_commit = on                -- Wait for local WAL
synchronous_commit = remote_write      -- Wait for standby to receive
synchronous_commit = remote_apply      -- Wait for standby to apply
synchronous_commit = off               -- Async (risk data loss)

synchronous_standby_names = 'standby1,standby2'  -- Priority list
synchronous_standby_names = 'FIRST 2 (s1,s2,s3)' -- Quorum
synchronous_standby_names = 'ANY 2 (s1,s2,s3)'   -- Any 2 of 3
```

## Standby Server Settings

### primary_conninfo

Connection string to primary:

```sql
primary_conninfo = 'host=primary port=5432 user=repl_user password=secret application_name=standby1'
```

### primary_slot_name

Replication slot on primary:

```sql
primary_slot_name = 'standby1_slot'
```

### Hot Standby

```sql
hot_standby = on                    -- Allow read queries on standby
hot_standby_feedback = off          -- Send standby position to primary
```

### Conflict Handling

```sql
max_standby_streaming_delay = 30s   -- Max replay delay before canceling queries
max_standby_archive_delay = 30s     -- Max archive replay delay
```

### Recovery Target (Point-in-Time)

```sql
recovery_target_time = '2024-01-15 10:30:00'
recovery_target_xid = '12345'
recovery_target_lsn = '0/1000000'
recovery_target_name = 'backup_point'
recovery_target_inclusive = true
recovery_target_timeline = 'latest'
recovery_target_action = 'pause'    -- pause, promote, shutdown
```

## Archive Settings

### WAL Archiving

```sql
archive_mode = on
archive_command = 'cp %p /archive/%f'
archive_timeout = 0                  -- Force archive every N seconds (0 = disabled)
```

### Archive Recovery

```sql
restore_command = 'cp /archive/%f %p'
archive_cleanup_command = 'pg_archivecleanup /archive %r'
recovery_end_command = ''
```

## Logical Replication

### Publisher

```sql
wal_level = logical                  -- Required
max_replication_slots = 10
max_wal_senders = 10
```

```sql
CREATE PUBLICATION mypub FOR TABLE t1, t2;
CREATE PUBLICATION allpub FOR ALL TABLES;
```

### Subscriber

```sql
CREATE SUBSCRIPTION mysub
  CONNECTION 'host=publisher dbname=mydb user=repl'
  PUBLICATION mypub;
```

### Logical Decoding

```sql
max_logical_replication_workers = 4
max_sync_workers_per_subscription = 2
```

## Quick Reference

### Streaming Replication Setup

**Primary postgresql.conf:**

```sql
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
synchronous_commit = on
```

**Primary pg_hba.conf:**

```text
host replication repl_user standby_ip/32 scram-sha-256
```

**Standby postgresql.conf:**

```sql
primary_conninfo = 'host=primary_ip user=repl_user password=...'
primary_slot_name = 'standby1_slot'
hot_standby = on
```

### Create Replication Slot

```sql
-- Physical
SELECT pg_create_physical_replication_slot('standby1_slot');

-- Logical
SELECT pg_create_logical_replication_slot('mysub', 'pgoutput');
```

### Monitor Replication

```sql
-- On primary
SELECT * FROM pg_stat_replication;
SELECT * FROM pg_replication_slots;

-- Lag calculation
SELECT client_addr,
       pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) AS send_lag,
       pg_wal_lsn_diff(sent_lsn, flush_lsn) AS flush_lag,
       pg_wal_lsn_diff(flush_lsn, replay_lsn) AS replay_lag
FROM pg_stat_replication;
```

### Promote Standby

```sql
SELECT pg_promote();
```

Or:

```bash
pg_ctl promote -D $PGDATA
```

## Parameter Context

| Parameter | Requires |
|-----------|----------|
| `wal_level` | Restart |
| `max_wal_senders` | Restart |
| `max_replication_slots` | Restart |
| `synchronous_commit` | Reload |
| `synchronous_standby_names` | Reload |
| `primary_conninfo` | Reload |
| `hot_standby` | Restart |

## See Also

- [PostgreSQL Streaming Replication docs](https://www.postgresql.org/docs/current/warm-standby.html)
- [PostgreSQL Logical Replication docs](https://www.postgresql.org/docs/current/logical-replication.html)
- [Replication Runtime Config](https://www.postgresql.org/docs/current/runtime-config-replication.html)
