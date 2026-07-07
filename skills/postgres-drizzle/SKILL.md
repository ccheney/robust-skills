---
name: postgres-drizzle
description: Proactively apply when creating APIs, backends, or data models. Triggers on PostgreSQL, Postgres, Drizzle, drizzle-orm, drizzle-kit, database, schema, pgTable, tables, columns, indexes, queries, migrations, ORM, relations, relational queries, joins, transactions, SQL, connection pooling, PgBouncer, N+1, JSONB, RLS, full-text search, partitioning. Use when writing database schemas, queries, migrations, connection setup, or any database-related code. PostgreSQL and Drizzle ORM best practices.
---

# PostgreSQL + Drizzle ORM

Type-safe database applications with PostgreSQL 17/18 and Drizzle ORM.

## Version Check (do this first)

Drizzle's API changed significantly between the stable 0.x line and v1.0. Check
`package.json` before writing code, because the two relations APIs are incompatible
and must not be mixed:

| `drizzle-orm` version | Relations API | Query filters |
|-----------------------|---------------|---------------|
| `^0.x` (npm `latest`) | `relations()` per table, `drizzle(client, { schema })` | `where: eq(users.id, id)` |
| `1.0.0-beta.*` / `1.0.0-rc.*` | `defineRelations()` once for all tables, `drizzle(client, { relations })` | `where: { id: userId }` (object style) |

The official docs site (orm.drizzle.team) documents v1.0 syntax on its main pages.
This skill defaults to **stable 0.x** syntax; for v1.0 projects read
[references/RELATIONS.md](references/RELATIONS.md) § "Relational Queries v2".
Signals a project is on v1.0: `defineRelations` imports, object-style `where`,
`r.many.posts()` in relations, `from`/`to` keys instead of `fields`/`references`.

## Essential Commands

```bash
npx drizzle-kit generate   # Generate SQL migration from schema changes
npx drizzle-kit migrate    # Apply pending migrations
npx drizzle-kit push       # Push schema directly (dev/prototyping only)
npx drizzle-kit pull       # Introspect existing DB into a schema file
npx drizzle-kit studio     # Open database browser
npx drizzle-kit check      # Detect migration collisions (race conditions)
```

## Quick Decision Trees

### "How do I model this relationship?"

```
Relationship type?
├─ One-to-many (user has posts)     → FK on "many" side + relations()
├─ Many-to-many (posts have tags)   → Junction table with composite PK + relations()
├─ One-to-one (user has profile)    → FK with unique constraint
└─ Self-referential (comments)      → FK to same table (type the ref as AnyPgColumn)
```

### "Why is my query slow?"

```
Slow query?
├─ Missing index on WHERE/JOIN columns  → Add index (Postgres does NOT auto-index FKs)
├─ Query per row in a loop (N+1)        → Use relational queries (`with:`) or a join
├─ Full table scan                      → EXPLAIN (ANALYZE, BUFFERS), add index
├─ Large OFFSET pagination              → Switch to cursor/keyset pagination
└─ Connection overhead per request      → Pool connections (pg Pool / postgres.js / PgBouncer)
```

### "Which drizzle-kit command?"

```
What do I need?
├─ Schema changed, need versioned SQL   → drizzle-kit generate, review SQL, then migrate
├─ Apply migrations (CI, prod)          → drizzle-kit migrate (or migrate() in code)
├─ Quick local iteration, throwaway DB  → drizzle-kit push
├─ Adopt Drizzle on an existing DB      → drizzle-kit pull
└─ Hand-written SQL (triggers, backfill)→ drizzle-kit generate --custom
```

## Connection Setup

```typescript
// node-postgres — pass a URL and Drizzle creates a Pool for you
import { drizzle } from 'drizzle-orm/node-postgres';
import * as schema from './schema';

export const db = drizzle(process.env.DATABASE_URL!, { schema });
```

```typescript
// postgres.js — built-in pooling; set prepare: false behind a
// transaction-mode pooler (PgBouncer/Supavisor) unless it supports prepared statements
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

const client = postgres(process.env.DATABASE_URL!, { max: 20 });
export const db = drizzle(client, { schema });
```

Passing `schema` is what enables `db.query.*` relational queries — forgetting it is
the most common cause of "Property 'users' does not exist on type ...".

Optional: `drizzle(url, { schema, casing: 'snake_case' })` maps camelCase TS keys to
snake_case columns so you can write `pgTable('users', { createdAt: timestamp() })`
without repeating column names. Set the same `casing` in `drizzle.config.ts`.

## Schema Patterns

