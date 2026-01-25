# PostgreSQL Database Roles & User Management

Role-based access control in PostgreSQL: create, alter, drop roles, membership, and privilege inheritance.

## Core Concepts

- **Role** — unified concept for users and groups
- **User** — role with LOGIN privilege
- **Group** — role without LOGIN, used for privilege grouping

## Creating Roles

### Basic Syntax

```sql
CREATE ROLE name [ WITH option ... ];
CREATE USER name [ WITH option ... ];  -- Implies LOGIN
CREATE GROUP name [ WITH option ... ]; -- Alias for CREATE ROLE
```

### Common Patterns

```sql
-- Application user with password
CREATE ROLE app_user LOGIN PASSWORD 'secure_password';

-- Read-only user
CREATE ROLE readonly_user LOGIN PASSWORD 'pass' NOSUPERUSER NOCREATEDB;

-- Admin with role management
CREATE ROLE admin_user LOGIN PASSWORD 'pass' CREATEROLE CREATEDB;

-- Service account for replication
CREATE ROLE repl_user REPLICATION LOGIN PASSWORD 'pass';

-- Password with expiration
CREATE ROLE temp_user LOGIN PASSWORD 'pass' VALID UNTIL '2025-12-31 23:59:59';
```

## Role Attributes

| Attribute | Effect |
|-----------|--------|
| `LOGIN` / `NOLOGIN` | Can connect to database |
| `SUPERUSER` / `NOSUPERUSER` | Bypass all permission checks |
| `CREATEDB` / `NOCREATEDB` | Can create databases |
| `CREATEROLE` / `NOCREATEROLE` | Can create/alter/drop roles |
| `REPLICATION` / `NOREPLICATION` | Can initiate streaming replication |
| `BYPASSRLS` / `NOBYPASSRLS` | Bypass row-level security |
| `INHERIT` / `NOINHERIT` | Inherit privileges from member roles |
| `CONNECTION LIMIT n` | Max concurrent connections (-1 = unlimited) |
| `PASSWORD 'pass'` | Set encrypted password |
| `PASSWORD NULL` | Remove password |
| `VALID UNTIL 'timestamp'` | Password expiration |

### Create Role Examples

```sql
-- Superuser (dangerous!)
CREATE ROLE dba SUPERUSER LOGIN PASSWORD 'pass';

-- App user bypassing RLS (for admin tools)
CREATE ROLE admin_api BYPASSRLS LOGIN PASSWORD 'pass';

-- Limited connections
CREATE ROLE batch_user LOGIN CONNECTION LIMIT 5;

-- No inheritance (explicit SET ROLE required)
CREATE ROLE strict_user NOINHERIT LOGIN;
```

## Altering Roles

```sql
-- Change password
ALTER ROLE app_user PASSWORD 'new_password';

-- Remove password
ALTER ROLE app_user PASSWORD NULL;

-- Add privileges
ALTER ROLE app_user CREATEDB CREATEROLE;

-- Remove privileges
ALTER ROLE app_user NOCREATEDB NOCREATEROLE;

-- Rename role
ALTER ROLE old_name RENAME TO new_name;

-- Set connection limit
ALTER ROLE app_user CONNECTION LIMIT 100;

-- Set role-specific defaults
ALTER ROLE analytics_user SET work_mem = '256MB';
ALTER ROLE analytics_user SET statement_timeout = '5min';

-- Reset to system default
ALTER ROLE analytics_user RESET work_mem;
ALTER ROLE analytics_user RESET ALL;
```

## Role Membership (Groups)

### Grant Membership

```sql
-- Basic membership
GRANT admin_group TO app_user;

-- Multiple roles
GRANT readers, writers TO app_user;

-- With options
GRANT admin_group TO app_user WITH ADMIN OPTION;  -- Can grant to others
GRANT admin_group TO app_user WITH INHERIT TRUE;  -- Inherit privileges
GRANT admin_group TO app_user WITH SET FALSE;     -- Cannot SET ROLE to it
```

### Membership Options

| Option | Effect |
|--------|--------|
| `ADMIN` | Can grant/revoke this role to others |
| `INHERIT` | Automatically inherit role's privileges |
| `SET` | Can use `SET ROLE` to assume this role |

### Revoke Membership

```sql
REVOKE admin_group FROM app_user;
REVOKE ADMIN OPTION FOR admin_group FROM app_user;
```

### Switching Roles

```sql
SET ROLE admin;       -- Switch to admin role
SET ROLE NONE;        -- Reset to login role
RESET ROLE;           -- Same as SET ROLE NONE
```

## Dropping Roles

### Pre-Drop Checklist

Before dropping, handle owned objects:

```sql
-- 1. Reassign owned objects to another role
REASSIGN OWNED BY doomed_role TO successor_role;

-- 2. Drop remaining objects and revoke privileges
DROP OWNED BY doomed_role;

-- 3. Repeat in each database
-- 4. Then drop
DROP ROLE doomed_role;
```

### Drop Commands

```sql
DROP ROLE role_name;
DROP ROLE IF EXISTS role_name;
DROP USER username;    -- Alias
DROP GROUP groupname;  -- Alias
```

## Object Privileges (GRANT/REVOKE)

### Table Privileges

