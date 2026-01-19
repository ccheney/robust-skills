import { eq, and, or, gt, gte, lt, lte, like, ilike, inArray, isNull, isNotNull, between, desc, asc, sql } from 'drizzle-orm';
import { db } from '../db';
import { users, posts, comments } from '../schema';

// Basic select
export async function getAllUsers() {
  return db.select().from(users);
}

// Select specific columns
export async function getUserEmails() {
  return db.select({
    id: users.id,
    email: users.email,
  }).from(users);
}

// Where clause
export async function getUserById(userId: string) {
  return db
    .select()
    .from(users)
    .where(eq(users.id, userId));
}

// Multiple conditions (AND)
export async function getActiveAdmins() {
  return db
    .select()
    .from(users)
    .where(and(
      isNull(users.deletedAt),
      eq(users.name, 'admin'),
    ));
}

// OR conditions
export async function getFlaggedUsers() {
  return db
    .select()
    .from(users)
    .where(or(
      isNotNull(users.deletedAt),
      like(users.email, '%spam%'),
    ));
}

// Conditional filters (undefined skips condition)
interface PostFilters {
  search?: string;
  authorId?: string;
  published?: boolean;
}

export async function filterPosts(filters: PostFilters) {
  return db
    .select()
    .from(posts)
    .where(and(
      filters.published !== undefined
        ? eq(posts.published, filters.published)
        : undefined,
      filters.authorId
        ? eq(posts.authorId, filters.authorId)
        : undefined,
      filters.search
        ? ilike(posts.title, `%${filters.search}%`)
        : undefined,
    ));
}

// Order, limit, offset
export async function getRecentPosts(limit = 20, offset = 0) {
  return db
    .select()
    .from(posts)
    .where(eq(posts.published, true))
    .orderBy(desc(posts.createdAt))
    .limit(limit)
    .offset(offset);
}

// Cursor-based pagination (better performance)
export async function getPostsAfterCursor(cursor?: string, limit = 20) {
  return db
    .select()
    .from(posts)
    .where(and(
      eq(posts.published, true),
      cursor ? lt(posts.id, cursor) : undefined,
    ))
    .orderBy(desc(posts.id))
    .limit(limit);
}

// Pattern matching
export async function searchUsers(term: string) {
  return db
    .select()
    .from(users)
    .where(or(
      ilike(users.name, `%${term}%`),
      ilike(users.email, `%${term}%`),
    ));
}

// Between
export async function getPostsInDateRange(start: Date, end: Date) {
  return db
    .select()
    .from(posts)
    .where(between(posts.createdAt, start, end));
}

// IN array
export async function getUsersByIds(ids: string[]) {
  return db
    .select()
    .from(users)
    .where(inArray(users.id, ids));
}
