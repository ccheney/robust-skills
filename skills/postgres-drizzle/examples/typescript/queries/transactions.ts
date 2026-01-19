import { eq } from 'drizzle-orm';
import { db } from '../db';
import { users, posts, profiles, type NewUser, type NewPost } from '../schema';

// Basic transaction
export async function createUserWithProfile(
  userData: NewUser,
  bio: string
) {
  return db.transaction(async (tx) => {
    // Insert user
    const [user] = await tx
      .insert(users)
      .values(userData)
      .returning();

    // Insert profile
    const [profile] = await tx
      .insert(profiles)
      .values({
        userId: user.id,
        bio,
      })
      .returning();

    return { user, profile };
  });
}

// Transaction with rollback on condition
export async function transferCredits(
  fromUserId: string,
  toUserId: string,
  amount: number
) {
  return db.transaction(async (tx) => {
    // Get sender's current balance
    const [sender] = await tx
      .select()
      .from(users)
      .where(eq(users.id, fromUserId));

    // Check balance (hypothetical credits field)
    // if (sender.credits < amount) {
    //   tx.rollback(); // Throws to abort transaction
    // }

    // Deduct from sender
    // await tx
    //   .update(users)
    //   .set({ credits: sql`credits - ${amount}` })
    //   .where(eq(users.id, fromUserId));

    // Add to receiver
    // await tx
    //   .update(users)
    //   .set({ credits: sql`credits + ${amount}` })
    //   .where(eq(users.id, toUserId));

    return { success: true };
  });
}

// Nested transaction (savepoint)
export async function createPostWithOptionalMedia(
  postData: NewPost,
  mediaUrls?: string[]
) {
  return db.transaction(async (tx) => {
    // Create post
    const [post] = await tx
      .insert(posts)
      .values(postData)
      .returning();

    // Try to add media (optional)
    if (mediaUrls && mediaUrls.length > 0) {
      try {
        await tx.transaction(async (tx2) => {
          // This creates a savepoint
          // If this fails, only this inner transaction rolls back
          // await tx2.insert(postMedia).values(
          //   mediaUrls.map(url => ({ postId: post.id, url }))
          // );
        });
      } catch (error) {
        // Inner transaction failed, but outer continues
        console.warn('Media upload failed, continuing without media');
      }
    }

    return post;
  });
}

// Transaction with isolation level
export async function processOrder(orderId: string) {
  return db.transaction(async (tx) => {
    // Process order logic...
    return { orderId, status: 'processed' };
  }, {
    isolationLevel: 'serializable',
    accessMode: 'read write',
  });
}
