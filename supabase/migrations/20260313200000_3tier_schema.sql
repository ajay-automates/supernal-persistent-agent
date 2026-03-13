-- 3-Tier Multi-Tenant Schema
-- Organization → AI Employees → Users → Conversations
-- All shared documents live at the organization level

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- DROP OLD TABLES (safe for fresh project)
-- ============================================================
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================
-- TIER 1: ORGANIZATIONS
-- ============================================================
DROP TABLE IF EXISTS organization_chunks CASCADE;
DROP TABLE IF EXISTS organization_documents CASCADE;
DROP TABLE IF EXISTS ai_employees CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

CREATE TABLE organizations (
  id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name         TEXT NOT NULL,
  created_at   TIMESTAMP DEFAULT now()
);

-- ============================================================
-- TIER 2: AI EMPLOYEES
-- ============================================================
CREATE TABLE ai_employees (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name             TEXT NOT NULL,
  role             TEXT NOT NULL,
  job_description  TEXT,
  created_at       TIMESTAMP DEFAULT now()
);

-- ============================================================
-- TIER 3: USERS
-- ============================================================
CREATE TABLE users (
  id                   UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id      UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id              TEXT UNIQUE NOT NULL,  -- external text identifier
  name                 TEXT,
  email                TEXT,
  assigned_ai_employees JSONB DEFAULT '[]',
  created_at           TIMESTAMP DEFAULT now()
);

-- ============================================================
-- ORGANIZATION-LEVEL DOCUMENTS (shared across org)
-- ============================================================
CREATE TABLE organization_documents (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  filename         TEXT NOT NULL,
  source           TEXT,
  uploaded_at      TIMESTAMP DEFAULT now()
);

CREATE TABLE organization_chunks (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  text             TEXT NOT NULL,
  embedding        VECTOR(1536),
  source           TEXT NOT NULL,
  created_at       TIMESTAMP DEFAULT now()
);

-- ============================================================
-- CONVERSATIONS (triple-keyed: org + ai_employee + user)
-- ============================================================
CREATE TABLE conversations (
  id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ai_employee_id   UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  user_id          TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role             TEXT NOT NULL,
  content          TEXT NOT NULL,
  timestamp        TIMESTAMP DEFAULT now()
);

-- ============================================================
-- VECTOR SEARCH RPC FUNCTIONS
-- ============================================================

-- Search organization-level shared chunks
CREATE OR REPLACE FUNCTION search_organization_chunks(
  p_organization_id  UUID,
  p_query_embedding  VECTOR(1536),
  p_match_count      INT
) RETURNS TABLE(
  id               UUID,
  organization_id  UUID,
  text             TEXT,
  source           TEXT,
  similarity       FLOAT8
) AS $$
  SELECT
    organization_chunks.id,
    organization_chunks.organization_id,
    organization_chunks.text,
    organization_chunks.source,
    1 - (organization_chunks.embedding <=> p_query_embedding) AS similarity
  FROM organization_chunks
  WHERE organization_chunks.organization_id = p_organization_id
  ORDER BY organization_chunks.embedding <=> p_query_embedding
  LIMIT p_match_count;
$$ LANGUAGE SQL;

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_ai_employees_org_id       ON ai_employees(organization_id);
CREATE INDEX idx_users_org_id              ON users(organization_id);
CREATE INDEX idx_users_user_id             ON users(user_id);
CREATE INDEX idx_org_documents_org_id      ON organization_documents(organization_id);
CREATE INDEX idx_org_chunks_org_id         ON organization_chunks(organization_id);
CREATE INDEX idx_conversations_org_id      ON conversations(organization_id);
CREATE INDEX idx_conversations_ai_emp_id   ON conversations(ai_employee_id);
CREATE INDEX idx_conversations_user_id     ON conversations(user_id);
CREATE INDEX idx_conversations_triple      ON conversations(organization_id, ai_employee_id, user_id);
