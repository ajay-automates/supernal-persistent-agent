-- ============================================================
-- Supernal Persistent Agent - Database Schema Setup
-- Run this in Supabase SQL Editor
-- ============================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

-- AI Employee Roles
CREATE TABLE IF NOT EXISTS ai_employee_roles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  role_name TEXT UNIQUE NOT NULL,
  role_category TEXT,
  description TEXT,
  job_description TEXT,
  icon TEXT,
  example_task TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- AI Employees table
CREATE TABLE IF NOT EXISTS ai_employees (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  role TEXT,
  role_id UUID REFERENCES ai_employee_roles(id) ON DELETE SET NULL,
  job_description TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  name TEXT,
  email TEXT,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE(organization_id, user_id)
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT now()
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  source TEXT,
  uploaded_at TIMESTAMP DEFAULT now()
);

-- Chunks table (with vector embeddings)
CREATE TABLE IF NOT EXISTS chunks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  embedding VECTOR(1536),
  source TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

-- Tools table
CREATE TABLE IF NOT EXISTS tools (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  schema JSONB,
  endpoint TEXT,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE(organization_id, name)
);

-- Tool execution history
CREATE TABLE IF NOT EXISTS tool_executions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  input_params JSONB,
  output_result JSONB,
  status TEXT,
  error_message TEXT,
  latency_ms INT,
  executed_at TIMESTAMP DEFAULT now()
);

-- Background jobs tracking
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  task_name TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  payload JSONB,
  result JSONB,
  error TEXT,
  created_at TIMESTAMP DEFAULT now(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);

-- API logs
CREATE TABLE IF NOT EXISTS api_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  endpoint TEXT,
  method TEXT,
  status_code INT,
  latency_ms INT,
  logged_at TIMESTAMP DEFAULT now()
);

-- Error logs
CREATE TABLE IF NOT EXISTS error_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  error_message TEXT,
  error_type TEXT,
  stack_trace TEXT,
  logged_at TIMESTAMP DEFAULT now()
);

-- LLM calls tracking
CREATE TABLE IF NOT EXISTS llm_calls (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID REFERENCES ai_employees(id) ON DELETE CASCADE,
  model TEXT,
  prompt_tokens INT,
  completion_tokens INT,
  total_tokens INT,
  latency_ms INT,
  cost_usd FLOAT,
  called_at TIMESTAMP DEFAULT now()
);

-- Conversation embeddings (for semantic memory)
CREATE TABLE IF NOT EXISTS conversation_embeddings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  embedding VECTOR(1536),
  summary TEXT,
  topics TEXT[] DEFAULT ARRAY[]::TEXT[],
  conversation_id UUID,
  created_at TIMESTAMP DEFAULT now()
);

-- RBAC: Tool information
CREATE TABLE IF NOT EXISTS rbac_tools (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tool_name TEXT UNIQUE NOT NULL,
  description TEXT,
  category TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- RBAC: Role to tool permissions
CREATE TABLE IF NOT EXISTS role_tool_permissions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  role_id UUID NOT NULL REFERENCES ai_employee_roles(id) ON DELETE CASCADE,
  tool_name TEXT NOT NULL,
  allowed BOOLEAN DEFAULT FALSE,
  reason TEXT,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE(role_id, tool_name)
);

-- User to AI Employee assignments
CREATE TABLE IF NOT EXISTS user_ai_employee_assignments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE(user_id, ai_employee_id)
);

-- RBAC Access attempts (audit log)
CREATE TABLE IF NOT EXISTS rbac_access_attempts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  user_id TEXT,
  ai_employee_id UUID REFERENCES ai_employees(id) ON DELETE CASCADE,
  tool_name TEXT,
  allowed BOOLEAN,
  reason TEXT,
  attempted_at TIMESTAMP DEFAULT now()
);

-- Tool verification: Emails sent
CREATE TABLE IF NOT EXISTS emails_sent (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  to_email TEXT,
  subject TEXT,
  body TEXT,
  sent_at TIMESTAMP DEFAULT now()
);

-- Tool verification: CRM leads
CREATE TABLE IF NOT EXISTS crm_leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  company_name TEXT,
  contact_name TEXT,
  email TEXT,
  phone TEXT,
  status TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- Tool verification: Support tickets
CREATE TABLE IF NOT EXISTS support_tickets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  ticket_id TEXT,
  customer_email TEXT,
  subject TEXT,
  description TEXT,
  priority TEXT,
  status TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- Tool verification: Calendar events
CREATE TABLE IF NOT EXISTS calendar_events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  title TEXT,
  description TEXT,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  attendee_email TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- Tool verification: Equipment orders
CREATE TABLE IF NOT EXISTS equipment_orders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  item_name TEXT,
  quantity INT,
  cost_usd FLOAT,
  delivery_date DATE,
  status TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- ============================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_conversations_org_ai_user ON conversations(organization_id, ai_employee_id, user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX IF NOT EXISTS idx_chunks_organization ON chunks(organization_id);
CREATE INDEX IF NOT EXISTS idx_documents_organization ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_ai_employees_organization ON ai_employees(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_org_ai_user ON tool_executions(organization_id, ai_employee_id, user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_org_ai_user ON conversation_embeddings(organization_id, ai_employee_id, user_id);
CREATE INDEX IF NOT EXISTS idx_llm_calls_organization ON llm_calls(organization_id);
