import {
  pgTable,
  uuid,
  text,
  timestamp,
  primaryKey,
} from 'drizzle-orm/pg-core';
import { relations, sql } from 'drizzle-orm';

// Many-to-many: Users belong to Groups

export const users = pgTable('users', {
  id: uuid('id').primaryKey().default(sql`uuidv7()`),
  name: text('name').notNull(),
});

export const groups = pgTable('groups', {
  id: uuid('id').primaryKey().default(sql`uuidv7()`),
  name: text('name').notNull(),
});

// Junction table with extra fields
export const usersToGroups = pgTable('users_to_groups', {
  userId: uuid('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  groupId: uuid('group_id')
    .notNull()
    .references(() => groups.id, { onDelete: 'cascade' }),

  // Extra fields on the relationship
  role: text('role').notNull().default('member'),
  joinedAt: timestamp('joined_at', { withTimezone: true })
    .notNull()
    .defaultNow(),
}, (table) => [
  // Composite primary key
  primaryKey({ columns: [table.userId, table.groupId] }),
]);

// Relations
export const usersRelations = relations(users, ({ many }) => ({
  usersToGroups: many(usersToGroups),
}));

export const groupsRelations = relations(groups, ({ many }) => ({
  usersToGroups: many(usersToGroups),
}));

export const usersToGroupsRelations = relations(usersToGroups, ({ one }) => ({
  user: one(users, {
    fields: [usersToGroups.userId],
    references: [users.id],
  }),
  group: one(groups, {
    fields: [usersToGroups.groupId],
    references: [groups.id],
  }),
}));
