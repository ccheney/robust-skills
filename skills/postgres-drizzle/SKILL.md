---
name: postgres-drizzle
description: PostgreSQL 18 and Drizzle ORM best practices. Use when writing database schemas, queries, or migrations.
---

# PostgreSQL 18 + Drizzle ORM Best Practices

Best practices for building performant, type-safe database applications with PostgreSQL 18 and Drizzle ORM 0.45.

## Quick Reference

### Schema Definition

```typescript
import { pgTable, text, timestamp, uuid, integer, boolean, index } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

// Use identity columns (recommended over serial in PostgreSQL)
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('users_email_idx').on(table.email),
]);

// Define relations separately
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));
```

### Type Inference

```typescript
import type { InferSelectModel, InferInsertModel } from 'drizzle-orm';

type User = InferSelectModel<typeof users>;
type NewUser = InferInsertModel<typeof users>;
```

### Queries

```typescript
import { eq, and, or, like, ilike, inArray, sql } from 'drizzle-orm';

// Simple select
const user = await db.select().from(users).where(eq(users.id, userId));

// Select with joins
const result = await db
  .select()
  .from(users)
  .leftJoin(posts, eq(posts.authorId, users.id))
  .where(eq(users.id, userId));

// Relational query (preferred for nested data)
const userWithPosts = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: { posts: true },
});
```

### Transactions

```typescript
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ ... }).returning();
  await tx.insert(profiles).values({ userId: user.id, ... });
});
```

---

## PostgreSQL 18 Key Features

### Asynchronous I/O

PostgreSQL 18 introduces AIO for improved read performance:

```sql
-- Check current settings
SHOW io_method;  -- worker (default), io_uring, or sync
SHOW io_workers; -- default 3, increase for larger systems (1/4 of cores)
SHOW effective_io_concurrency; -- default 16
```

**Configuration for production:**
```sql
ALTER SYSTEM SET io_method = 'worker';
ALTER SYSTEM SET io_workers = 12;  -- adjust based on core count
ALTER SYSTEM SET effective_io_concurrency = 32;
```

### Index Skip Scan

PostgreSQL 18 uses skip scan for multicolumn B-tree indexes even when leading columns aren't specified. No configuration needed—automatic ~40% improvement for qualifying queries.

### UUIDv7

Use `uuidv7()` for timestamp-ordered UUIDs (better index performance than UUIDv4):

```sql
SELECT uuidv7();
```

In Drizzle:
```typescript
id: uuid('id').primaryKey().default(sql`uuidv7()`),
```

### RETURNING Enhancements

Access both old and new values in DML:

```sql
UPDATE users SET status = 'active'
RETURNING OLD.status AS previous, NEW.status AS current;
```

---

## Detailed References

**PostgreSQL 18 Best Practices**: See [POSTGRES.md](POSTGRES.md)
- Memory configuration
- Indexing strategies (B-tree, GIN, partial, covering)
- JSONB optimization
- Partitioning strategies
- Connection pooling
- Query plan analysis
- Row-level security

**Drizzle ORM Best Practices**: See [DRIZZLE.md](DRIZZLE.md)
- Schema design patterns
- Query optimization
- Prepared statements
- Migration workflows
- Type inference
- Relations API

---

## Essential Patterns

### Reusable Timestamp Columns

```typescript
const timestamps = {
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
};

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  ...timestamps,
});
```

### Soft Delete Pattern

```typescript
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  deletedAt: timestamp('deleted_at', { withTimezone: true }),
  ...timestamps,
});

// Query active users only
const activeUsers = await db
  .select()
  .from(users)
  .where(isNull(users.deletedAt));
```

### Prepared Statements for Performance

```typescript
// Prepare once, execute many times
const getUserById = db
  .select()
  .from(users)
  .where(eq(users.id, sql.placeholder('id')))
  .prepare('get_user_by_id');

// Execute with parameters
const user = await getUserById.execute({ id: userId });
```

### Conditional Filters

```typescript
const results = await db
  .select()
  .from(posts)
  .where(
    and(
      eq(posts.published, true),
      searchTerm ? ilike(posts.title, `%${searchTerm}%`) : undefined,
      categoryId ? eq(posts.categoryId, categoryId) : undefined,
    )
  );
```

---

## Performance Checklist

### PostgreSQL Configuration
- [ ] Set `shared_buffers` to 25% of RAM
- [ ] Set `effective_cache_size` to 50-75% of RAM
- [ ] Configure `work_mem` based on workload (OLTP: 4-16MB, OLAP: 64-256MB)
- [ ] Enable `io_method = worker` and tune `io_workers`
- [ ] Enable data checksums (default in PostgreSQL 18)

### Indexing
- [ ] Create indexes for foreign keys
- [ ] Use partial indexes for frequently filtered subsets
- [ ] Use covering indexes for hot queries
- [ ] Use GIN with `jsonb_path_ops` for JSONB containment queries
- [ ] Monitor index usage with `pg_stat_user_indexes`

### Queries
- [ ] Use `EXPLAIN (ANALYZE, BUFFERS)` for optimization
- [ ] Use prepared statements for repeated queries
- [ ] Use relational queries API for nested data (avoids N+1)
- [ ] Batch operations where possible

### Maintenance
- [ ] Ensure autovacuum is properly configured
- [ ] Run `ANALYZE` after bulk data changes
- [ ] Monitor bloat and reindex as needed
- [ ] Use connection pooling (PgBouncer) in production
