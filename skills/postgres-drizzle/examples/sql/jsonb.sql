-- JSONB Operations


-- Access operators

-- Get JSON object field (returns jsonb)
SELECT data->'name' FROM users;

-- Get JSON field as text
SELECT data->>'name' FROM users;

-- Get nested field (returns jsonb)
SELECT data#>'{address,city}' FROM users;

-- Get nested field as text
SELECT data#>>'{address,city}' FROM users;


-- Containment operators

-- Contains (data contains the right side)
SELECT * FROM events WHERE data @> '{"type": "purchase"}';

-- Contained by (data is contained by the right side)
SELECT * FROM events WHERE data <@ '{"type": "purchase", "status": "completed"}';


-- Key existence

-- Key exists
SELECT * FROM events WHERE data ? 'error_code';

-- Any key exists
SELECT * FROM events WHERE data ?| array['error', 'warning'];

-- All keys exist
SELECT * FROM events WHERE data ?& array['type', 'timestamp'];


-- JSONB functions

-- Build JSON object
SELECT jsonb_build_object(
  'name', 'John',
  'age', 30,
  'active', true
);

-- Build JSON array
SELECT jsonb_build_array('a', 'b', 'c');

-- Aggregate rows to JSON array
SELECT jsonb_agg(row_to_json(users)) FROM users;

-- Pretty print
SELECT jsonb_pretty(data) FROM events LIMIT 1;


-- Modify JSONB

-- Set/update a key
UPDATE users
SET data = jsonb_set(data, '{preferences,theme}', '"dark"')
WHERE id = 1;

-- Set nested key (create path if not exists)
UPDATE users
SET data = jsonb_set(data, '{settings,notifications,email}', 'true', true)
WHERE id = 1;

-- Remove key
UPDATE users
SET data = data - 'deprecated_field'
WHERE id = 1;

-- Remove nested key
UPDATE users
SET data = data #- '{settings,old_key}'
WHERE id = 1;

-- Concatenate/merge JSONB
UPDATE users
SET data = data || '{"newKey": "value"}'::jsonb
WHERE id = 1;


-- JSONPath queries (SQL/JSON standard)

-- Path exists
SELECT * FROM events
WHERE data @? '$.items[*] ? (@.price > 100)';

-- Extract with path
SELECT jsonb_path_query(data, '$.items[*].name')
FROM orders;

-- Extract all matching values
SELECT jsonb_path_query_array(data, '$.items[*].price')
FROM orders;

-- Extract first matching value
SELECT jsonb_path_query_first(data, '$.items[0].name')
FROM orders;


-- Indexing JSONB

-- GIN index for general queries
CREATE INDEX events_data_gin ON events USING gin(data);

-- GIN with jsonb_path_ops (smaller, faster for @> only)
CREATE INDEX events_data_path ON events USING gin(data jsonb_path_ops);

-- Expression index for specific field
CREATE INDEX events_type_idx ON events((data->>'type'));


-- Query with index hints

-- Uses GIN index (containment)
SELECT * FROM events WHERE data @> '{"type": "purchase"}';

-- Uses expression index
SELECT * FROM events WHERE data->>'type' = 'purchase';

-- Uses GIN index (key existence, requires jsonb_ops)
SELECT * FROM events WHERE data ? 'error_code';
