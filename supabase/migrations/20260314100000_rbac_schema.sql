-- RBAC for AI employees
-- Adds role catalog, tool permission matrix, user-to-agent assignments,
-- and access attempt auditing.

CREATE TABLE IF NOT EXISTS ai_employee_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_name TEXT UNIQUE NOT NULL,
  role_category TEXT NOT NULL,
  description TEXT NOT NULL,
  job_description TEXT NOT NULL,
  icon TEXT,
  example_task TEXT,
  created_at TIMESTAMP DEFAULT now()
);

ALTER TABLE ai_employees
ADD COLUMN IF NOT EXISTS role_id UUID REFERENCES ai_employee_roles(id);

CREATE TABLE IF NOT EXISTS rbac_tools (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tool_name TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS role_tool_permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_id UUID NOT NULL REFERENCES ai_employee_roles(id) ON DELETE CASCADE,
  tool_name TEXT NOT NULL REFERENCES rbac_tools(tool_name) ON DELETE CASCADE,
  allowed BOOLEAN NOT NULL,
  reason TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE(role_id, tool_name)
);

CREATE TABLE IF NOT EXISTS user_ai_employee_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  assigned_at TIMESTAMP DEFAULT now(),
  UNIQUE(organization_id, user_id, ai_employee_id)
);

CREATE TABLE IF NOT EXISTS tool_access_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  ai_employee_id UUID NOT NULL REFERENCES ai_employees(id) ON DELETE CASCADE,
  tool_name TEXT NOT NULL,
  allowed BOOLEAN NOT NULL,
  reason TEXT,
  attempted_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_employees_role_id
ON ai_employees(role_id);

CREATE INDEX IF NOT EXISTS idx_role_tool_permissions_role
ON role_tool_permissions(role_id);

CREATE INDEX IF NOT EXISTS idx_role_tool_permissions_tool
ON role_tool_permissions(tool_name);

CREATE INDEX IF NOT EXISTS idx_user_assignments_org
ON user_ai_employee_assignments(organization_id);

CREATE INDEX IF NOT EXISTS idx_user_assignments_user
ON user_ai_employee_assignments(user_id);

CREATE INDEX IF NOT EXISTS idx_user_assignments_agent
ON user_ai_employee_assignments(ai_employee_id);

CREATE INDEX IF NOT EXISTS idx_tool_access_org
ON tool_access_attempts(organization_id);

CREATE INDEX IF NOT EXISTS idx_tool_access_user
ON tool_access_attempts(user_id);

INSERT INTO ai_employee_roles (
  role_name, role_category, description, job_description, example_task
)
VALUES
  (
    'Sales Development Rep (SDR)', 'Sales',
    'AI-powered sales prospecting and lead generation',
    'Research target accounts and decision makers. Write personalized cold emails and LinkedIn outreach. Qualify leads, add them to CRM, and schedule discovery calls.',
    'Research a prospect, send outreach, add lead to CRM, and book a meeting'
  ),
  (
    'Customer Support Agent', 'Support',
    'AI-powered customer service across email, chat, and phone',
    'Handle customer inquiries, search knowledge sources, verify account details, create support tickets, and escalate when needed.',
    'Investigate a billing issue, check the account, and create a support ticket'
  ),
  (
    'Finance Coordinator', 'BackOffice',
    'AI-powered accounting and financial operations',
    'Reconcile invoices, update records, generate reports, monitor transactions, and flag discrepancies.',
    'Generate an invoice and prepare a monthly finance report'
  ),
  (
    'Operations Coordinator', 'BackOffice',
    'AI-powered operations and workflow management',
    'Coordinate deliveries, manage vendors, update operational data, and optimize internal workflows.',
    'Update inventory, schedule a delivery, and notify a vendor'
  ),
  (
    'Social Media Manager', 'Marketing',
    'AI-powered social media strategy and publishing',
    'Create, schedule, and analyze social media content while maintaining brand voice.',
    'Draft and schedule posts, then review engagement metrics'
  ),
  (
    'Content Creator', 'Marketing',
    'AI-powered content writing and campaign support',
    'Write blog posts, ad copy, and campaign content while managing a content calendar.',
    'Write a blog post and draft copy for an email campaign'
  ),
  (
    'Dispatch Manager', 'Operations',
    'AI-powered field dispatch and routing',
    'Dispatch crews, optimize routes, and coordinate field service schedules.',
    'Dispatch technicians and optimize the route for today''s jobs'
  ),
  (
    'Customer Scheduler', 'Operations',
    'AI-powered appointment scheduling and rescheduling',
    'Manage customer appointments, availability, reminders, and schedule changes.',
    'Book an appointment and handle a reschedule request'
  ),
  (
    'Insurance Claims Processor', 'Insurance',
    'AI-powered claims intake and processing',
    'Create claim intakes, verify coverage, detect fraud signals, generate quotes, and route cases to adjusters.',
    'Process a claim, verify coverage, and route it for review'
  ),
  (
    'Insurance Underwriter Assistant', 'Insurance',
    'AI-powered underwriting and risk analysis',
    'Assess risk, analyze coverage, create quotes, and flag complex underwriting cases.',
    'Review an application, assess risk, and generate a quote recommendation'
  ),
  (
    'Recruiter', 'HR',
    'AI-powered recruiting and candidate screening',
    'Screen candidates, source talent, create job postings, schedule interviews, and track the hiring pipeline.',
    'Screen applications and schedule interviews for qualified candidates'
  ),
  (
    'Onboarding Specialist', 'HR',
    'AI-powered employee onboarding and setup',
    'Collect documents, schedule training, set up access, and create onboarding plans.',
    'Collect new hire documents and schedule onboarding training'
  )
