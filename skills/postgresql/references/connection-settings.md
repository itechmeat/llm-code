# PostgreSQL Connection Settings

Runtime configuration parameters for connections and authentication.

## Connection Settings

### listen_addresses

```sql
-- Default: 'localhost' (local connections only)
listen_addresses = '*'              -- All interfaces
listen_addresses = '0.0.0.0'        -- All IPv4
listen_addresses = '192.168.1.10'   -- Specific IP
listen_addresses = 'localhost,192.168.1.10'  -- Multiple
```

**Note:** Requires restart. Use `pg_hba.conf` for fine-grained access control.

### port

```sql
port = 5432  -- Default
```

### max_connections

Maximum concurrent connections:

```sql
max_connections = 100  -- Default
```

**Sizing:**
- Each connection uses ~5-10MB RAM
- Formula: `max_connections < (RAM - shared_buffers) / per_connection_memory`
- Use connection pooling (PgBouncer) for high-connection workloads

### superuser_reserved_connections

Reserved connections for superusers when `max_connections` is reached:

```sql
superuser_reserved_connections = 3  -- Default
```

### reserved_connections (PG16+)

Reserved connections for roles with `pg_use_reserved_connections`:

```sql
reserved_connections = 0  -- Default
```

### Unix Socket Settings

```sql
unix_socket_directories = '/var/run/postgresql'  -- Default varies
unix_socket_group = ''
unix_socket_permissions = 0777  -- Default
```

## TCP Settings

### TCP Keepalives

Detect dead connections:

```sql
tcp_keepalives_idle = 0       -- Use OS default (seconds)
tcp_keepalives_interval = 0   -- Use OS default
tcp_keepalives_count = 0      -- Use OS default
```

**Recommended for cloud/firewalls:**

```sql
tcp_keepalives_idle = 60
tcp_keepalives_interval = 10
tcp_keepalives_count = 6
```

### tcp_user_timeout (PG12+)

```sql
tcp_user_timeout = 0  -- Milliseconds, 0 = OS default
```

### client_connection_check_interval (PG14+)

```sql
client_connection_check_interval = 0  -- Milliseconds
```

## Authentication Timeouts

### authentication_timeout

Time limit for authentication:

```sql
authentication_timeout = 1min  -- Default
```

### password_encryption

```sql
password_encryption = 'scram-sha-256'  -- Recommended (default in PG14+)
password_encryption = 'md5'            -- Legacy
```

## SSL Settings

### ssl

```sql
ssl = off  -- Default
ssl = on   -- Enable SSL
```

### Certificate Files

```sql
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = ''                  -- For client cert verification
ssl_crl_file = ''                 -- Certificate revocation list
ssl_crl_dir = ''                  -- CRL directory (PG16+)
```

### SSL Protocols and Ciphers

```sql
ssl_min_protocol_version = 'TLSv1.2'  -- Default (PG12+)
ssl_max_protocol_version = ''          -- Empty = no maximum
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on
```

### ssl_passphrase_command

For encrypted private keys:

```sql
ssl_passphrase_command = ''
ssl_passphrase_command_supports_reload = off
```

## Application Settings

### application_name

Set by client, visible in `pg_stat_activity`:

```sql
application_name = ''  -- Default
```

### update_process_title

```sql
update_process_title = on  -- Show query in process title
```

## Quick Reference

### Production Defaults

```sql
# postgresql.conf
listen_addresses = '*'
max_connections = 100
superuser_reserved_connections = 3

# TCP keepalives (recommended)
tcp_keepalives_idle = 60
tcp_keepalives_interval = 10
tcp_keepalives_count = 6

# Authentication
authentication_timeout = 1min
password_encryption = 'scram-sha-256'

# SSL (if enabled)
ssl = on
ssl_min_protocol_version = 'TLSv1.2'
```

### Memory per Connection

| Component | Typical Size |
|-----------|--------------|
| Base overhead | ~5-10 MB |
| work_mem (per sort/hash) | configurable |
| temp_buffers | 8 MB default |

### Connection Limits

Check current connections:

```sql
SELECT count(*) FROM pg_stat_activity;
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

Set per-role limits:

```sql
ALTER ROLE myuser CONNECTION LIMIT 10;
ALTER DATABASE mydb CONNECTION LIMIT 50;
```

## Parameter Context

| Parameter | Requires |
|-----------|----------|
| `listen_addresses` | Restart |
| `port` | Restart |
| `max_connections` | Restart |
| `ssl` | Restart |
| `ssl_*` files | Reload (SIGHUP) |
| `tcp_keepalives_*` | Reload |
| `authentication_timeout` | Reload |

## See Also

- [authentication.md](authentication.md) — pg_hba.conf and auth methods
- [query-tuning.md](query-tuning.md) — Query planner settings
- [PostgreSQL Docs](https://www.postgresql.org/docs/current/runtime-config-connection.html)
