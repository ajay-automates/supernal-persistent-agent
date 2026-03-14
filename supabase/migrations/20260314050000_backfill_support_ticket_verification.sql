-- Backfill historical support-ticket tool executions into the verification table.
INSERT INTO mock_support_tickets (
  organization_id,
  ticket_id,
  customer_email,
  issue_type,
  description,
  priority,
  status,
  assigned_to,
  created_at,
  updated_at
)
SELECT DISTINCT ON ((output_result->>'ticket_id'))
  organization_id,
  output_result->>'ticket_id' AS ticket_id,
  COALESCE(input_params->>'customer_email', (input_params->>'customer_id') || '@example.com') AS customer_email,
  COALESCE(output_result->>'issue_type', input_params->>'issue_type', 'general') AS issue_type,
  COALESCE(input_params->>'description', output_result->>'description_preview', '') AS description,
  COALESCE(output_result->>'priority', input_params->>'priority', 'medium') AS priority,
  'open' AS status,
  COALESCE(output_result->>'assigned_team', 'support_team') AS assigned_to,
  COALESCE((output_result->>'created_at')::timestamp, created_at) AS created_at,
  created_at AS updated_at
FROM tool_executions
WHERE tool_name = 'create_support_ticket'
  AND status = 'success'
  AND output_result ? 'ticket_id'
ON CONFLICT (ticket_id) DO NOTHING;
