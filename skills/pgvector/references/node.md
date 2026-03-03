# Node.js / TypeScript (pgvector-node)

Upstream: https://github.com/pgvector/pgvector-node

## Install

- `npm install pgvector`

## Common core: SQL literal conversion

- Many integrations use `pgvector.toSql([1, 2, 3])` to pass vectors to SQL safely.

## node-postgres (`pg`)

### Enable extension

- `CREATE EXTENSION IF NOT EXISTS vector`

### Register types (important)

- Register per client or on pool connections:
  - `pgvector.registerTypes(client)`

This enables automatic parsing/serialization of pgvector types.

## Query patterns

- Nearest neighbor:
  - `ORDER BY embedding <-> $1 LIMIT 5` (pass `$1` as `pgvector.toSql([...])`)

## Indexing

- Create HNSW/IVFFlat indexes with operator classes:
  - `vector_l2_ops`, `vector_ip_ops`, `vector_cosine_ops`

## Supported query-builder / ORM integrations shown in README

- Knex.js
- Objection.js
- Kysely
- Sequelize
- pg-promise
- Prisma
- Postgres.js
- Slonik
- TypeORM (0.3.27+ has built-in pgvector support)
- MikroORM

## Notable gotchas

- Prisma: README notes `prisma migrate dev` does not support pgvector indexes; use SQL migrations / raw SQL for index creation.