ON CONFLICT (role_name) DO NOTHING;

INSERT INTO rbac_tools (tool_name, description, category)
VALUES
  ('send_email', 'Send emails to prospects, customers, or teammates', 'Communication'),
  ('send_notification', 'Send internal or customer notifications', 'Communication'),
  ('search_web', 'Research companies and people on the web', 'Sales'),
  ('add_lead_to_crm', 'Add a prospect or lead to CRM', 'Sales'),
  ('query_crm', 'Query CRM data for leads and accounts', 'Sales'),
  ('schedule_meeting', 'Schedule meetings and discovery calls', 'Sales'),
  ('search_knowledge_base', 'Search the support knowledge base', 'Support'),
  ('create_support_ticket', 'Create and escalate support tickets', 'Support'),
  ('check_account_status', 'Look up customer account details', 'Support'),
  ('create_invoice', 'Generate invoices for customers', 'Finance'),
  ('query_database', 'Query operational or financial data', 'Operations'),
  ('update_database', 'Update records in the operational data store', 'Operations'),
  ('generate_report', 'Generate financial or operational reports', 'Finance'),
  ('schedule_delivery', 'Coordinate a delivery', 'Operations'),
  ('notify_vendor', 'Contact a vendor or supplier', 'Operations'),
  ('post_social_media', 'Publish content to social media', 'Marketing'),
  ('schedule_post', 'Schedule a social media post', 'Marketing'),
  ('analyze_metrics', 'Analyze campaign or engagement performance', 'Marketing'),
  ('generate_content', 'Generate marketing copy or content', 'Marketing'),
  ('write_blog_post', 'Write a blog post or article', 'Marketing'),
  ('create_ad_copy', 'Create ad copy for campaigns', 'Marketing'),
  ('generate_email_campaign', 'Generate an email campaign draft', 'Marketing'),
  ('manage_content_calendar', 'Manage the content calendar', 'Marketing'),
  ('dispatch_crew', 'Dispatch field crews to job sites', 'Operations'),
  ('optimize_route', 'Optimize a delivery or service route', 'Operations'),
  ('handle_reschedule', 'Handle appointment rescheduling', 'Operations'),
  ('create_claim_intake', 'Create an insurance claim intake', 'Insurance'),
  ('verify_coverage', 'Verify insurance coverage details', 'Insurance'),
  ('detect_fraud', 'Detect fraud patterns in claims', 'Insurance'),
  ('generate_quote', 'Generate an insurance quote', 'Insurance'),
  ('route_to_adjuster', 'Route a claim to an adjuster', 'Insurance'),
  ('assess_risk', 'Assess underwriting risk', 'Insurance'),
  ('generate_recommendation', 'Generate an underwriting recommendation', 'Insurance'),
  ('create_quote', 'Create a policy quote', 'Insurance'),
  ('analyze_coverage', 'Analyze coverage needs', 'Insurance'),
  ('flag_edge_cases', 'Flag complex underwriting or claim cases', 'Insurance'),
  ('screen_candidates', 'Screen candidates automatically', 'HR'),
  ('schedule_interview', 'Schedule a candidate interview', 'HR'),
  ('create_job_posting', 'Create and post an open role', 'HR'),
  ('source_candidates', 'Source candidates from external channels', 'HR'),
  ('track_pipeline', 'Track applicants through the hiring pipeline', 'HR'),
  ('collect_documents', 'Collect onboarding documents', 'HR'),
  ('schedule_training', 'Schedule training sessions', 'HR'),
  ('setup_access', 'Set up access for a new hire', 'HR'),
  ('create_onboarding_plan', 'Create an onboarding plan', 'HR'),
  ('process_leave_request', 'Process a leave request', 'HR'),
  ('order_equipment', 'Order equipment for an employee', 'HR'),
  ('schedule_meeting_room', 'Reserve a meeting room or resource', 'HR')
