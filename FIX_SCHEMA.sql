-- ============================================================
-- Fix database schema - rename tables and add missing columns
-- ============================================================

-- Rename documents table to organization_documents
ALTER TABLE IF EXISTS documents RENAME TO organization_documents;

-- Rename chunks table to organization_chunks
ALTER TABLE IF EXISTS chunks RENAME TO organization_chunks;

-- Add missing column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS assigned_ai_employees UUID[] DEFAULT ARRAY[]::UUID[];

-- Rename rbac_access_attempts to tool_access_attempts
ALTER TABLE IF EXISTS rbac_access_attempts RENAME TO tool_access_attempts;

-- ============================================================
-- Seed RBAC Roles (required for demo setup)
-- ============================================================

INSERT INTO ai_employee_roles (role_name, role_category, description, job_description, icon, example_task)
VALUES
  ('Sales Development Rep (SDR)', 'sales', 'SDR for prospecting and lead generation', 'Find and qualify leads', '📞', 'Email 100 prospects'),
  ('Customer Support Agent', 'support', 'Support agent for customer issues', 'Resolve customer problems', '🎧', 'Handle support tickets'),
  ('Recruiter', 'hr', 'Technical recruiter for hiring', 'Source and screen candidates', '👥', 'Send recruitment emails'),
  ('Sales Manager', 'sales', 'Sales manager for team oversight', 'Manage sales team', '📊', 'Create sales reports'),
  ('Operations Manager', 'ops', 'Operations manager', 'Manage operations', '⚙️', 'Order equipment')
ON CONFLICT (role_name) DO NOTHING;

-- ============================================================
-- Seed RBAC Tools
-- ============================================================

INSERT INTO rbac_tools (tool_name, description, category)
VALUES
  ('send_email', 'Send emails to contacts', 'communication'),
  ('create_crm_lead', 'Add leads to CRM system', 'crm'),
  ('create_support_ticket', 'Create support tickets', 'support'),
  ('schedule_calendar_event', 'Schedule calendar events', 'calendar'),
  ('place_equipment_order', 'Place equipment orders', 'operations')
ON CONFLICT (tool_name) DO NOTHING;

-- ============================================================
-- Seed Role Permissions
-- ============================================================

-- Get role IDs
WITH roles AS (
  SELECT id, role_name FROM ai_employee_roles
),
tools AS (
  SELECT id, tool_name FROM rbac_tools
)

INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
-- Sales Development Rep (SDR) - can send email and create CRM leads
SELECT r.id, 'send_email', true, NULL FROM roles r WHERE r.role_name = 'Sales Development Rep (SDR)'
UNION ALL
SELECT r.id, 'create_crm_lead', true, NULL FROM roles r WHERE r.role_name = 'Sales Development Rep (SDR)'
UNION ALL
-- Customer Support Agent - can create tickets and send email
SELECT r.id, 'create_support_ticket', true, NULL FROM roles r WHERE r.role_name = 'Customer Support Agent'
UNION ALL
SELECT r.id, 'send_email', true, NULL FROM roles r WHERE r.role_name = 'Customer Support Agent'
UNION ALL
-- Recruiter - can send email only
SELECT r.id, 'send_email', true, NULL FROM roles r WHERE r.role_name = 'Recruiter'
UNION ALL
-- Sales Manager - all tools
SELECT r.id, 'send_email', true, NULL FROM roles r WHERE r.role_name = 'Sales Manager'
UNION ALL
SELECT r.id, 'create_crm_lead', true, NULL FROM roles r WHERE r.role_name = 'Sales Manager'
UNION ALL
SELECT r.id, 'schedule_calendar_event', true, NULL FROM roles r WHERE r.role_name = 'Sales Manager'
UNION ALL
-- Operations Manager - can place orders and schedule events
SELECT r.id, 'place_equipment_order', true, NULL FROM roles r WHERE r.role_name = 'Operations Manager'
UNION ALL
SELECT r.id, 'schedule_calendar_event', true, NULL FROM roles r WHERE r.role_name = 'Operations Manager'
ON CONFLICT (role_id, tool_name) DO NOTHING;

-- ============================================================
-- Fix indexes for renamed tables
-- ============================================================

DROP INDEX IF EXISTS idx_chunks_organization;
DROP INDEX IF EXISTS idx_documents_organization;

CREATE INDEX IF NOT EXISTS idx_organization_documents_org ON organization_documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_organization_chunks_org ON organization_chunks(organization_id);
