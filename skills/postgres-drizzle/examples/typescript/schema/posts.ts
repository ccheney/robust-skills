import {
  pgTable,
  uuid,
  text,
  boolean,
  timestamp,
  integer,
  index,
} from 'drizzle-orm/pg-core';
import { relations, sql } from 'drizzle-orm';
import { users } from './users';
import { comments } from './comments';

const timestamps = {
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true })
    .notNull()
    .defaultNow()
    .$onUpdate(() => new Date()),
};

export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().default(sql`uuidv7()`),

  title: text('title').notNull(),
  content: text('content').notNull(),
  slug: text('slug').notNull().unique(),

  published: boolean('published').notNull().default(false),
  views: integer('views').notNull().default(0),

  // Foreign key with cascade delete
  authorId: uuid('author_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),

  ...timestamps,
}, (table) => [
  // Index for author queries
  index('posts_author_idx').on(table.authorId),

  // Partial index for published posts
  index('published_posts_idx')
    .on(table.createdAt)
    .where(sql`published = true`),

  // Composite index for author + status
  index('posts_author_published_idx').on(table.authorId, table.published),
]);

export const postsRelations = relations(posts, ({ one, many }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
  comments: many(comments),
}));

export type Post = typeof posts.$inferSelect;
export type NewPost = typeof posts.$inferInsert;