ON CONFLICT (tool_name) DO NOTHING;

WITH permissions(role_name, tool_name, allowed, reason) AS (
  VALUES
    ('Sales Development Rep (SDR)', 'send_email', TRUE, 'SDRs send outreach emails'),
    ('Sales Development Rep (SDR)', 'search_web', TRUE, 'SDRs research prospects'),
    ('Sales Development Rep (SDR)', 'add_lead_to_crm', TRUE, 'SDRs add leads to CRM'),
    ('Sales Development Rep (SDR)', 'query_crm', TRUE, 'SDRs look up existing leads'),
    ('Sales Development Rep (SDR)', 'schedule_meeting', TRUE, 'SDRs book meetings'),
    ('Sales Development Rep (SDR)', 'send_notification', TRUE, 'SDRs notify the sales team'),

    ('Customer Support Agent', 'search_knowledge_base', TRUE, 'Support agents search help articles'),
    ('Customer Support Agent', 'create_support_ticket', TRUE, 'Support agents escalate issues'),
    ('Customer Support Agent', 'check_account_status', TRUE, 'Support agents verify accounts'),
    ('Customer Support Agent', 'send_email', TRUE, 'Support agents email customers'),
    ('Customer Support Agent', 'send_notification', TRUE, 'Support agents send follow-ups'),

    ('Finance Coordinator', 'create_invoice', TRUE, 'Finance creates invoices'),
    ('Finance Coordinator', 'query_database', TRUE, 'Finance queries records'),
    ('Finance Coordinator', 'update_database', TRUE, 'Finance updates records'),
    ('Finance Coordinator', 'generate_report', TRUE, 'Finance generates reports'),
    ('Finance Coordinator', 'send_notification', TRUE, 'Finance sends internal alerts'),

    ('Operations Coordinator', 'query_database', TRUE, 'Operations queries operational data'),
    ('Operations Coordinator', 'update_database', TRUE, 'Operations updates records'),
    ('Operations Coordinator', 'schedule_delivery', TRUE, 'Operations schedules deliveries'),
    ('Operations Coordinator', 'notify_vendor', TRUE, 'Operations coordinates vendors'),
    ('Operations Coordinator', 'send_notification', TRUE, 'Operations notifies the team'),

    ('Social Media Manager', 'post_social_media', TRUE, 'Social managers publish posts'),
    ('Social Media Manager', 'schedule_post', TRUE, 'Social managers schedule posts'),
    ('Social Media Manager', 'analyze_metrics', TRUE, 'Social managers review performance'),
    ('Social Media Manager', 'generate_content', TRUE, 'Social managers draft content'),
    ('Social Media Manager', 'send_notification', TRUE, 'Social managers notify stakeholders'),

    ('Content Creator', 'write_blog_post', TRUE, 'Content creators write blog posts'),
    ('Content Creator', 'create_ad_copy', TRUE, 'Content creators draft ad copy'),
    ('Content Creator', 'generate_email_campaign', TRUE, 'Content creators draft campaigns'),
    ('Content Creator', 'manage_content_calendar', TRUE, 'Content creators manage calendars'),
    ('Content Creator', 'generate_content', TRUE, 'Content creators generate content'),

    ('Dispatch Manager', 'dispatch_crew', TRUE, 'Dispatch manages crews'),
    ('Dispatch Manager', 'optimize_route', TRUE, 'Dispatch optimizes routes'),
    ('Dispatch Manager', 'update_database', TRUE, 'Dispatch updates job data'),
    ('Dispatch Manager', 'send_notification', TRUE, 'Dispatch notifies technicians'),
    ('Dispatch Manager', 'query_database', TRUE, 'Dispatch queries schedules'),

    ('Customer Scheduler', 'schedule_meeting', TRUE, 'Schedulers book appointments'),
    ('Customer Scheduler', 'handle_reschedule', TRUE, 'Schedulers handle changes'),
    ('Customer Scheduler', 'send_notification', TRUE, 'Schedulers send reminders'),
    ('Customer Scheduler', 'query_database', TRUE, 'Schedulers check availability'),
    ('Customer Scheduler', 'update_database', TRUE, 'Schedulers update schedules'),

    ('Insurance Claims Processor', 'create_claim_intake', TRUE, 'Claims processors intake claims'),
    ('Insurance Claims Processor', 'verify_coverage', TRUE, 'Claims processors verify coverage'),
    ('Insurance Claims Processor', 'detect_fraud', TRUE, 'Claims processors check fraud risk'),
    ('Insurance Claims Processor', 'generate_quote', TRUE, 'Claims processors generate quotes'),
    ('Insurance Claims Processor', 'route_to_adjuster', TRUE, 'Claims processors route cases'),

    ('Insurance Underwriter Assistant', 'assess_risk', TRUE, 'Underwriters assess risk'),
    ('Insurance Underwriter Assistant', 'generate_recommendation', TRUE, 'Underwriters recommend decisions'),
    ('Insurance Underwriter Assistant', 'create_quote', TRUE, 'Underwriters create quotes'),
    ('Insurance Underwriter Assistant', 'analyze_coverage', TRUE, 'Underwriters analyze coverage'),
    ('Insurance Underwriter Assistant', 'flag_edge_cases', TRUE, 'Underwriters flag edge cases'),

    ('Recruiter', 'screen_candidates', TRUE, 'Recruiters screen candidates'),
    ('Recruiter', 'schedule_interview', TRUE, 'Recruiters schedule interviews'),
    ('Recruiter', 'create_job_posting', TRUE, 'Recruiters create job posts'),
    ('Recruiter', 'source_candidates', TRUE, 'Recruiters source talent'),
    ('Recruiter', 'track_pipeline', TRUE, 'Recruiters track the hiring pipeline'),

    ('Onboarding Specialist', 'collect_documents', TRUE, 'Onboarding specialists collect documents'),
    ('Onboarding Specialist', 'schedule_training', TRUE, 'Onboarding specialists schedule training'),
    ('Onboarding Specialist', 'setup_access', TRUE, 'Onboarding specialists set up access'),
    ('Onboarding Specialist', 'create_onboarding_plan', TRUE, 'Onboarding specialists create plans'),
    ('Onboarding Specialist', 'send_notification', TRUE, 'Onboarding specialists notify stakeholders')
)
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT roles.id, tools.tool_name, COALESCE(perms.allowed, FALSE), COALESCE(perms.reason, 'Denied by default for this role')
FROM ai_employee_roles roles
CROSS JOIN rbac_tools tools
LEFT JOIN permissions perms
  ON perms.role_name = roles.role_name
 AND perms.tool_name = tools.tool_name
