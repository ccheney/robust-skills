import { eq, gt, desc, count, sum, avg, min, max, countDistinct, sql } from 'drizzle-orm';
import { db } from '../db';
import { users, posts, comments } from '../schema';

// Count all rows
export async function getTotalUsers() {
  const [{ total }] = await db
    .select({ total: count() })
    .from(users);
  return total;
}

// Count with condition
export async function getActiveUserCount() {
  const [{ count: activeCount }] = await db
    .select({ count: count() })
    .from(users)
    .where(eq(users.deletedAt, null));
  return activeCount;
}

// Count distinct
export async function getUniqueAuthorsCount() {
  const [{ total }] = await db
    .select({ total: countDistinct(posts.authorId) })
    .from(posts);
  return total;
}

// Sum
export async function getTotalPostViews() {
  const [{ total }] = await db
    .select({ total: sum(posts.views) })
    .from(posts);
  return total;
}

// Average
export async function getAveragePostViews() {
  const [{ avg: average }] = await db
    .select({ avg: avg(posts.views) })
    .from(posts);
  return average;
}

// Min / Max
export async function getViewsRange() {
  const [result] = await db
    .select({
      minViews: min(posts.views),
      maxViews: max(posts.views),
    })
    .from(posts);
  return result;
}

// Group by
export async function getPostCountByAuthor() {
  return db
    .select({
      authorId: posts.authorId,
      postCount: count(),
      totalViews: sum(posts.views),
    })
    .from(posts)
    .groupBy(posts.authorId);
}

// Group by with join
export async function getAuthorStats() {
  return db
    .select({
      authorId: users.id,
      authorName: users.name,
      postCount: count(posts.id),
      totalViews: sum(posts.views),
    })
    .from(users)
    .leftJoin(posts, eq(posts.authorId, users.id))
    .groupBy(users.id, users.name)
    .orderBy(desc(count(posts.id)));
}

// Having clause
export async function getProlificAuthors(minPosts = 10) {
  return db
    .select({
      authorId: posts.authorId,
      postCount: count(),
    })
    .from(posts)
    .groupBy(posts.authorId)
    .having(gt(count(), minPosts));
}

// Complex aggregation with subquery
export async function getUsersWithPostStats() {
  const postStats = db
    .select({
      authorId: posts.authorId,
      postCount: sql<number>`count(*)`.as('post_count'),
      totalViews: sql<number>`sum(${posts.views})`.as('total_views'),
    })
    .from(posts)
    .groupBy(posts.authorId)
    .as('post_stats');

  return db
    .select({
      user: users,
      postCount: postStats.postCount,
      totalViews: postStats.totalViews,
    })
    .from(users)
    .leftJoin(postStats, eq(users.id, postStats.authorId));
}
