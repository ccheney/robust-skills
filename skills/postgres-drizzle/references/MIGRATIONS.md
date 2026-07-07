# Drizzle Migrations

Comprehensive reference for managing database migrations with drizzle-kit
(stable drizzle-kit 0.3x; v1.0 differences noted inline).

## Contents

- [Configuration](#configuration)
- [Commands](#commands)
- [Migration Workflow](#migration-workflow)
- [Push vs Generate](#push-vs-generate)
- [Migration Patterns](#migration-patterns)
- [Custom Migrations](#custom-migrations)
- [Migration Table](#migration-table)
- [Rollback Strategies](#rollback-strategies)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Configuration

### drizzle.config.ts

```typescript
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  // Schema location
  schema: './src/db/schema.ts',

  // Migration output directory
  out: './drizzle',

  // Database dialect
  dialect: 'postgresql',

  // Database credentials
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },

  // Optional: must match the casing passed to drizzle() at runtime
  casing: 'snake_case',

  // Optional: verbose logging; strict prompts before risky push statements
  verbose: true,
  strict: true,

  // Optional: where the migrations journal table lives
  // (defaults: table "__drizzle_migrations" in schema "drizzle")
  migrations: {
    table: '__drizzle_migrations',
    schema: 'drizzle',
  },
});
```

Note: drizzle-kit@1.0 (beta/RC) removes the `--strict` flag/`strict` behavior
because `push` always prompts for confirmation on data-loss statements
(`--force` to skip).

### Multiple Schema Files

```typescript
export default defineConfig({
  schema: './src/db/schema/*.ts',  // Glob pattern
  // or
  schema: [
    './src/db/schema/users.ts',
    './src/db/schema/posts.ts',
  ],
  // ...
});
```

### Environment-Specific Config

```typescript
import { defineConfig } from 'drizzle-kit';

const isProd = process.env.NODE_ENV === 'production';

export default defineConfig({
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: isProd
      ? process.env.DATABASE_URL!
      : process.env.DEV_DATABASE_URL!,
  },
});
```

---

## Commands

### generate

Generate SQL migrations from schema changes.

```bash
npx drizzle-kit generate
npx drizzle-kit generate --name=add_posts   # readable file name
npx drizzle-kit generate --custom --name=seed-users   # empty file for hand-written SQL
```

Output:
```
drizzle/
  0000_initial.sql
  0001_add_posts.sql
  meta/
    0000_snapshot.json
    0001_snapshot.json
    _journal.json
```

The `meta/` folder and `_journal.json` are part of the migration state — commit
them, and never edit or hand-create files in `drizzle/` outside of `generate`
(the journal won't know about them and `migrate` will skip or mismatch).

### migrate

Apply pending migrations to the database.

```bash
npx drizzle-kit migrate
```

### push

Push schema directly to database (no migration files).

```bash
npx drizzle-kit push
```

**Use cases:**
- Rapid prototyping
- Local development
- Schema experimentation

### pull

Introspect existing database and generate schema.

```bash
npx drizzle-kit pull
```

**Use cases:**
- Adopting Drizzle on existing project
- Syncing schema from production
- Reverse engineering

### check

Verify migration integrity.

```bash
npx drizzle-kit check
```

### studio

Launch Drizzle Studio (database browser).

```bash
npx drizzle-kit studio
```

---

## Migration Workflow

### Development Workflow

```bash
# 1. Modify schema in TypeScript
# Edit src/db/schema.ts

# 2. Generate migration
npx drizzle-kit generate

# 3. Review generated SQL
cat drizzle/0001_*.sql

# 4. Apply migration (local)
npx drizzle-kit migrate
```

### Production Workflow

#### Option 1: Programmatic Migration

```typescript
// src/db/migrate.ts
import { drizzle } from 'drizzle-orm/postgres-js';
import { migrate } from 'drizzle-orm/postgres-js/migrator';
import postgres from 'postgres';

const runMigrations = async () => {
  const connection = postgres(process.env.DATABASE_URL!, { max: 1 });
  const db = drizzle(connection);

  console.log('Running migrations...');
  await migrate(db, { migrationsFolder: './drizzle' });
  console.log('Migrations complete!');

  await connection.end();
};

runMigrations().catch(console.error);
```

```bash
# Run before app starts
npx tsx src/db/migrate.ts
```

#### Option 2: CI/CD Migration

```yaml
# .github/workflows/deploy.yml
- name: Run migrations
  run: npx drizzle-kit migrate
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

#### Option 3: Application Startup

```typescript
// src/index.ts
import { migrate } from 'drizzle-orm/postgres-js/migrator';
import { db } from './db';

async function main() {
  // Run migrations on startup
  await migrate(db, { migrationsFolder: './drizzle' });

  // Start application
  app.listen(3000);
}
```

---

## Push vs Generate

| Aspect | `push` | `generate` + `migrate` |
|--------|--------|------------------------|
| Migration files | No | Yes |
| Version control | No | Yes |
| Rollback support | No | Manual |
| Team collaboration | Difficult | Easy |
| Production use | Not recommended | Recommended |
| Speed | Fast | Slower |

### Transitioning from Push to Migrate

```bash
# 1. Pull current schema as baseline
npx drizzle-kit pull

# 2. Mark current state as migrated
# (Create empty initial migration or use introspect)

# 3. Future changes use generate
npx drizzle-kit generate
```

---

## Migration Patterns

### Adding a Column

```typescript
// Before
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull(),
});

// After
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull(),
  name: text('name'),  // New nullable column
});
```

Generated SQL:
```sql
ALTER TABLE "users" ADD COLUMN "name" text;
```

### Adding a Required Column

```typescript
// Add with default for existing rows
name: text('name').notNull().default('Unknown'),
```

Generated SQL:
```sql
ALTER TABLE "users" ADD COLUMN "name" text NOT NULL DEFAULT 'Unknown';
```

### Renaming a Column or Table

`drizzle-kit generate` cannot tell a rename from a drop+create, so it prompts
interactively ("column renamed or deleted?"). Answer "renamed" to get `ALTER ...
RENAME`; answering wrong (or blindly accepting in CI) produces DROP + ADD and
**loses data**. Always review the generated SQL for renames:

```sql
-- What you want to see
ALTER TABLE "users" RENAME COLUMN "name" TO "full_name";
```

### Adding an Index

```typescript
export const users = pgTable('users', {
  // ...
}, (table) => [
  index('users_email_idx').on(table.email),  // New index
]);
```

Generated SQL:
```sql
CREATE INDEX "users_email_idx" ON "users" ("email");
```

### Adding a Foreign Key

```typescript
export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  authorId: uuid('author_id')
    .notNull()
    .references(() => users.id),  // New FK
});
```

Generated SQL:
```sql
ALTER TABLE "posts"
ADD CONSTRAINT "posts_author_id_users_id_fk"
FOREIGN KEY ("author_id") REFERENCES "users"("id");
```

### Creating a New Table

```typescript
export const comments = pgTable('comments', {
  id: uuid('id').primaryKey().defaultRandom(),
  content: text('content').notNull(),
  postId: uuid('post_id').notNull().references(() => posts.id),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});
```

### Dropping a Table

Remove the table definition from schema. Generated SQL:
```sql
DROP TABLE "old_table";
```

---

## Custom Migrations

### Adding Custom SQL

Generate an empty, journal-registered migration file — do NOT create SQL files
in `drizzle/` by hand (they won't be tracked in `meta/_journal.json`):

```bash
npx drizzle-kit generate --custom --name=posts-search
```

Then fill in the generated file:

```sql
-- drizzle/0005_posts-search.sql

-- Add full-text search
ALTER TABLE posts ADD COLUMN search_vector tsvector;

CREATE INDEX posts_search_idx ON posts USING gin(search_vector);

CREATE OR REPLACE FUNCTION posts_search_trigger() RETURNS trigger AS $$
BEGIN
  NEW.search_vector := to_tsvector('english', NEW.title || ' ' || NEW.content);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_search_update
  BEFORE INSERT OR UPDATE ON posts
  FOR EACH ROW EXECUTE FUNCTION posts_search_trigger();
```

### Data Migrations

```sql
-- Generated with: npx drizzle-kit generate --custom --name=backfill-names
-- drizzle/0006_backfill-names.sql

-- Migrate data from old structure to new
UPDATE users SET full_name = first_name || ' ' || last_name
WHERE full_name IS NULL;

-- Backfill computed column
UPDATE posts SET word_count = array_length(string_to_array(content, ' '), 1);
```

---

## Migration Table

Drizzle tracks applied migrations in `__drizzle_migrations`, which lives in the
`drizzle` schema by default (not `public`):

```sql
SELECT * FROM drizzle.__drizzle_migrations;
```

| id | hash | created_at |
|----|------|------------|
| 1 | abc123 | 2024-01-15 |
| 2 | def456 | 2024-01-20 |

Change the location with the `migrations: { table, schema }` config option
(must match between drizzle-kit and any programmatic `migrate()` call via
`migrationsTable`/`migrationsSchema`).

---

## Rollback Strategies

Drizzle doesn't generate automatic rollbacks. Strategies:

### Manual Rollback Script

```sql
-- drizzle/0003_add_feature.sql
ALTER TABLE users ADD COLUMN feature_flag boolean DEFAULT false;

-- drizzle/rollback/0003_add_feature.sql (manual)
ALTER TABLE users DROP COLUMN feature_flag;
```

### Point-in-Time Recovery

Use PostgreSQL's backup/restore for critical rollbacks.

### Feature Flags

Design migrations to be additive when possible:

```typescript
// Add nullable column (safe)
newFeature: text('new_feature'),

// Later, make required after backfill
newFeature: text('new_feature').notNull(),
```

---

## Best Practices

### 1. Review Generated SQL

Always review before applying:

```bash
npx drizzle-kit generate
cat drizzle/0001_*.sql
```

### 2. Test Migrations

```bash
# Test on copy of production data
pg_dump production_db | psql test_db
npx drizzle-kit migrate --config=drizzle.config.test.ts
```

### 3. Keep Migrations Small

- One feature per migration
- Easier to review and rollback
- Faster to apply

### 4. Use Transactions

PostgreSQL wraps DDL in transactions by default. For large data migrations:

```sql
BEGIN;
-- Migration statements
COMMIT;
```

### 5. Handle Downtime

For zero-downtime deployments, build indexes without locking writes:

```sql
CREATE INDEX CONCURRENTLY users_email_idx ON users(email);
```

Caveat: `CREATE INDEX CONCURRENTLY` cannot run inside a transaction, and the
Drizzle migrator applies each migration file transactionally. Run concurrent
index builds outside the migration pipeline (ops script/psql), or accept a
brief lock with a plain `CREATE INDEX` in the migration.

### 6. Version Control

```gitignore
# .gitignore
# Don't ignore migrations!
# drizzle/  <- Include this in version control
```

### 7. CI Validation

```yaml
# Validate schema matches migrations
- name: Check migrations
  run: |
    npx drizzle-kit generate
    git diff --exit-code drizzle/
```

---

## Troubleshooting

### "Migration already applied"

```sql
-- Check migration status (note the drizzle schema)
SELECT * FROM drizzle.__drizzle_migrations;
```

If a migration ran manually and only needs recording, insert its hash into that
table — but prefer fixing the workflow (only ever apply via `migrate`).

### "Schema out of sync"

```bash
# Pull current state
npx drizzle-kit pull

# Compare with your schema
diff src/db/schema.ts drizzle/schema.ts
```

### "Cannot drop column"

Check for dependencies:

```sql
-- Find dependent objects
SELECT * FROM pg_depend WHERE refobjid = 'table_name'::regclass;
```

### Concurrent Migration Issues

Use advisory locks:

```typescript
await db.execute(sql`SELECT pg_advisory_lock(12345)`);
await migrate(db, { migrationsFolder: './drizzle' });
await db.execute(sql`SELECT pg_advisory_unlock(12345)`);
```
