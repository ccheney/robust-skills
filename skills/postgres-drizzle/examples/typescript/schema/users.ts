import {
  pgTable,
  uuid,
  text,
  timestamp,
  boolean,
  index,
  uniqueIndex,
} from 'drizzle-orm/pg-core';
import { relations, sql } from 'drizzle-orm';
import { posts } from './posts';
import { profiles } from './profiles';

// Reusable timestamp columns
const timestamps = {
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true })
    .notNull()
    .defaultNow()
    .$onUpdate(() => new Date()),
};

// Users table with soft delete
export const users = pgTable('users', {
  // UUIDv7 for timestamp-ordered IDs (PostgreSQL 18+)
  id: uuid('id').primaryKey().default(sql`uuidv7()`),

  email: text('email').notNull().unique(),
  name: text('name').notNull(),

  // Soft delete
  deletedAt: timestamp('deleted_at', { withTimezone: true }),

  ...timestamps,
}, (table) => [
  // Index for email lookups
  index('users_email_idx').on(table.email),

  // Partial index for active users only
  index('active_users_email_idx')
    .on(table.email)
    .where(sql`deleted_at IS NULL`),
]);

// Relations (application-level, not database constraints)
export const usersRelations = relations(users, ({ one, many }) => ({
  profile: one(profiles),
  posts: many(posts),
}));

// Type inference
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
