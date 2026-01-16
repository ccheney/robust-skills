# PostgreSQL 18 Best Practices

Comprehensive reference for PostgreSQL 18 configuration, optimization, and best practices.

## PostgreSQL 18 New Features

### Asynchronous I/O Subsystem

PostgreSQL 18 introduces AIO for concurrent read operations. Benchmarks show up to 3x improvement for sequential scans.

**io_method options:**

| Method | Description | Best For |
|--------|-------------|----------|
| `sync` | PostgreSQL 17 behavior, synchronous | Compatibility |
| `worker` | Background worker processes (default) | Most workloads |
| `io_uring` | Linux kernel interface (5.1+) | Cold cache workloads |

**Configuration:**

```sql
-- Check current settings
SHOW io_method;
SHOW io_workers;
SHOW effective_io_concurrency;
SHOW maintenance_io_concurrency;

-- Recommended production settings
ALTER SYSTEM SET io_method = 'worker';
ALTER SYSTEM SET io_workers = 12;  -- ~1/4 of CPU cores
ALTER SYSTEM SET effective_io_concurrency = 32;
ALTER SYSTEM SET maintenance_io_concurrency = 16;
```

**Supported operations:** Sequential scans, bitmap heap scans, VACUUM. Index scans not yet supported.

### Index Skip Scan

B-tree indexes now support skip scan, improving queries that don't specify leading columns.

```sql
-- Index on (region, status, created_at)
CREATE INDEX orders_region_status_date ON orders(region, status, created_at);

-- This query now uses skip scan (previously full table scan)
SELECT * FROM orders WHERE status = 'pending';
-- ~40% faster without changing SQL
```

### Virtual Generated Columns

Virtual columns compute values at read time (not stored on disk). Now default for generated columns.

```sql
CREATE TABLE products (
  price numeric NOT NULL,
  tax_rate numeric NOT NULL,
  total_price numeric GENERATED ALWAYS AS (price * (1 + tax_rate)) STORED,  -- explicit STORED
  display_price text GENERATED ALWAYS AS (price::text || ' USD')  -- virtual (default)
);
```

**Limitation:** Virtual generated columns cannot be indexed.

### UUIDv7 Support

Timestamp-ordered UUIDs for better index locality:

```sql
SELECT uuidv7();
-- Returns: 019470a8-1234-7abc-8def-012345678901
```

**Advantages over UUIDv4:**
- Chronologically sortable
- Better B-tree index performance
- Reduced index fragmentation
- Time-based partitioning friendly

### Temporal Constraints

`WITHOUT OVERLAPS` for temporal database patterns:

```sql
CREATE TABLE room_bookings (
  room_id int,
  booking_period tstzrange,
  PRIMARY KEY (room_id, booking_period WITHOUT OVERLAPS)
);
```

### RETURNING Enhancements

Access both old and new values:

```sql
-- UPDATE with OLD/NEW access
UPDATE inventory
SET quantity = quantity - 10
WHERE product_id = 123
RETURNING OLD.quantity AS was, NEW.quantity AS now;

-- DELETE with OLD access
DELETE FROM audit_log
WHERE created_at < now() - interval '90 days'
RETURNING OLD.*;

-- MERGE with RETURNING
MERGE INTO products t
USING staging s ON t.sku = s.sku
WHEN MATCHED THEN UPDATE SET price = s.price
WHEN NOT MATCHED THEN INSERT VALUES (s.*)
RETURNING *;
```

---

## Memory Configuration

### shared_buffers

PostgreSQL's main memory cache. Set to ~25% of total RAM.

```sql
-- For 32GB RAM server
ALTER SYSTEM SET shared_buffers = '8GB';
```

### work_mem

Memory for sort and hash operations per query.

| Workload | Recommendation |
|----------|----------------|
| OLTP | 4-16 MB |
| OLAP | 64-256 MB |
| Mixed | 16-64 MB |

```sql
-- Set globally
ALTER SYSTEM SET work_mem = '32MB';

-- Or per-session for large queries
SET work_mem = '256MB';
```

**Warning:** Total memory = `work_mem × max_connections × operations_per_query`. Set conservatively.

### maintenance_work_mem

Memory for VACUUM, CREATE INDEX, and maintenance operations:

```sql
ALTER SYSTEM SET maintenance_work_mem = '1GB';
```

### effective_cache_size

