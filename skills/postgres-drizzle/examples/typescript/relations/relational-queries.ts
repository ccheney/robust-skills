import { eq, desc, gt } from 'drizzle-orm';
import { db } from '../db';
import { users, posts } from '../schema';

// Find many
export async function getAllUsers() {
  return db.query.users.findMany();
}

// Find many with filters
export async function getActiveUsers() {
  return db.query.users.findMany({
    where: eq(users.deletedAt, null),
    orderBy: [desc(users.createdAt)],
    limit: 20,
  });
}

// Find first
export async function getUserByEmail(email: string) {
  return db.query.users.findFirst({
    where: eq(users.email, email),
  });
}

// With single relation
export async function getUserWithProfile(userId: string) {
  return db.query.users.findFirst({
    where: eq(users.id, userId),
    with: {
      profile: true,
    },
  });
}

// With multiple relations
export async function getUserWithAllRelations(userId: string) {
  return db.query.users.findFirst({
    where: eq(users.id, userId),
    with: {
      profile: true,
      posts: true,
    },
  });
}

// Nested relations
export async function getPostWithComments(postId: string) {
  return db.query.posts.findFirst({
    where: eq(posts.id, postId),
    with: {
      author: true,
      comments: {
        with: {
          author: true,
        },
      },
    },
  });
}

// Filter and sort relations
export async function getUserWithRecentPosts(userId: string) {
  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

  return db.query.users.findFirst({
    where: eq(users.id, userId),
    with: {
      posts: {
        where: gt(posts.createdAt, oneWeekAgo),
        orderBy: [desc(posts.createdAt)],
        limit: 10,
      },
    },
  });
}

// Select specific columns
export async function getUserBasicInfo(userId: string) {
  return db.query.users.findFirst({
    where: eq(users.id, userId),
    columns: {
      id: true,
      email: true,
      name: true,
      // Excludes: deletedAt, createdAt, updatedAt
    },
  });
}

// Select columns on relations
export async function getUserWithPostTitles(userId: string) {
  return db.query.users.findFirst({
    where: eq(users.id, userId),
    columns: {
      id: true,
      name: true,
    },
    with: {
      posts: {
        columns: {
          id: true,
          title: true,
          published: true,
        },
      },
    },
  });
}

// Exclude sensitive columns
export async function getUserPublicProfile(userId: string) {
  return db.query.users.findFirst({
    where: eq(users.id, userId),
    columns: {
      email: false,  // Exclude email
      deletedAt: false,
    },
    with: {
      profile: {
        columns: {
          userId: false,  // Exclude internal reference
        },
      },
    },
  });
}

// Many-to-many through junction
export async function getUserWithGroups(userId: string) {
  return db.query.users.findFirst({
    where: eq(users.id, userId),
    with: {
      usersToGroups: {
        with: {
          group: true,
        },
      },
    },
  });
}

// Flatten many-to-many result
export async function getUserGroups(userId: string) {
  const user = await db.query.users.findFirst({
    where: eq(users.id, userId),
    with: {
      usersToGroups: {
        with: {
          group: true,
        },
      },
    },
  });

  if (!user) return null;

  // Flatten the junction table
  return {
    ...user,
    groups: user.usersToGroups.map(utg => ({
      ...utg.group,
      role: utg.role,
      joinedAt: utg.joinedAt,
    })),
  };
}
