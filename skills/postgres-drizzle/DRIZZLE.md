# Drizzle ORM 0.45 Best Practices

Comprehensive reference for Drizzle ORM schema design, queries, migrations, and TypeScript patterns.

## Schema Design

### Column Types for PostgreSQL

```typescript
import {
  pgTable,
  uuid,
  text,
  varchar,
  integer,
  bigint,
  serial,
  bigserial,
  boolean,
  timestamp,
  date,
  time,
  numeric,
  real,
  doublePrecision,
  json,
  jsonb,
  pgEnum,
  index,
  uniqueIndex,
} from 'drizzle-orm/pg-core';
```

### Primary Keys

**UUID (Recommended):**
```typescript
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),  // UUIDv4
  // Or for UUIDv7 (PostgreSQL 18+)
  id: uuid('id').primaryKey().default(sql`uuidv7()`),
});
```

**Serial (Legacy):**
```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),  // auto-increment
});
```

**Identity (PostgreSQL preferred):**
```typescript
export const users = pgTable('users', {
  id: integer('id').primaryKey().generatedAlwaysAsIdentity(),
});
```

### Timestamps Pattern

```typescript
const timestamps = {
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true })
    .notNull()
    .defaultNow()
    .$onUpdate(() => new Date()),
};

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  ...timestamps,
});
```

### Enums

```typescript
// PostgreSQL enum
export const statusEnum = pgEnum('status', ['pending', 'active', 'archived']);

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  status: statusEnum('status').notNull().default('pending'),
});
```

### JSONB Columns

```typescript
export const events = pgTable('events', {
  id: uuid('id').primaryKey().defaultRandom(),
  data: jsonb('data').$type<{
    type: string;
    payload: Record<string, unknown>;
  }>().notNull(),
});
```

### Indexes

```typescript
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull(),
  tenantId: uuid('tenant_id').notNull(),
  status: text('status').notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  // Single column
  index('users_email_idx').on(table.email),

  // Composite
  index('users_tenant_status_idx').on(table.tenantId, table.status),

  // Unique
  uniqueIndex('users_email_unique').on(table.email),

  // Partial (requires raw SQL)
  index('users_active_idx')
    .on(table.email)
    .where(sql`status = 'active'`),
]);
```

### Foreign Keys

```typescript
export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  authorId: uuid('author_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  title: text('title').notNull(),
});
```

---

## Relations

Relations are application-level (not database constraints). Use for relational queries API.

### One-to-Many

```typescript
import { relations } from 'drizzle-orm';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull(),
});

export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  authorId: uuid('author_id').notNull().references(() => users.id),
  title: text('title').notNull(),
});

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

### Many-to-Many

```typescript
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
});

export const groups = pgTable('groups', {
  id: uuid('id').primaryKey().defaultRandom(),
});

export const usersToGroups = pgTable('users_to_groups', {
  userId: uuid('user_id').notNull().references(() => users.id),
  groupId: uuid('group_id').notNull().references(() => groups.id),
}, (table) => [
  primaryKey({ columns: [table.userId, table.groupId] }),
]);

export const usersRelations = relations(users, ({ many }) => ({
  usersToGroups: many(usersToGroups),
}));

export const groupsRelations = relations(groups, ({ many }) => ({
  usersToGroups: many(usersToGroups),
}));

export const usersToGroupsRelations = relations(usersToGroups, ({ one }) => ({
  user: one(users, { fields: [usersToGroups.userId], references: [users.id] }),
  group: one(groups, { fields: [usersToGroups.groupId], references: [groups.id] }),
}));
```

---

## Type Inference

### Basic Types

```typescript
import type { InferSelectModel, InferInsertModel } from 'drizzle-orm';

// Full row type (for SELECT)
type User = InferSelectModel<typeof users>;

// Insert type (optional columns allowed)
type NewUser = InferInsertModel<typeof users>;
```

### Partial Selects

```typescript
// Type from a specific select
const result = await db
  .select({
    id: users.id,
    email: users.email,
  })
  .from(users);

type UserBasic = typeof result[number];
// { id: string; email: string }
```

### Relations Type

```typescript
type UserWithPosts = Awaited<ReturnType<typeof db.query.users.findFirst<{
  with: { posts: true };
}>>>;
```

---

## Query Patterns

### Select Queries

```typescript
import { eq, ne, gt, gte, lt, lte, like, ilike, and, or, not, inArray, isNull, isNotNull, sql } from 'drizzle-orm';

// Basic select
const allUsers = await db.select().from(users);

// Select specific columns
const emails = await db.select({ email: users.email }).from(users);

// With where clause
const user = await db
  .select()
  .from(users)
  .where(eq(users.id, userId));

