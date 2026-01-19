-- Row-Level Security (RLS) Examples


-- Enable RLS on a table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Force owner to also follow RLS (optional)
ALTER TABLE documents FORCE ROW LEVEL SECURITY;


-- Multi-tenant isolation policy

-- Set tenant context per connection/transaction
SET app.current_tenant_id = 'tenant-123';

-- Or per transaction
SET LOCAL app.current_tenant_id = 'tenant-123';

-- Create isolation policy
CREATE POLICY tenant_isolation ON documents
  FOR ALL
  TO application_role
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);


-- Command-specific policies

-- SELECT only: users can only see their own data
CREATE POLICY select_own ON documents
  FOR SELECT
  TO authenticated_users
  USING (owner_id = current_user_id());

-- INSERT only: users can only insert their own data
CREATE POLICY insert_own ON documents
  FOR INSERT
  TO authenticated_users
  WITH CHECK (owner_id = current_user_id());

-- UPDATE: need both USING (which rows) and WITH CHECK (new values)
CREATE POLICY update_own ON documents
  FOR UPDATE
  TO authenticated_users
  USING (owner_id = current_user_id())
  WITH CHECK (owner_id = current_user_id());

-- DELETE: users can only delete their own data
CREATE POLICY delete_own ON documents
  FOR DELETE
  TO authenticated_users
  USING (owner_id = current_user_id());


-- Admin bypass policy

CREATE POLICY admin_all ON documents
  FOR ALL
  TO admin_role
  USING (true)
  WITH CHECK (true);


-- Shared access policy (users + collaborators)

CREATE POLICY shared_access ON documents
  FOR SELECT
  TO authenticated_users
  USING (
    owner_id = current_user_id()
    OR id IN (
      SELECT document_id FROM document_shares
      WHERE shared_with_user_id = current_user_id()
    )
  );


-- Helper function for current user ID

CREATE OR REPLACE FUNCTION current_user_id()
RETURNS uuid AS $$
  SELECT current_setting('app.current_user_id', true)::uuid;
$$ LANGUAGE sql STABLE;


-- View policies

SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE tablename = 'documents';


-- Drop policy

DROP POLICY IF EXISTS tenant_isolation ON documents;


-- Disable RLS

ALTER TABLE documents DISABLE ROW LEVEL SECURITY;
