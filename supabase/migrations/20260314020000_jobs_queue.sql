-- Background job queue: tracks all async task executions
CREATE TABLE jobs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID,
  task_type     TEXT NOT NULL,
  payload       JSONB,
  status        TEXT NOT NULL DEFAULT 'pending',  -- pending, running, done, failed
  result        JSONB,
  error_message TEXT,
  created_at    TIMESTAMP DEFAULT now(),
  started_at    TIMESTAMP,
  completed_at  TIMESTAMP
);

CREATE INDEX idx_jobs_status     ON jobs(status, created_at DESC);
CREATE INDEX idx_jobs_org        ON jobs(organization_id, created_at DESC);
CREATE INDEX idx_jobs_task_type  ON jobs(task_type);
