-- Semantic memory: embed conversation turns for similarity-based retrieval
CREATE TABLE conversation_embeddings (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id  UUID NOT NULL,
  ai_employee_id   UUID NOT NULL,
  user_id          TEXT NOT NULL,
  conversation_id  UUID REFERENCES conversations(id) ON DELETE CASCADE,
  embedding        VECTOR(1536),
  summary          TEXT,
  topics           JSONB,
  created_at       TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_conversation_embeddings_org_agent_user
  ON conversation_embeddings(organization_id, ai_employee_id, user_id);

-- RPC: vector similarity search over a user's conversation history
CREATE OR REPLACE FUNCTION search_memory(
  p_organization_id  UUID,
  p_ai_employee_id   UUID,
  p_user_id          TEXT,
  p_query_embedding  VECTOR(1536),
  p_match_count      INT DEFAULT 5
) RETURNS TABLE(
  conversation_id  UUID,
  summary          TEXT,
  topics           JSONB,
  similarity       FLOAT8
) AS $$
  SELECT
    conversation_id,
    summary,
    topics,
    1 - (embedding <=> p_query_embedding) AS similarity
  FROM conversation_embeddings
  WHERE organization_id = p_organization_id
    AND ai_employee_id  = p_ai_employee_id
    AND user_id         = p_user_id
  ORDER BY embedding <=> p_query_embedding
  LIMIT p_match_count;
$$ LANGUAGE SQL STABLE;
