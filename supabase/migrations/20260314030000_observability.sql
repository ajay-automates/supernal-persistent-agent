-- Observability: track API calls, LLM usage, and errors

-- API request logs (org nullable — middleware may not have it)
CREATE TABLE api_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID,
  endpoint        TEXT,
  method          TEXT,
  status_code     INTEGER,
  latency_ms      INTEGER,
  error_message   TEXT,
  created_at      TIMESTAMP DEFAULT now()
);

-- LLM call metrics (token counts + cost per call)
CREATE TABLE llm_metrics (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id   UUID NOT NULL,
  ai_employee_id    UUID NOT NULL,
  model             TEXT,
  prompt_tokens     INTEGER,
  completion_tokens INTEGER,
  total_tokens      INTEGER,
  latency_ms        INTEGER,
  cost_usd          NUMERIC(12, 8),
  created_at        TIMESTAMP DEFAULT now()
);

-- Error log
CREATE TABLE error_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID,
  error_type      TEXT,
  error_message   TEXT,
  stack_trace     TEXT,
  created_at      TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_api_logs_created   ON api_logs(created_at DESC);
CREATE INDEX idx_llm_metrics_org    ON llm_metrics(organization_id, created_at DESC);
CREATE INDEX idx_error_logs_created ON error_logs(created_at DESC);
