import { db } from '../db';
import { users, posts, profiles, comments } from '../schema';

async function seed() {
  console.log('Seeding database...');

  // Create users
  const [alice, bob] = await db
    .insert(users)
    .values([
      { email: 'alice@example.com', name: 'Alice' },
      { email: 'bob@example.com', name: 'Bob' },
    ])
    .returning();

  console.log('Created users:', alice.id, bob.id);

  // Create profiles
  await db.insert(profiles).values([
    { userId: alice.id, bio: 'Software engineer' },
    { userId: bob.id, bio: 'Designer' },
  ]);

  // Create posts
  const [post1, post2] = await db
    .insert(posts)
    .values([
      {
        title: 'Getting Started with Drizzle',
        content: 'Drizzle is a TypeScript ORM...',
        slug: 'getting-started-drizzle',
        authorId: alice.id,
        published: true,
      },
      {
        title: 'PostgreSQL Best Practices',
        content: 'When working with PostgreSQL...',
        slug: 'postgresql-best-practices',
        authorId: alice.id,
        published: true,
      },
      {
        title: 'Draft Post',
        content: 'This is a draft...',
        slug: 'draft-post',
        authorId: bob.id,
        published: false,
      },
    ])
    .returning();

  console.log('Created posts:', post1.id, post2.id);

  // Create comments
  await db.insert(comments).values([
    { content: 'Great post!', postId: post1.id, authorId: bob.id },
    { content: 'Very helpful, thanks!', postId: post1.id, authorId: alice.id },
    { content: 'Bookmarked!', postId: post2.id, authorId: bob.id },
  ]);

  console.log('Seeding complete!');
}

seed().catch((error) => {
  console.error('Seed failed:', error);
  process.exit(1);
});
