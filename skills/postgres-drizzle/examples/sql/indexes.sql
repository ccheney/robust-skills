-- B-tree indexes (default)

-- Single column index
CREATE INDEX users_email_idx ON users(email);

-- Composite index (order matters for leading column queries)
CREATE INDEX orders_user_date_idx ON orders(user_id, created_at DESC);

-- Unique index
CREATE UNIQUE INDEX users_email_unique ON users(email);


-- Partial indexes (index only matching rows)

-- Index only active users
CREATE INDEX active_users_email_idx ON users(email)
WHERE deleted_at IS NULL;

-- Index only pending orders
CREATE INDEX pending_orders_idx ON orders(created_at)
WHERE status = 'pending';


-- Covering indexes (INCLUDE for index-only scans)

CREATE INDEX orders_user_idx ON orders(user_id)
INCLUDE (status, total);

-- This query uses index-only scan (no table access):
-- SELECT status, total FROM orders WHERE user_id = 123;


-- Expression indexes

-- Case-insensitive email search
CREATE INDEX users_email_lower_idx ON users(lower(email));

-- Date extraction for time-based queries
CREATE INDEX orders_month_idx ON orders(date_trunc('month', created_at));

-- JSONB field extraction
CREATE INDEX events_type_idx ON events((data->>'type'));


-- GIN indexes for JSONB

-- Default (supports @>, ?, ?|, ?&)
CREATE INDEX events_data_gin_idx ON events USING gin(data);

-- Smaller, faster for containment only (@>)
CREATE INDEX events_data_path_idx ON events USING gin(data jsonb_path_ops);


-- Concurrent index creation (no table lock)

CREATE INDEX CONCURRENTLY users_name_idx ON users(name);


-- Drop index

DROP INDEX IF EXISTS users_name_idx;

-- Concurrent drop
DROP INDEX CONCURRENTLY users_name_idx;


-- Reindex without locking

REINDEX INDEX CONCURRENTLY users_email_idx;
REINDEX TABLE CONCURRENTLY users;
