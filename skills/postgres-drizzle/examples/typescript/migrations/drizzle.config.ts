import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  // Schema file(s) location
  schema: './src/db/schema/*.ts',

  // Migration output directory
  out: './drizzle',

  // Database dialect
  dialect: 'postgresql',

  // Database connection
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },

  // Optional settings
  verbose: true,
  strict: true,
});
