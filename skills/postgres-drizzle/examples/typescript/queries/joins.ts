import { eq, desc, count, sum } from 'drizzle-orm';
import { db } from '../db';
import { users, posts, comments } from '../schema';

// Left join
export async function getUsersWithPosts() {
  return db
    .select()
    .from(users)
    .leftJoin(posts, eq(posts.authorId, users.id));
}

// Inner join with specific columns
export async function getPostsWithAuthorName() {
  return db
    .select({
      postId: posts.id,
      postTitle: posts.title,
      authorName: users.name,
      authorEmail: users.email,
    })
    .from(posts)
    .innerJoin(users, eq(posts.authorId, users.id));
}

// Multiple joins
export async function getCommentsWithContext() {
  return db
    .select({
      comment: comments,
      post: {
        id: posts.id,
        title: posts.title,
      },
      author: {
        id: users.id,
        name: users.name,
      },
    })
    .from(comments)
    .innerJoin(posts, eq(comments.postId, posts.id))
    .innerJoin(users, eq(comments.authorId, users.id))
    .orderBy(desc(comments.createdAt));
}

// Self-join (e.g., for hierarchical data)
// import { categories } from '../schema';
// export async function getCategoriesWithParent() {
//   const parent = alias(categories, 'parent');
//   return db
//     .select({
//       category: categories,
//       parentName: parent.name,
//     })
//     .from(categories)
//     .leftJoin(parent, eq(categories.parentId, parent.id));
// }
