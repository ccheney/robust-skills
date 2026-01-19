import {
  pgTable,
  pgEnum,
  uuid,
  text,
  jsonb,
  timestamp,
  index,
} from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

// PostgreSQL enum
export const statusEnum = pgEnum('status', ['pending', 'active', 'archived']);
export const roleEnum = pgEnum('user_role', ['admin', 'user', 'guest']);

// Typed JSONB interface
interface UserSettings {
  theme: 'light' | 'dark';
  notifications: {
    email: boolean;
    push: boolean;
  };
  language: string;
}

interface EventData {
  type: string;
  payload: Record<string, unknown>;
  metadata?: {
    source: string;
    version: number;
  };
}

export const users = pgTable('users', {
  id: uuid('id').primaryKey().default(sql`uuidv7()`),
  email: text('email').notNull(),

  // PostgreSQL enum columns
  status: statusEnum('status').notNull().default('pending'),
  role: roleEnum('role').notNull().default('user'),

  // Typed JSONB with default
  settings: jsonb('settings').$type<UserSettings>().default({
    theme: 'light',
    notifications: { email: true, push: false },
    language: 'en',
  }),
});

export const events = pgTable('events', {
  id: uuid('id').primaryKey().default(sql`uuidv7()`),

  // Typed JSONB
  data: jsonb('data').$type<EventData>().notNull(),

  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .defaultNow(),
}, (table) => [
  // GIN index for JSONB containment queries
  index('events_data_gin_idx').on(table.data).using('gin'),
]);

// Query JSONB with containment
// .where(sql`${events.data} @> '{"type": "purchase"}'`)

// Query JSONB field
// .where(sql`${events.data}->>'type' = 'purchase'`)