// Multiple conditions
const activeAdmins = await db
  .select()
  .from(users)
  .where(
    and(
      eq(users.status, 'active'),
      eq(users.role, 'admin'),
    )
  );

// OR conditions
const flaggedUsers = await db
  .select()
  .from(users)
  .where(
    or(
      eq(users.status, 'suspended'),
      gt(users.warningCount, 3),
    )
  );
```

### Conditional Filters

```typescript
// Pass undefined to skip a condition
const filteredPosts = await db
  .select()
  .from(posts)
  .where(
    and(
      eq(posts.published, true),
      searchTerm ? ilike(posts.title, `%${searchTerm}%`) : undefined,
      categoryId ? eq(posts.categoryId, categoryId) : undefined,
      authorId ? eq(posts.authorId, authorId) : undefined,
    )
  );
```

### Joins

```typescript
// Left join
const usersWithPosts = await db
  .select()
  .from(users)
  .leftJoin(posts, eq(posts.authorId, users.id));

// Inner join with specific columns
const result = await db
  .select({
    userName: users.name,
    postTitle: posts.title,
  })
  .from(users)
  .innerJoin(posts, eq(posts.authorId, users.id));

// Multiple joins
const fullData = await db
  .select()
  .from(orders)
  .leftJoin(users, eq(orders.userId, users.id))
  .leftJoin(products, eq(orders.productId, products.id));
```

### Relational Queries (Recommended for Nested Data)

```typescript
// Initialize with schema
const db = drizzle(client, { schema });

// Find one with relations
const userWithPosts = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: {
    posts: true,
  },
});

// Nested relations
const userWithAll = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: {
    posts: {
      with: {
        comments: true,
      },
    },
  },
});

// With filtering on relations
const userWithRecentPosts = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: {
    posts: {
      where: gt(posts.createdAt, oneWeekAgo),
      orderBy: desc(posts.createdAt),
      limit: 10,
    },
  },
});

// Select specific columns
const userBasic = await db.query.users.findFirst({
  columns: {
    id: true,
    email: true,
  },
  with: {
    posts: {
      columns: {
        title: true,
      },
    },
  },
});
```

### Subqueries

```typescript
// Subquery in FROM
const sq = db
  .select({
    authorId: posts.authorId,
    postCount: sql<number>`count(*)`.as('post_count'),
  })
  .from(posts)
  .groupBy(posts.authorId)
  .as('sq');

const usersWithCounts = await db
  .select({
    user: users,
    postCount: sq.postCount,
  })
  .from(users)
  .leftJoin(sq, eq(users.id, sq.authorId));

// Subquery in WHERE (EXISTS)
const usersWithPosts = await db
  .select()
  .from(users)
  .where(
    exists(
      db.select().from(posts).where(eq(posts.authorId, users.id))
    )
  );
```

### Aggregations

```typescript
import { count, sum, avg, min, max } from 'drizzle-orm';

// Count
const [{ total }] = await db
  .select({ total: count() })
  .from(users);

// Group by with aggregates
const postsByAuthor = await db
  .select({
    authorId: posts.authorId,
    postCount: count(),
    totalViews: sum(posts.views),
  })
  .from(posts)
  .groupBy(posts.authorId);

// Having clause
const prolificAuthors = await db
  .select({
    authorId: posts.authorId,
    postCount: count(),
  })
  .from(posts)
  .groupBy(posts.authorId)
  .having(gt(count(), 10));
```

---

## Insert, Update, Delete

### Insert

```typescript
// Single insert
const [newUser] = await db
  .insert(users)
  .values({
    email: 'user@example.com',
    name: 'John',
  })
  .returning();

// Multiple insert
await db.insert(users).values([
  { email: 'user1@example.com', name: 'User 1' },
  { email: 'user2@example.com', name: 'User 2' },
]);

// Upsert (on conflict)
await db
  .insert(users)
  .values({ email: 'user@example.com', name: 'John' })
  .onConflictDoUpdate({
    target: users.email,
    set: { name: 'John Updated' },
  });

// Insert or ignore
await db
  .insert(users)
  .values({ email: 'user@example.com', name: 'John' })
  .onConflictDoNothing();
```

### Update

```typescript
// Update with returning
const [updated] = await db
  .update(users)
  .set({ status: 'active' })
  .where(eq(users.id, userId))
  .returning();

// Update multiple columns
await db
  .update(users)
  .set({
    status: 'active',
    updatedAt: new Date(),
  })
  .where(eq(users.id, userId));

// Increment
await db
  .update(posts)
  .set({ views: sql`${posts.views} + 1` })
  .where(eq(posts.id, postId));
```

### Delete

```typescript
// Delete with returning
const [deleted] = await db
  .delete(users)
  .where(eq(users.id, userId))
  .returning();

