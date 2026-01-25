# PostgreSQL Skill

PostgreSQL best practices for multi-tenant applications.

## What it covers

- **RLS & Multi-tenancy** — tenant isolation via Row-Level Security
- **Schema Design** — data types, constraints, indexes, partitioning
- **Authentication** — pg_hba.conf, SCRAM, OAuth (PG18+), role management
- **Runtime Config** — connections, query tuning, replication, vacuum
- **Internals** — query pipeline, wire protocol, access methods

## Key topics

- UUID-based tenant identifier
- `SET LOCAL` for RLS context in transactions
- Alembic migrations with RLS policies
- Safety constraints for destructive operations

## When to use

Use this skill when designing multi-tenant tables, debugging tenant isolation, writing migrations, or configuring PostgreSQL runtime settings.

## Links

- [Documentation](https://www.postgresql.org/docs/current/)
- [Releases](https://www.postgresql.org/about/newsarchive/pgsql/)
- [GitHub](https://github.com/postgres/postgres)
- [Wiki](https://wiki.postgresql.org/)