```sql
-- Grant specific
GRANT SELECT, INSERT ON table_name TO app_user;
GRANT UPDATE (column1, column2) ON table_name TO app_user;

-- Grant all
GRANT ALL PRIVILEGES ON table_name TO admin_user;

-- Grant to all roles
GRANT SELECT ON public_data TO PUBLIC;

-- With grant option
GRANT SELECT ON table_name TO lead_user WITH GRANT OPTION;

-- All tables in schema
GRANT SELECT ON ALL TABLES IN SCHEMA myschema TO readonly_user;
```

### Revoke Privileges

```sql
REVOKE INSERT ON table_name FROM app_user;
REVOKE ALL PRIVILEGES ON table_name FROM PUBLIC;
REVOKE GRANT OPTION FOR SELECT ON table_name FROM lead_user;
```

### Schema Privileges

```sql
GRANT USAGE ON SCHEMA app_schema TO app_user;
GRANT CREATE ON SCHEMA app_schema TO admin_user;
GRANT ALL ON SCHEMA app_schema TO owner_role;

-- Remove public access
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

### Function Privileges

```sql
GRANT EXECUTE ON FUNCTION my_func(integer) TO app_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA myschema TO admin;
```

## Default Privileges

Set privileges for future objects:

```sql
-- Grant SELECT on all future tables in schema
ALTER DEFAULT PRIVILEGES IN SCHEMA myschema
    GRANT SELECT ON TABLES TO readonly_user;

-- Grant INSERT to webuser
ALTER DEFAULT PRIVILEGES IN SCHEMA myschema
    GRANT INSERT ON TABLES TO webuser;

-- For objects created by specific role
ALTER DEFAULT PRIVILEGES FOR ROLE creator_role IN SCHEMA myschema
    GRANT SELECT ON TABLES TO reader_role;

-- Revoke default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA myschema
    REVOKE SELECT ON TABLES FROM readonly_user;
```

## Security Best Practices

### Principle of Least Privilege

```sql
-- Create minimal role
CREATE ROLE app_user LOGIN PASSWORD 'pass'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;

-- Grant only needed privileges
GRANT USAGE ON SCHEMA app TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON app.orders TO app_user;
GRANT USAGE, SELECT ON SEQUENCE app.orders_id_seq TO app_user;
```

### SECURITY DEFINER Functions

```sql
-- Safe pattern: revoke PUBLIC, grant specific
BEGIN;
CREATE FUNCTION admin_operation() RETURNS void
    SECURITY DEFINER
    SET search_path = pg_catalog, public
AS $$ ... $$;

REVOKE ALL ON FUNCTION admin_operation() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION admin_operation() TO admin_role;
COMMIT;
```

### Password Management

```sql
-- Use SCRAM-SHA-256 (check pg_hba.conf)
ALTER ROLE app_user PASSWORD 'strong_password_here';

-- Temporary access
ALTER ROLE temp_user VALID UNTIL 'now + 1 day';

-- Revoke access immediately
ALTER ROLE compromised_user NOLOGIN;
```

## Predefined Roles (PG14+)

| Role | Purpose |
|------|---------|
| `pg_read_all_data` | SELECT on all tables |
| `pg_write_all_data` | INSERT/UPDATE/DELETE on all tables |
| `pg_read_all_settings` | Read all config parameters |
| `pg_read_all_stats` | Read all statistics views |
| `pg_stat_scan_tables` | Execute functions scanning tables for stats |
| `pg_monitor` | Read various monitoring views |
| `pg_signal_backend` | Send signals to other backends |
| `pg_checkpoint` | Execute CHECKPOINT |

```sql
GRANT pg_read_all_data TO readonly_admin;
GRANT pg_monitor TO monitoring_user;
```

## Querying Role Information

```sql
-- List all roles
SELECT rolname, rolsuper, rolcanlogin, rolcreaterole
FROM pg_roles;

-- Check role membership
SELECT r.rolname AS role, m.rolname AS member
FROM pg_auth_members am
JOIN pg_roles r ON am.roleid = r.oid
JOIN pg_roles m ON am.member = m.oid;

-- Check privileges
SELECT pg_has_role('user', 'role', 'MEMBER');
SELECT pg_has_role('user', 'role', 'USAGE');
```

## Command-Line Tools

```bash
# Create role
createuser -P app_user

# Create superuser
createuser -s admin_user

# Drop role
dropuser app_user

# List roles
psql -c "\\du"
```

## Quick Reference

### Role Lifecycle

```sql
-- 1. Create
CREATE ROLE app_user LOGIN PASSWORD 'pass';

-- 2. Grant membership/privileges
GRANT app_group TO app_user;
GRANT SELECT ON schema.table TO app_user;

-- 3. Maintain
ALTER ROLE app_user PASSWORD 'new_pass';

-- 4. Remove (cleanup first!)
REASSIGN OWNED BY app_user TO admin;
DROP OWNED BY app_user;
DROP ROLE app_user;
```

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| `DROP ROLE` with owned objects | Run `REASSIGN OWNED` + `DROP OWNED` first |
| No `USAGE` on schema | Grant `USAGE ON SCHEMA` before table grants |
| PUBLIC has CREATE on public schema | `REVOKE CREATE ON SCHEMA public FROM PUBLIC` |
| Password not encrypted | Use `ENCRYPTED PASSWORD` or SCRAM-SHA-256 |

## See Also

- [authentication.md](authentication.md) — pg_hba.conf and auth methods
- [PostgreSQL Role Attributes](https://www.postgresql.org/docs/current/role-attributes.html)
- [PostgreSQL GRANT](https://www.postgresql.org/docs/current/sql-grant.html)
