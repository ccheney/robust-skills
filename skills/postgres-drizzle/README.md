# postgres-drizzle

PostgreSQL 18 and Drizzle ORM 0.45 best practices for schema design, queries, migrations, performance optimization, and TypeScript type safety.

## When to use

Claude will automatically use this skill when you're working with:

- Database schema design
- Drizzle ORM queries and relations
- PostgreSQL migrations
- Query performance optimization
- Type-safe database access in TypeScript

## Example usage

```
"Create a Drizzle schema for a blog with users, posts, and comments"
"Optimize this PostgreSQL query for better performance"
"Set up soft deletes with Drizzle ORM"
"What indexes should I add for this query pattern?"
```

## Quick reference

### Schema definition

```typescript
import { pgTable, text, timestamp, uuid, index } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (table) => [
  index('users_email_idx').on(table.email),
]);

export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));
```

### Type inference

```typescript
import type { InferSelectModel, InferInsertModel } from 'drizzle-orm';

type User = InferSelectModel<typeof users>;
type NewUser = InferInsertModel<typeof users>;
```

### Relational queries

```typescript
const userWithPosts = await db.query.users.findFirst({
  where: eq(users.id, userId),
  with: { posts: true },
});
```

## Detailed documentation

- [SKILL.md](SKILL.md) - Quick reference and essential patterns
- [POSTGRES.md](POSTGRES.md) - PostgreSQL 18 configuration, indexing, JSONB, partitioning
- [DRIZZLE.md](DRIZZLE.md) - Drizzle ORM schema design, queries, migrations, relations