### Basic Table with Timestamps

```typescript
import { pgTable, uuid, varchar, timestamp } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true })
    .defaultNow()
    .notNull()
    .$onUpdate(() => new Date()),
});
```

Prefer `timestamp(..., { withTimezone: true })` (timestamptz) — naive timestamps
cause silent timezone bugs. For integer PKs, prefer
`integer().primaryKey().generatedAlwaysAsIdentity()` over `serial()` (the
PostgreSQL-recommended form; serial is legacy).

### Foreign Key with Index

```typescript
import { index } from 'drizzle-orm/pg-core';

export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  title: varchar('title', { length: 255 }).notNull(),
}, (table) => [
  // Postgres creates NO index for FK columns — add one or JOINs/cascades scan
  index('posts_user_id_idx').on(table.userId),
]);
```

The third `pgTable` argument returns an **array** (the older object form is deprecated).

### Relations (stable 0.x API)

```typescript
import { relations } from 'drizzle-orm';

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, { fields: [posts.userId], references: [users.id] }),
}));
```

`relations()` is application-level metadata for `db.query.*` — it does not create
FK constraints. Define both (`.references()` for the DB, `relations()` for queries).

## Query Patterns

```typescript
import { eq } from 'drizzle-orm';

// Relational query — nested data in one round trip, no N+1
const usersWithPosts = await db.query.users.findMany({
  with: { posts: true },
});

// SQL-like query — filters, joins, aggregations
const activeUsers = await db
  .select()
  .from(users)
  .where(eq(users.status, 'active'));

// Transaction — all statements commit or roll back together
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ email }).returning();
  await tx.insert(profiles).values({ userId: user.id });
});
```

Inside a transaction, always use `tx`, not `db` — queries on `db` escape the
transaction and won't roll back.

## Performance Checklist

| Priority | Check | Impact |
|----------|-------|--------|
| CRITICAL | Index all foreign keys | Prevents full scans on JOINs and cascaded deletes |
| CRITICAL | Use relational queries or joins for nested data | Avoids N+1 |
| HIGH | Connection pooling in production | Each PG connection costs ~MBs of RAM |
| HIGH | `EXPLAIN (ANALYZE, BUFFERS)` slow queries | Identifies missing indexes |
| MEDIUM | Partial indexes for filtered subsets | Smaller, faster indexes |
| MEDIUM | UUIDv7 (`uuidv7()`, PG18+) or identity for PKs | Better index locality than UUIDv4 |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| No FK index | Slow JOINs, slow cascades | Add index on every FK column |
| N+1 in loops | Query per row | `with:` relational queries or a join |
| One connection per request | Connection storms, RAM exhaustion | pg `Pool` / postgres.js `max` / PgBouncer |
| `push` in prod | No history, data-loss prompts | `generate` + `migrate` |
| Mixing 0.x `relations()` with v1.0 `defineRelations` | Type errors, broken `db.query` | Pick one per project (see Version Check) |
| Storing JSON as `text` | No validation, no indexing | `jsonb()` column + GIN index |
| `timestamp` without timezone | Silent TZ bugs | `{ withTimezone: true }` |
| Editing applied migration files | Checksum mismatch, drift | New migration (`generate` / `generate --custom`) |

## Reference Documentation

| Read this | When you are... |
|-----------|-----------------|
| [references/SCHEMA.md](references/SCHEMA.md) | Defining tables: column types, constraints, indexes, enums, generated columns |
| [references/QUERIES.md](references/QUERIES.md) | Writing selects, inserts, upserts, transactions, prepared statements |
| [references/RELATIONS.md](references/RELATIONS.md) | Modeling relations or using `db.query.*` — includes the v1.0 RQB v2 API |
| [references/MIGRATIONS.md](references/MIGRATIONS.md) | Configuring drizzle-kit, generating/applying migrations, custom SQL |
| [references/POSTGRES.md](references/POSTGRES.md) | Using PG17/18 features, RLS, partitioning, JSONB ops, full-text search |
| [references/PERFORMANCE.md](references/PERFORMANCE.md) | Indexing strategy, EXPLAIN, pooling, pagination, bulk operations |
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Needing a compact syntax reminder for any of the above |

## Resources

- Drizzle ORM docs: https://orm.drizzle.team (documents v1.0 syntax; see Version Check)
- Drizzle GitHub: https://github.com/drizzle-team/drizzle-orm
- PostgreSQL docs: https://www.postgresql.org/docs/current/
- Row-Level Security: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Index types: https://www.postgresql.org/docs/current/indexes-types.html
