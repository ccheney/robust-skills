import {
  pgTable,
  uuid,
  text,
  timestamp,
  index,
} from 'drizzle-orm/pg-core';
import { relations, sql } from 'drizzle-orm';
import { users } from './users';
import { posts } from './posts';

export const comments = pgTable('comments', {
  id: uuid('id').primaryKey().default(sql`uuidv7()`),

  content: text('content').notNull(),

  postId: uuid('post_id')
    .notNull()
    .references(() => posts.id, { onDelete: 'cascade' }),

  authorId: uuid('author_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),

  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .defaultNow(),
}, (table) => [
  index('comments_post_idx').on(table.postId),
  index('comments_author_idx').on(table.authorId),
]);

export const commentsRelations = relations(comments, ({ one }) => ({
  post: one(posts, {
    fields: [comments.postId],
    references: [posts.id],
  }),
  author: one(users, {
    fields: [comments.authorId],
    references: [users.id],
  }),
}));

export type Comment = typeof comments.$inferSelect;
export type NewComment = typeof comments.$inferInsert;
