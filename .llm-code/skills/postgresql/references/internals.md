# PostgreSQL Internals Reference

High-level overview of PostgreSQL internal architecture.

## Query Processing Pipeline

```
SQL Query → Parser → Rewriter → Planner → Executor → Results
```

| Stage | Input | Output | Purpose |
|-------|-------|--------|---------|
| Parser | SQL text | Parse tree | Syntax validation, tokenization |
| Transformation | Parse tree | Query tree | Semantic analysis, type resolution |
| Rewriter | Query tree | Query tree(s) | Rule/view expansion |
| Planner | Query tree | Plan tree | Cost-based optimization |
| Executor | Plan tree | Tuples | Demand-driven execution |

## Connection Model

PostgreSQL uses **process-per-user** model:
- Postmaster listens on TCP port (default 5432)
- Each client connection gets a dedicated backend process
- Backends communicate via shared memory + semaphores

## Parser Stage

Two-phase architecture:
1. **Lexer/Parser** (scan.l + gram.y): Pure syntax, no database access
2. **Transformation** (analyze.c): Semantic analysis, requires catalog lookups

## Planner/Optimizer

Cost-based optimization with:
- **Path generation**: Sequential scans, index scans, bitmap scans
- **Join planning**: Nested loop, merge join, hash join
- **GEQO**: Genetic algorithm for queries with many tables (>12 by default)

### Cost Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `seq_page_cost` | 1.0 | Sequential page read |
| `random_page_cost` | 4.0 | Random page read |
| `cpu_tuple_cost` | 0.01 | Per-tuple processing |

## Executor

Demand-driven ("volcano") model:
- Plan tree of nodes (Seq Scan, Index Scan, Hash Join, etc.)
- Each node returns one tuple at a time
- Parent nodes call children recursively

## System Catalogs

Metadata stored in regular PostgreSQL tables:

| Catalog | Purpose |
|---------|---------|
| `pg_class` | Tables, indexes, sequences, views |
| `pg_attribute` | Table columns |
| `pg_type` | Data types |
| `pg_proc` | Functions/procedures |
| `pg_index` | Index information |

**Warning**: Direct modification can corrupt the database. Use DDL commands.

## Index Access Methods

| Type | Use Case |
|------|----------|
| B-tree | Equality and range queries (default) |
| GIN | JSONB, arrays, full-text search |
| GiST | Geometric types, ranges |
| SP-GiST | Space-partitioned data |
| BRIN | Large naturally-ordered tables |
| Hash | Equality only |

## Extension Points

| Extension Type | Purpose |
|----------------|---------|
| **Index AM** | Custom index types |
| **Table AM** | Custom storage engines |
| **FDW** | Foreign data wrappers |
| **PL Handler** | Procedural languages |
| **Custom WAL** | Extension logging |

## Error Reporting

```c
ereport(ERROR,
        (errcode(ERRCODE_INVALID_PARAMETER_VALUE),
         errmsg("invalid value: %d", value),
         errhint("Value must be positive.")));
```

| Level | Behavior |
|-------|----------|
| `DEBUG1-5` | Debug messages |
| `LOG` | Server log only |
| `WARNING` | Warning, continues |
| `ERROR` | Abort transaction |
| `FATAL` | Abort session |
| `PANIC` | Crash recovery |

## Key Source Directories

| Directory | Contents |
|-----------|----------|
| `src/backend/parser/` | Parser and transformation |
| `src/backend/optimizer/` | Query planner |
| `src/backend/executor/` | Query executor |
| `src/backend/access/` | Access methods |
| `src/backend/catalog/` | System catalogs |

## See Also

- [protocol.md](protocol.md) — Wire protocol details
- [PostgreSQL Internals Docs](https://www.postgresql.org/docs/current/internals.html)
