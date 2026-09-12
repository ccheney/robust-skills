---
name: postgres-drizzle
description: Write or review PostgreSQL schemas, queries, migrations, and Drizzle ORM code. Use for Postgres/Drizzle relations, indexing, pooling, or query performance; not for unrelated databases or generic backend work.
---

# PostgreSQL and Drizzle ORM

Match database work to the project's installed API and deployment context. The user's explicit instructions take precedence over this skill's guidelines.

## Establish the database contract

Use the relevant schema/query, migration history, and requested behavior as input. For Drizzle code, inspect installed `drizzle-orm`/`drizzle-kit` versions and the driver; for SQL, establish the PostgreSQL version when a version-specific feature matters.

The references cover PostgreSQL 17/18 and distinguish Drizzle's 0.x `relations()` API from the v1 `defineRelations()` API. Do not mix them or infer the installed API from an npm dist-tag. When the version is unknown, use imports/lockfiles or ask for the missing version before giving version-dependent code.

## Keep changes consistent

- Declare database foreign keys separately from ORM relation metadata. Match nullability, uniqueness, and delete behavior to the actual relationship.
- Use the transaction handle for every statement in that transaction; a query through the outer connection can escape it.
- Diagnose slow queries from plans and workload evidence. Evaluate indexes on referencing columns; PostgreSQL does not create them automatically.
- Generate and inspect migration SQL for schema changes. Preserve applied migration history; use a new migration for subsequent changes.
- Establish the target before applying migrations or `push`. Authoring or reviewing SQL does not itself require executing it against a database. Continue execution when the user has already authorized that target and action.
- Treat `EXPLAIN ANALYZE` as query execution, including writes. Use a suitable test target or non-executing plan when execution is outside the task.

Deliver the requested SQL/code, migration, or diagnosis, with compatibility assumptions and relevant verification. If execution is requested but the target is missing, prepare the change and ask only for that missing target.

## References

Read the topic required for the current operation.

| Task | Reference |
|---|---|
| Tables, types, constraints, indexes, generated columns | [SCHEMA.md](references/SCHEMA.md) |
| Reads, writes, joins, transactions, prepared queries | [QUERIES.md](references/QUERIES.md) |
| Relationships and version-specific relational query APIs | [RELATIONS.md](references/RELATIONS.md) |
| drizzle-kit configuration, migration generation and rollout | [MIGRATIONS.md](references/MIGRATIONS.md) |
| PostgreSQL features, RLS, partitioning, JSONB, full-text search | [POSTGRES.md](references/POSTGRES.md) |
| Query plans, indexing, pooling, pagination, bulk work | [PERFORMANCE.md](references/PERFORMANCE.md) |
| Compact syntax or connection setup lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |

For APIs or support not established by the installed project and references, consult version-matched [Drizzle](https://orm.drizzle.team) and [PostgreSQL](https://www.postgresql.org/docs/) documentation.
