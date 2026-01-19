import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

// Connection string from environment
const connectionString = process.env.DATABASE_URL!;

// postgres.js client with connection pooling
const client = postgres(connectionString, {
  max: 20,              // Max connections in pool
  idle_timeout: 30,     // Close idle connections after 30s
  connect_timeout: 10,  // Connection timeout in seconds
});

// Drizzle instance with schema for relational queries
export const db = drizzle(client, { schema });

// For migrations and one-off scripts (single connection)
export function createMigrationClient() {
  return postgres(connectionString, { max: 1 });
}

// Graceful shutdown
export async function closeDatabase() {
  await client.end();
}
