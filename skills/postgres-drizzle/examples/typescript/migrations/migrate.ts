import { drizzle } from 'drizzle-orm/postgres-js';
import { migrate } from 'drizzle-orm/postgres-js/migrator';
import postgres from 'postgres';

async function runMigrations() {
  const connectionString = process.env.DATABASE_URL;

  if (!connectionString) {
    throw new Error('DATABASE_URL environment variable is required');
  }

  // Use single connection for migrations
  const connection = postgres(connectionString, { max: 1 });
  const db = drizzle(connection);

  console.log('Running migrations...');

  await migrate(db, {
    migrationsFolder: './drizzle',
  });

  console.log('Migrations complete!');

  await connection.end();
}

runMigrations().catch((error) => {
  console.error('Migration failed:', error);
  process.exit(1);
});
