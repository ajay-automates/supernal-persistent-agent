-- Tools registry (per organization)
CREATE TABLE tools (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  schema JSONB,
  endpoint TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- Tool executions log
CREATE TABLE tool_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  ai_employee_id UUID NOT NULL,
  user_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  input_params JSONB,
  output_result JSONB,
  status TEXT,  -- 'pending', 'success', 'failed'
  error_message TEXT,
  latency_ms INTEGER,
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_tool_executions_org_agent ON tool_executions(organization_id, ai_employee_id);
