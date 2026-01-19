import {
  pgTable,
  uuid,
  text,
  timestamp,
} from 'drizzle-orm/pg-core';
import { relations, sql } from 'drizzle-orm';
import { users } from './users';

export const profiles = pgTable('profiles', {
  id: uuid('id').primaryKey().default(sql`uuidv7()`),

  // One-to-one with users (unique constraint)
  userId: uuid('user_id')
    .notNull()
    .unique()
    .references(() => users.id, { onDelete: 'cascade' }),

  bio: text('bio'),
  avatarUrl: text('avatar_url'),
  website: text('website'),

  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export const profilesRelations = relations(profiles, ({ one }) => ({
  user: one(users, {
    fields: [profiles.userId],
    references: [users.id],
  }),
}));

export type Profile = typeof profiles.$inferSelect;
export type NewProfile = typeof profiles.$inferInsert;
