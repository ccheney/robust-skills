# postgres-drizzle

PostgreSQL and Drizzle ORM best practices. This skill activates automatically when writing database schemas, queries, migrations, or any database-related code.

Covers the **stable drizzle-orm 0.x** API (npm `latest`) and flags where **v1.0
(beta/RC, Relational Queries v2 / `defineRelations`)** differs, so generated code
matches the version a project actually uses.

## Topics Covered

| Category | Topics |
|----------|--------|
| **Schema** | Column types, constraints, indexes, enums, JSONB, generated columns |
| **Queries** | Operators, joins, aggregations, subqueries, transactions, prepared statements |
| **Relations** | One-to-many, many-to-many, relational queries API (0.x and v1.0 RQB v2) |
| **Migrations** | drizzle-kit commands, workflows, custom SQL migrations, configuration |
| **PostgreSQL** | PG17/18 features, RLS (SQL + Drizzle `pgPolicy`), partitioning, full-text search |
| **Performance** | Indexing strategies, EXPLAIN, connection pooling, pagination |

## Example Usage

```
"Create a users table with email and timestamps"
"Add a posts table with foreign key to users"
"Write a query to get users with their posts"
"Set up drizzle migrations for production"
"Optimize this slow database query"
```

## Skill Structure

- **[SKILL.md](SKILL.md)** - Main skill file (version check, decision trees, core patterns)
- **Reference Files:**
  - [SCHEMA.md](references/SCHEMA.md) - Column types, constraints, indexes
  - [QUERIES.md](references/QUERIES.md) - Query patterns and operators
  - [RELATIONS.md](references/RELATIONS.md) - Relations API, relational queries, RQB v2
  - [MIGRATIONS.md](references/MIGRATIONS.md) - drizzle-kit workflows
  - [POSTGRES.md](references/POSTGRES.md) - PostgreSQL 17/18 features
  - [PERFORMANCE.md](references/PERFORMANCE.md) - Optimization and pooling
  - [CHEATSHEET.md](references/CHEATSHEET.md) - Quick reference

## Quick Start

```typescript
import { eq, relations } from 'drizzle-orm';
import { pgTable, uuid, text, timestamp, index } from 'drizzle-orm/pg-core';
import { drizzle } from 'drizzle-orm/node-postgres';
import * as schema from './schema';

// Schema (schema.ts)
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
});

// Connection — pass the schema to enable db.query.*
export const db = drizzle(process.env.DATABASE_URL!, { schema });

// Query
const user = await db.query.users.findFirst({
  where: eq(users.email, 'user@example.com'),
});
```

## Resources

- **Drizzle Docs**: https://orm.drizzle.team
- **PostgreSQL Docs**: https://www.postgresql.org/docs/current/