// Soft delete pattern
await db
  .update(users)
  .set({ deletedAt: new Date() })
  .where(eq(users.id, userId));
```

---

## Transactions

```typescript
// Basic transaction
const result = await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ email, name }).returning();
  await tx.insert(profiles).values({ userId: user.id });
  return user;
});

// Nested transactions (savepoints)
await db.transaction(async (tx) => {
  await tx.insert(users).values({ ... });

  await tx.transaction(async (tx2) => {
    // Creates savepoint
    await tx2.insert(posts).values({ ... });
  });
});

// Rollback
await db.transaction(async (tx) => {
  await tx.insert(users).values({ ... });

  if (someCondition) {
    tx.rollback();  // Throws to abort transaction
  }

  await tx.insert(profiles).values({ ... });
});
```

---

## Prepared Statements

Prepared statements improve performance by compiling SQL once and reusing.

```typescript
// Prepare a query
const getUserById = db
  .select()
  .from(users)
  .where(eq(users.id, sql.placeholder('id')))
  .prepare('get_user_by_id');

// Execute multiple times
const user1 = await getUserById.execute({ id: 'uuid-1' });
const user2 = await getUserById.execute({ id: 'uuid-2' });

// Prepared insert
const createUser = db
  .insert(users)
  .values({
    email: sql.placeholder('email'),
    name: sql.placeholder('name'),
  })
  .returning()
  .prepare('create_user');

const newUser = await createUser.execute({
  email: 'user@example.com',
  name: 'John',
});
```

**Note:** postgres.js uses prepared statements by default. node-postgres requires explicit preparation.

---

## Migration Workflows

### Commands

```bash
# Generate SQL migration from schema changes
npx drizzle-kit generate

# Apply migrations to database
npx drizzle-kit migrate

# Push schema directly (no migration files)
npx drizzle-kit push

# Pull existing database schema
npx drizzle-kit pull

# Check migration status
npx drizzle-kit check

# Open Drizzle Studio
npx drizzle-kit studio
```

### Configuration (drizzle.config.ts)

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});
```

### Development Workflow

```bash
# 1. Modify schema in TypeScript
# 2. Generate migration
npx drizzle-kit generate

# 3. Review generated SQL in ./drizzle/
# 4. Apply migration
npx drizzle-kit migrate
```

### Production Workflow

```typescript
// In application startup
import { migrate } from 'drizzle-orm/postgres-js/migrator';

await migrate(db, { migrationsFolder: './drizzle' });
```

### Push vs Generate

| Command | Use Case |
|---------|----------|
| `push` | Rapid prototyping, development |
| `generate` + `migrate` | Production, version control |

**Transitioning from push to migrate:**

```bash
# Pull current schema as baseline
npx drizzle-kit pull

# Future changes use generate
npx drizzle-kit generate
```

---

## Database Connection

### postgres.js (Recommended)

```typescript
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

const client = postgres(process.env.DATABASE_URL!);
const db = drizzle(client, { schema });
```

### node-postgres

```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from './schema';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});
const db = drizzle(pool, { schema });
```

### Connection with pg-native (10% faster)

```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool, native } from 'pg';

const pool = new native.Pool({
  connectionString: process.env.DATABASE_URL,
});
const db = drizzle(pool, { schema });
```

---

## Naming Conventions

### Auto camelCase to snake_case

```typescript
import { drizzle } from 'drizzle-orm/postgres-js';

const db = drizzle(client, {
  schema,
  casing: 'snake_case',  // Auto-convert camelCase fields
});

// Now you can use camelCase in schema
export const users = pgTable('users', {
  createdAt: timestamp('created_at'),  // Both work
});
```

### Explicit Column Names

```typescript
export const users = pgTable('users', {
  // TypeScript: createdAt, Database: created_at
  createdAt: timestamp('created_at').notNull(),
});
```

---

## Error Handling

```typescript
import { PostgresError } from 'postgres';

try {
  await db.insert(users).values({ email: 'duplicate@example.com' });
} catch (error) {
  if (error instanceof PostgresError) {
    if (error.code === '23505') {
      // Unique violation
      throw new Error('Email already exists');
    }
    if (error.code === '23503') {
      // Foreign key violation
      throw new Error('Referenced record not found');
    }
  }
  throw error;
}
```

### Common PostgreSQL Error Codes

| Code | Name | Description |
|------|------|-------------|
| 23505 | unique_violation | Duplicate key |
| 23503 | foreign_key_violation | FK constraint |
| 23502 | not_null_violation | NULL in NOT NULL column |
| 23514 | check_violation | CHECK constraint |
| 42P01 | undefined_table | Table doesn't exist |