ON CONFLICT (role_id, tool_name) DO NOTHING;

UPDATE ai_employees
SET role_id = roles.id
FROM ai_employee_roles roles
WHERE ai_employees.role_id IS NULL
  AND (
    ai_employees.role = roles.role_name
    OR (ai_employees.role = 'Sales Development Representative' AND roles.role_name = 'Sales Development Rep (SDR)')
    OR (ai_employees.role = 'Level 1 Customer Support' AND roles.role_name = 'Customer Support Agent')
    OR (ai_employees.role = 'Technical Support Engineer' AND roles.role_name = 'Customer Support Agent')
    OR (ai_employees.role = 'Account Manager' AND roles.role_name = 'Sales Development Rep (SDR)')
  );

INSERT INTO user_ai_employee_assignments (organization_id, user_id, ai_employee_id)
SELECT DISTINCT users.organization_id, users.user_id, ai_emp_id::UUID
FROM users
CROSS JOIN LATERAL jsonb_array_elements_text(COALESCE(users.assigned_ai_employees, '[]'::jsonb)) AS ai_emp(ai_emp_id)
JOIN ai_employees ON ai_employees.id = ai_emp.ai_emp_id::UUID
ON CONFLICT (organization_id, user_id, ai_employee_id) DO NOTHING;