Hint to planner about OS cache. Set to 50-75% of total RAM:

```sql
-- For 32GB RAM
ALTER SYSTEM SET effective_cache_size = '20GB';
```

---

## Indexing Strategies

### B-Tree Indexes (Default)

Best for: equality, range, sorting, LIKE patterns with left anchor.

```sql
-- Single column
CREATE INDEX users_email_idx ON users(email);

-- Composite (order matters for leading column queries)
CREATE INDEX orders_user_date_idx ON orders(user_id, created_at DESC);

-- Unique constraint with index
CREATE UNIQUE INDEX users_email_unique ON users(email);
```

### Partial Indexes

Index only rows matching a condition:

```sql
-- Index only active users
CREATE INDEX active_users_email_idx ON users(email)
WHERE deleted_at IS NULL;

-- Index only pending orders
CREATE INDEX pending_orders_idx ON orders(created_at)
WHERE status = 'pending';
```

**Benefits:** Smaller size, faster updates, more efficient queries.

### Covering Indexes (INCLUDE)

Include columns for index-only scans:

```sql
CREATE INDEX orders_user_idx ON orders(user_id)
INCLUDE (status, total);

-- This query uses index-only scan (no table access)
SELECT status, total FROM orders WHERE user_id = 123;
```

### GIN Indexes for JSONB

Two operator classes:

| Class | Size | Operators | Best For |
|-------|------|-----------|----------|
| `jsonb_ops` (default) | 60-80% of table | @>, ?, ?\|, ?& | Key existence queries |
| `jsonb_path_ops` | 20-30% of table | @> only | Containment queries |

```sql
-- Default (supports key existence)
CREATE INDEX data_gin_idx ON events USING gin(data);

-- Smaller, faster for containment only
CREATE INDEX data_gin_path_idx ON events USING gin(data jsonb_path_ops);
```

**Querying:**

```sql
-- Containment (uses GIN)
SELECT * FROM events WHERE data @> '{"type": "purchase"}';

-- Key existence (requires jsonb_ops)
SELECT * FROM events WHERE data ? 'error_code';

-- Expression index for specific fields
CREATE INDEX events_type_idx ON events USING gin((data->'type'));
```

### Expression Indexes

Index computed values:

```sql
-- Case-insensitive search
CREATE INDEX users_email_lower_idx ON users(lower(email));

-- Date extraction
CREATE INDEX orders_month_idx ON orders(date_trunc('month', created_at));

-- JSONB field
CREATE INDEX events_type_idx ON events((data->>'type'));
```

**Important:** Query must match expression exactly to use the index.

---

## Table Partitioning

### When to Partition

- Tables > 100GB
- Clear partition key (dates, tenant IDs)
- Queries frequently filter on partition key
- Need to archive/drop old data efficiently

### Range Partitioning (Time-Series)

```sql
CREATE TABLE events (
  id uuid PRIMARY KEY DEFAULT uuidv7(),
  event_type text NOT NULL,
  data jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE events_2025_01 PARTITION OF events
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE events_2025_02 PARTITION OF events
  FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

### List Partitioning (Categories)

```sql
CREATE TABLE orders (
  id uuid PRIMARY KEY DEFAULT uuidv7(),
  region text NOT NULL,
  total numeric
) PARTITION BY LIST (region);

CREATE TABLE orders_na PARTITION OF orders
  FOR VALUES IN ('US', 'CA', 'MX');

CREATE TABLE orders_eu PARTITION OF orders
  FOR VALUES IN ('UK', 'DE', 'FR');
```

### Hash Partitioning (Even Distribution)

```sql
CREATE TABLE user_events (
  id uuid PRIMARY KEY DEFAULT uuidv7(),
  user_id uuid NOT NULL,
  data jsonb
) PARTITION BY HASH (user_id);

CREATE TABLE user_events_0 PARTITION OF user_events
  FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE user_events_1 PARTITION OF user_events
  FOR VALUES WITH (MODULUS 4, REMAINDER 1);
-- etc.
```

### Partition Management

```sql
-- Detach old partition (fast)
ALTER TABLE events DETACH PARTITION events_2024_01;

-- Drop detached partition
DROP TABLE events_2024_01;

