-- Range partitioning (time-series data)

CREATE TABLE events (
  id uuid PRIMARY KEY DEFAULT uuidv7(),
  event_type text NOT NULL,
  data jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE events_2025_01 PARTITION OF events
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE events_2025_02 PARTITION OF events
  FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE events_2025_03 PARTITION OF events
  FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');


-- List partitioning (categorical data)

CREATE TABLE orders (
  id uuid PRIMARY KEY DEFAULT uuidv7(),
  region text NOT NULL,
  total numeric
) PARTITION BY LIST (region);

CREATE TABLE orders_na PARTITION OF orders
  FOR VALUES IN ('US', 'CA', 'MX');

CREATE TABLE orders_eu PARTITION OF orders
  FOR VALUES IN ('UK', 'DE', 'FR', 'IT', 'ES');

CREATE TABLE orders_apac PARTITION OF orders
  FOR VALUES IN ('JP', 'AU', 'SG', 'IN');


-- Hash partitioning (even distribution)

CREATE TABLE user_events (
  id uuid PRIMARY KEY DEFAULT uuidv7(),
  user_id uuid NOT NULL,
  data jsonb
) PARTITION BY HASH (user_id);

CREATE TABLE user_events_0 PARTITION OF user_events
  FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE user_events_1 PARTITION OF user_events
  FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE user_events_2 PARTITION OF user_events
  FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE user_events_3 PARTITION OF user_events
  FOR VALUES WITH (MODULUS 4, REMAINDER 3);


-- Partition management

-- Detach old partition (fast, no lock)
ALTER TABLE events DETACH PARTITION events_2024_01 CONCURRENTLY;

-- Drop detached partition
DROP TABLE events_2024_01;

-- Attach new partition
ALTER TABLE events ATTACH PARTITION events_2025_04
  FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');


-- Query partition directly (for maintenance)
SELECT * FROM events_2025_01 WHERE event_type = 'purchase';


-- Check partition info
SELECT
  parent.relname AS parent,
  child.relname AS partition,
  pg_get_expr(child.relpartbound, child.oid) AS bounds
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'events';
