import { eq, sql } from 'drizzle-orm';
import { db } from '../db';
import { users, posts, type NewUser, type NewPost } from '../schema';

// Single insert with returning
export async function createUser(data: NewUser) {
  const [user] = await db
    .insert(users)
    .values(data)
    .returning();
  return user;
}

// Multiple insert
export async function createUsers(data: NewUser[]) {
  return db
    .insert(users)
    .values(data)
    .returning();
}

// Upsert (on conflict update)
export async function upsertUser(data: NewUser) {
  const [user] = await db
    .insert(users)
    .values(data)
    .onConflictDoUpdate({
      target: users.email,
      set: {
        name: data.name,
        updatedAt: new Date(),
      },
    })
    .returning();
  return user;
}

// Insert or ignore
export async function createUserIfNotExists(data: NewUser) {
  const [user] = await db
    .insert(users)
    .values(data)
    .onConflictDoNothing({ target: users.email })
    .returning();
  return user;
}

// Update with returning
export async function updateUser(userId: string, data: Partial<NewUser>) {
  const [user] = await db
    .update(users)
    .set({
      ...data,
      updatedAt: new Date(),
    })
    .where(eq(users.id, userId))
    .returning();
  return user;
}

// Increment field
export async function incrementPostViews(postId: string) {
  const [post] = await db
    .update(posts)
    .set({
      views: sql`${posts.views} + 1`,
    })
    .where(eq(posts.id, postId))
    .returning();
  return post;
}

// Delete with returning
export async function deleteUser(userId: string) {
  const [deleted] = await db
    .delete(users)
    .where(eq(users.id, userId))
    .returning();
  return deleted;
}

// Soft delete
export async function softDeleteUser(userId: string) {
  const [user] = await db
    .update(users)
    .set({ deletedAt: new Date() })
    .where(eq(users.id, userId))
    .returning();
  return user;
}

// Restore soft-deleted user
export async function restoreUser(userId: string) {
  const [user] = await db
    .update(users)
    .set({ deletedAt: null })
    .where(eq(users.id, userId))
    .returning();
  return user;
}

// Batch update
export async function publishPosts(postIds: string[]) {
  return db
    .update(posts)
    .set({
      published: true,
      updatedAt: new Date(),
    })
    .where(sql`${posts.id} = ANY(${postIds})`)
    .returning();
}