-- Create future partitions ahead of time
-- Use pg_partman or scheduled scripts
```

---

## Connection Pooling (PgBouncer)

### Why Pool

Each PostgreSQL connection uses ~10MB RAM. PgBouncer connections use ~2KB.

### Pooling Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Session | Connection held for session lifetime | Legacy apps |
| Transaction | Connection released after each transaction | Most applications |
| Statement | Connection released after each statement | Simple queries only |

### Configuration Example

```ini
[databases]
myapp = host=localhost port=5432 dbname=myapp

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = scram-sha-256
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
min_pool_size = 10
reserve_pool_size = 5
```

### Transaction Pooling Limitations

- No `SET SESSION` (use `SET LOCAL`)
- No `PREPARE` (enable `max_prepared_statements`)
- Temp tables must be created/dropped in same transaction

---

## Query Plan Analysis

### EXPLAIN Options

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
```

| Option | Description |
|--------|-------------|
| ANALYZE | Execute query, show actual times |
| BUFFERS | Show buffer/cache hits and reads |
| COSTS | Show planner estimates (default on) |
| TIMING | Show per-node timing (default on with ANALYZE) |
| FORMAT | TEXT, JSON, YAML, XML |

### Reading Plans

**Key metrics:**

- `actual time`: Startup time..total time in ms
- `rows`: Estimated vs actual row count
- `loops`: Number of iterations
- `Buffers: shared hit/read`: Cache hits vs disk reads

**Problem indicators:**

- Large discrepancy between estimated and actual rows
- High `shared read` (cold cache, missing indexes)
- Seq Scan on large tables (missing index)
- Nested Loop with high loop count (consider hash/merge join)

### Example Analysis

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE user_id = '123' AND status = 'pending';

-- Bad: Seq Scan on orders (cost=0.00..50000.00)
--      Filter: (user_id = '123' AND status = 'pending')
--      Rows Removed by Filter: 999000
--      Buffers: shared hit=10000 read=40000

-- Good: Index Scan using orders_user_status_idx
--       Index Cond: (user_id = '123' AND status = 'pending')
--       Buffers: shared hit=10
```

### Maintaining Statistics

```sql
-- Update statistics for a table
ANALYZE orders;

-- Update all statistics
ANALYZE;

-- Check when last analyzed
SELECT relname, last_analyze, last_autoanalyze
FROM pg_stat_user_tables;
```

---

## Row-Level Security (RLS)

### Enable RLS

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Force owner to also follow RLS (optional)
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

### Policy Types

**PERMISSIVE (default):** Any matching policy grants access (OR logic).

**RESTRICTIVE:** All restrictive policies must pass (AND logic).

### Multi-Tenant Pattern

```sql
-- Set tenant context per connection/transaction
SET app.current_tenant_id = 'tenant-123';

-- Create policy
CREATE POLICY tenant_isolation ON documents
  FOR ALL
  TO application_role
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Command-Specific Policies

```sql
-- SELECT only
CREATE POLICY select_own ON documents
  FOR SELECT
  USING (owner_id = current_user_id());

-- INSERT only
CREATE POLICY insert_own ON documents
  FOR INSERT
  WITH CHECK (owner_id = current_user_id());

-- UPDATE (both USING and WITH CHECK)
CREATE POLICY update_own ON documents
  FOR UPDATE
  USING (owner_id = current_user_id())
  WITH CHECK (owner_id = current_user_id());
```

### Performance Tips

- Index columns used in RLS policies
- Avoid joins in policy expressions (use `IN` or `ANY` with arrays)
- Test with `EXPLAIN ANALYZE` to verify policy efficiency

---

## Maintenance Best Practices

### Autovacuum Tuning

```sql
-- Global settings
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;  -- default 0.2
ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.05;  -- default 0.1

-- Per-table for high-write tables
ALTER TABLE events SET (
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_analyze_scale_factor = 0.005
);
```

### Monitoring Bloat

```sql
-- Check table bloat
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS total_size,
       n_dead_tup,
       last_vacuum,
       last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

### Reindexing

```sql
-- Rebuild index without locking (PostgreSQL 12+)
REINDEX INDEX CONCURRENTLY orders_user_idx;

-- Rebuild all indexes on a table
REINDEX TABLE CONCURRENTLY orders;
```

### Checkpoints

```sql
-- Reduce checkpoint frequency for lower I/O
ALTER SYSTEM SET checkpoint_timeout = '15min';  -- default 5min
ALTER SYSTEM SET max_wal_size = '4GB';  -- default 1GB
```
