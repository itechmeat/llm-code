# PostgreSQL Authentication

## Overview

PostgreSQL authentication is controlled via `pg_hba.conf` (Host-Based Authentication). Rules are evaluated top-to-bottom; first match wins.

## Authentication Methods Summary

| Method | Security | Use Case |
|--------|----------|----------|
| `trust` | None | Local dev only |
| `reject` | — | Explicit deny |
| `peer` | OS-level | Local Unix sockets |
| `ident` | OS-level | Remote (RFC 1413) |
| `scram-sha-256` | Strong | Remote (recommended) |
| `md5` | Weak | Legacy |
| `password` | Very weak | Never use |
| `cert` | Strong | mTLS |
| `ldap` | Delegated | Enterprise |
| `radius` | Delegated | Enterprise |
| `gssapi` | Delegated | Kerberos/AD |
| `sspi` | Delegated | Windows AD |
| `pam` | Delegated | PAM modules |
| `oauth` | Delegated | Cloud-native (PG18+) |

## pg_hba.conf Format

### Record Structure

```text
TYPE  DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
```

### Connection Types

| Type | Description |
|------|-------------|
| `local` | Unix socket connections |
| `host` | TCP/IP (SSL or plain) |
| `hostssl` | TCP/IP with SSL required |
| `hostnossl` | TCP/IP without SSL |
| `hostgssenc` | TCP/IP with GSSAPI encryption |
| `hostnogssenc` | TCP/IP without GSSAPI encryption |

### Database Field

| Value | Meaning |
|-------|---------|
| `all` | All databases |
| `sameuser` | Database matching role name |
| `samerole` | User is member of role with DB name |
| `replication` | Replication connections |
| `dbname` | Specific database |
| `db1,db2` | Multiple databases |
| `@file.txt` | Read from file |

### User Field

| Value | Meaning |
|-------|---------|
| `all` | All users |
| `username` | Specific user |
| `+groupname` | Members of group |
| `user1,user2` | Multiple users |
| `@file.txt` | Read from file |

### Address Field

| Format | Example |
|--------|---------|
| CIDR | `192.168.1.0/24` |
| IP/mask | `192.168.1.0 255.255.255.0` |
| Hostname | `host.example.com` |
| Domain suffix | `.example.com` |
| `all` | Any address |
| `samehost` | Server's own IPs |
| `samenet` | Server's subnets |

### Include Directives

```text
include auth.conf
include_if_exists optional.conf
include_dir conf.d
```

### Example pg_hba.conf

```text
# TYPE   DATABASE  USER       ADDRESS          METHOD

# Local connections
local    all       postgres                    peer
local    all       all                         peer

# IPv4 local connections
host     all       all        127.0.0.1/32     scram-sha-256

# IPv6 local connections  
host     all       all        ::1/128          scram-sha-256

# Internal network
host     all       all        10.0.0.0/8       scram-sha-256

# Remote (SSL required)
hostssl  all       all        0.0.0.0/0        scram-sha-256

# Replication
host     replication repl_user 10.0.0.0/8      scram-sha-256

# Block specific user
host     all       baduser    0.0.0.0/0        reject
```

---

## Password Authentication

### SCRAM-SHA-256 (Recommended)

Most secure password-based method:
- Salted Challenge Response
- No plaintext transmission
- Server stores only verifier (non-recoverable)
- Channel binding with SSL

**Setup:**

```sql
-- postgresql.conf
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();
```

```text
# pg_hba.conf
host all all 0.0.0.0/0 scram-sha-256
```

### MD5 (Legacy)

- Weaker, vulnerable to replay attacks
- Auto-upgrades to SCRAM if password stored as SCRAM

**Migration to SCRAM:**

```sql
-- 1. Set encryption
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();

-- 2. Reset passwords
ALTER USER myuser PASSWORD 'new_password';

-- 3. Update pg_hba.conf: md5 -> scram-sha-256
-- 4. Reload
SELECT pg_reload_conf();
```

**Check encoding:**

```sql
SELECT rolname, 
       CASE WHEN rolpassword LIKE 'SCRAM%' THEN 'scram-sha-256'
            WHEN rolpassword LIKE 'md5%' THEN 'md5'
            ELSE 'unknown' END AS encoding
FROM pg_authid WHERE rolpassword IS NOT NULL;
```

### password (Never Use)

Transmits password in cleartext. Never use.

---

## OS-Level Authentication

### peer (Local Only)

Maps OS user to PostgreSQL role via Unix socket:

```text
local all all peer
local all all peer map=mymap
```

### ident (Remote)

Uses RFC 1413 ident server on client machine. Rarely used; requires client ident daemon.

```text
host all all 192.168.0.0/24 ident map=mymap
```

### User Mapping (pg_ident.conf)

Maps external usernames to PostgreSQL roles:

```text
# MAPNAME   SYSTEM-USER   PG-USER
mymap       admin         postgres
mymap       /^(.*)$       \1
```

---

## Certificate Authentication

Requires SSL with client certificate:

```text
hostssl all all 0.0.0.0/0 cert
hostssl all all 0.0.0.0/0 cert clientcert=verify-full
```

Options:
- `clientcert=verify-ca` — Verify CA only
- `clientcert=verify-full` — Verify CA + hostname

Map certificate CN:

```text
# pg_ident.conf
certmap  /CN=(.*)@corp\.com$  \1
```

---

## Enterprise Authentication (Brief)

### LDAP

```text
host all all 0.0.0.0/0 ldap ldapserver=ldap.example.com ldapbasedn="dc=example,dc=com" ldapsearchattribute=uid
```

Two modes:
- **Simple bind**: `ldapprefix` + username + `ldapsuffix`
- **Search+bind**: Search for DN, then bind

### RADIUS

```text
host all all 0.0.0.0/0 radius radiusservers="radius.example.com" radiussecrets="sharedsecret"
```

### GSSAPI (Kerberos)

```text
host all all 0.0.0.0/0 gss include_realm=0 krb_realm=EXAMPLE.COM
```

Requires Kerberos infrastructure.

### SSPI (Windows)

```text
host all all 0.0.0.0/0 sspi include_realm=0
```

Windows-specific, similar to GSSAPI.

### PAM

```text
host all all 0.0.0.0/0 pam pamservice=postgresql
```

Delegates to PAM subsystem.

---

## Special Methods

### trust

No authentication. **Never in production.**

```text
local all all trust
```

### reject

Explicitly deny connections:

```text
host all baduser 0.0.0.0/0 reject
```

---

## Security Best Practices

### Production Checklist

- [ ] `scram-sha-256` for all password auth
- [ ] `hostssl` for remote connections
- [ ] No `trust` authentication
- [ ] Restrict by IP/CIDR
- [ ] `password_encryption = 'scram-sha-256'`
- [ ] `log_connections = on`
- [ ] Audit pg_hba.conf changes

### Reload Configuration

```sql
SELECT pg_reload_conf();
```

Or:

```bash
pg_ctl reload -D $PGDATA
```

**Note:** SSL certificate changes require restart.

### Test Authentication

```bash
psql -h hostname -U user -d dbname
```

```sql
SELECT current_user, session_user, inet_server_addr();
```

---

## See Also

- [authentication-oauth.md](authentication-oauth.md) — OAuth 2.0 (PG18+)
- [PostgreSQL Auth Docs](https://www.postgresql.org/docs/current/client-authentication.html)
