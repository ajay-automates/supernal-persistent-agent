-- ============================================================================
-- SUPERNAL AI EMPLOYEES - COMPLETE ROLE-BASED ACCESS CONTROL SYSTEM
-- ============================================================================
-- This schema implements Supernal's actual 12 AI employee roles with
-- complete role-based access control (RBAC) for tools and users.
-- ============================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- TIER 1: AI EMPLOYEE ROLES (Supernal's 12 actual roles)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_employee_roles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  role_name TEXT UNIQUE NOT NULL,
  role_category TEXT NOT NULL,  -- Sales, Support, BackOffice, Marketing, Operations, Insurance, HR
  description TEXT NOT NULL,
  job_description TEXT NOT NULL,
  icon TEXT,
  example_task TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- Insert Supernal's 12 actual AI employee roles
INSERT INTO ai_employee_roles 
  (role_name, role_category, description, job_description, example_task) 
VALUES
  -- CATEGORY 1: SALES & PROSPECTING (1 role)
  ('Sales Development Rep (SDR)', 'Sales', 
   'AI-powered sales prospecting and lead generation',
   'Research target accounts and decision makers. Write personalized cold emails and LinkedIn outreach. Qualify leads and score prospects. Schedule discovery calls. Track prospect engagement and follow up systematically.',
   'Research john@techcorp.com, send personalized email about Q2 offering, add to CRM, schedule discovery call'),

  -- CATEGORY 2: CUSTOMER SUPPORT (1 role)
  ('Customer Support Agent', 'Support',
   'AI-powered customer service across email, chat, phone',
   'Handle customer inquiries across email, chat, and phone. Classify issues, search knowledge base, provide solutions. Escalate complex issues to humans. Track customer satisfaction and resolution time.',
   'Customer reports billing issue, search KB, create support ticket, notify team'),

  -- CATEGORY 3: BACK-OFFICE ADMINISTRATION (2 roles)
  ('Finance Coordinator', 'BackOffice',
   'AI-powered accounting and financial management',
   'Reconcile invoices and bank statements. Categorize expenses. Prepare financial reports. Monitor cash flow. Flag discrepancies for human review.',
   'Reconcile March invoices, prepare monthly P&L, identify duplicate charges'),

  ('Operations Coordinator', 'BackOffice',
   'AI-powered operations and workflow management',
   'Schedule and coordinate deliveries. Manage warehouse operations. Track inventory. Coordinate with vendors. Optimize resource allocation.',
   'Schedule delivery for 5 customers, update inventory, notify vendors of delays'),

  -- CATEGORY 4: MARKETING & CONTENT (2 roles)
  ('Social Media Manager', 'Marketing',
   'AI-powered social media marketing and content strategy',
   'Learn and replicate brand voice. Create engaging social media posts. Plan marketing campaigns. Schedule content across platforms. Analyze engagement metrics.',
   'Create 3 TikTok posts in brand voice, schedule for optimal times, analyze performance'),

  ('Content Creator', 'Marketing',
   'AI-powered blog, email, and ad copy creation',
   'Write blog posts and articles. Create ad copy and landing pages. Develop email campaigns. Manage content calendar. Optimize for SEO.',
   'Write 2 blog posts, create email campaign copy, update content calendar'),

  -- CATEGORY 5: OPERATIONS & LOGISTICS (2 roles)
  ('Dispatch Manager', 'Operations',
   'AI-powered field service dispatch and routing',
   'Dispatch field crews to job sites. Optimize routing. Manage service schedules. Track technician locations. Handle dynamic job assignments.',
   'Dispatch 3 technicians to HVAC jobs, optimize routes, send location updates'),

  ('Customer Scheduler', 'Operations',
   'AI-powered appointment scheduling and coordination',
   'Answer customer calls and inquiries. Schedule appointments. Manage availability calendars. Send appointment reminders. Handle cancellations and rescheduling.',
   'Answer 10 customer calls, schedule appointments, send reminders'),

  -- CATEGORY 6: INDUSTRY-SPECIFIC - INSURANCE (2 roles)
  ('Insurance Claims Processor', 'Insurance',
   'AI-powered insurance claims intake and processing',
   'Receive and process claims. Generate quotes. Verify coverage. Detect fraud indicators. Route claims to adjusters. Manage claim timeline.',
   'Process claim, verify coverage, detect fraud patterns, route to adjuster'),

  ('Insurance Underwriter Assistant', 'Insurance',
   'AI-powered insurance risk assessment and underwriting',
   'Assess risk from applications. Generate underwriting recommendations. Analyze coverage needs. Create policy quotes. Flag edge cases for human review.',
   'Review application, assess risk, generate underwriting recommendation'),

  -- CATEGORY 7: INDUSTRY-SPECIFIC - HR/RECRUITING (2 roles)
  ('Recruiter', 'HR',
   'AI-powered candidate screening and recruitment',
   'Screen candidates automatically. Schedule interviews. Create job postings. Source candidates from multiple channels. Track applicants through pipeline.',
   'Screen 50 applications, schedule 5 interviews, source candidates from LinkedIn'),

  ('Onboarding Specialist', 'HR',
   'AI-powered employee onboarding and setup',
   'Collect onboarding documents. Schedule training sessions. Set up system access. Create onboarding timeline. Answer new hire questions.',
   'Collect onboarding docs, schedule training, setup access, create timeline');


-- ============================================================================
-- TIER 2: TOOLS (All available tools in the system)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tools (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tool_name TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL,  -- Email, CRM, Support, HR, etc.
  created_at TIMESTAMP DEFAULT now()
);

-- Insert all tools
INSERT INTO tools (tool_name, description, category) VALUES
  -- COMMUNICATION TOOLS
  ('send_email', 'Send emails to prospects, customers, team members', 'Communication'),
  ('send_notification', 'Send internal team notifications', 'Communication'),

  -- SALES/CRM TOOLS
  ('search_web', 'Research companies and prospects on the web', 'Sales'),
  ('add_lead_to_crm', 'Add prospect to CRM system (Salesforce)', 'Sales'),
  ('query_crm', 'Query existing leads and accounts in CRM', 'Sales'),
  ('schedule_meeting', 'Schedule meetings and discovery calls', 'Sales'),

  -- SUPPORT TOOLS
  ('search_knowledge_base', 'Search support knowledge base for solutions', 'Support'),
  ('create_support_ticket', 'Create and escalate support tickets', 'Support'),
  ('check_account_status', 'Check customer account status and history', 'Support'),

  -- BACK-OFFICE TOOLS
  ('create_invoice', 'Generate invoices for customers', 'Finance'),
  ('query_database', 'Query databases for operational data', 'Operations'),
  ('update_database', 'Update inventory, schedules, and operational data', 'Operations'),
  ('generate_report', 'Generate financial and operational reports', 'Finance'),
  ('schedule_delivery', 'Schedule deliveries with vendors', 'Operations'),
  ('notify_vendor', 'Send notifications to vendors and suppliers', 'Operations'),

  -- MARKETING TOOLS
  ('post_social_media', 'Post content to social media platforms', 'Marketing'),
  ('schedule_post', 'Schedule social media posts for future posting', 'Marketing'),
  ('analyze_metrics', 'Analyze engagement and performance metrics', 'Marketing'),
  ('generate_content', 'Generate marketing copy and content', 'Marketing'),
  ('write_blog_post', 'Write blog posts and articles', 'Marketing'),
  ('create_ad_copy', 'Create ad copy for marketing campaigns', 'Marketing'),
  ('generate_email_campaign', 'Generate email campaign content', 'Marketing'),
  ('manage_content_calendar', 'Manage content calendar and scheduling', 'Marketing'),

  -- OPERATIONS & LOGISTICS TOOLS
  ('dispatch_crew', 'Dispatch field crews to job sites', 'Operations'),
  ('optimize_route', 'Optimize delivery and service routes', 'Operations'),
  ('handle_reschedule', 'Handle appointment rescheduling', 'Operations'),

  -- INSURANCE TOOLS
  ('create_claim_intake', 'Create and receive insurance claims', 'Insurance'),
  ('verify_coverage', 'Verify insurance coverage and policy details', 'Insurance'),
  ('detect_fraud', 'Detect fraud patterns in claims', 'Insurance'),
  ('generate_quote', 'Generate insurance quotes', 'Insurance'),
  ('route_to_adjuster', 'Route claims to adjusters', 'Insurance'),
  ('assess_risk', 'Assess risk from insurance applications', 'Insurance'),
  ('generate_recommendation', 'Generate underwriting recommendations', 'Insurance'),
  ('create_quote', 'Create policy quotes', 'Insurance'),
  ('analyze_coverage', 'Analyze insurance coverage needs', 'Insurance'),
  ('flag_edge_cases', 'Flag complex/edge case claims', 'Insurance'),

  -- HR/RECRUITING TOOLS
  ('screen_candidates', 'Screen candidates automatically', 'HR'),
  ('schedule_interview', 'Schedule candidate interviews', 'HR'),
  ('create_job_posting', 'Create and post job openings', 'HR'),
  ('source_candidates', 'Source candidates from multiple channels', 'HR'),
  ('track_pipeline', 'Track applicants through hiring pipeline', 'HR'),
  ('collect_documents', 'Collect onboarding documents', 'HR'),
  ('schedule_training', 'Schedule training sessions', 'HR'),
  ('setup_access', 'Setup system access for new hires', 'HR'),
  ('create_onboarding_plan', 'Create onboarding timeline and plan', 'HR'),
  ('process_leave_request', 'Process employee leave requests', 'HR'),
  ('order_equipment', 'Order equipment for employees', 'HR'),
  ('schedule_meeting_room', 'Schedule conference rooms and resources', 'HR');


-- ============================================================================
-- TIER 3: ROLE-BASED TOOL PERMISSIONS (144 mappings: 12 roles x 12 categories)
-- ============================================================================

CREATE TABLE IF NOT EXISTS role_tool_permissions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  role_id UUID NOT NULL REFERENCES ai_employee_roles(id),
  tool_name TEXT NOT NULL REFERENCES tools(tool_name),
  allowed BOOLEAN NOT NULL,
  reason TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE(role_id, tool_name)
);

-- ============================================================================
-- INSERT ROLE-TOOL PERMISSIONS
-- ============================================================================

-- SALES DEVELOPMENT REP (SDR) - 6 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'send_email', TRUE, 'SDRs send cold outreach emails to prospects'
FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)'
UNION ALL
SELECT id, 'search_web', TRUE, 'SDRs research companies and prospects'
FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)'
UNION ALL
SELECT id, 'add_lead_to_crm', TRUE, 'SDRs add qualified prospects to CRM'
FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)'
UNION ALL
SELECT id, 'query_crm', TRUE, 'SDRs lookup existing leads'
FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)'
UNION ALL
SELECT id, 'schedule_meeting', TRUE, 'SDRs schedule discovery calls'
FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)'
UNION ALL
SELECT id, 'send_notification', TRUE, 'SDRs notify sales team'
FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)';

-- SDR Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Sales tool - not applicable to SDR'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Sales Development Rep (SDR)'
AND tools.tool_name NOT IN ('send_email', 'search_web', 'add_lead_to_crm', 'query_crm', 'schedule_meeting', 'send_notification');


-- CUSTOMER SUPPORT AGENT - 5 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'search_knowledge_base', TRUE, 'Support agents search help docs'
FROM ai_employee_roles WHERE role_name = 'Customer Support Agent'
UNION ALL
SELECT id, 'create_support_ticket', TRUE, 'Support agents escalate to humans'
FROM ai_employee_roles WHERE role_name = 'Customer Support Agent'
UNION ALL
SELECT id, 'check_account_status', TRUE, 'Support agents verify customer accounts'
FROM ai_employee_roles WHERE role_name = 'Customer Support Agent'
UNION ALL
SELECT id, 'send_email', TRUE, 'Support agents email customers'
FROM ai_employee_roles WHERE role_name = 'Customer Support Agent'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Support agents notify team'
FROM ai_employee_roles WHERE role_name = 'Customer Support Agent';

-- Support Agent Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not a support responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Customer Support Agent'
AND tools.tool_name NOT IN ('search_knowledge_base', 'create_support_ticket', 'check_account_status', 'send_email', 'send_notification');


-- FINANCE COORDINATOR - 5 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'create_invoice', TRUE, 'Finance creates invoices'
FROM ai_employee_roles WHERE role_name = 'Finance Coordinator'
UNION ALL
SELECT id, 'query_database', TRUE, 'Finance queries financial data'
FROM ai_employee_roles WHERE role_name = 'Finance Coordinator'
UNION ALL
SELECT id, 'update_database', TRUE, 'Finance records transactions'
FROM ai_employee_roles WHERE role_name = 'Finance Coordinator'
UNION ALL
SELECT id, 'generate_report', TRUE, 'Finance generates financial reports'
FROM ai_employee_roles WHERE role_name = 'Finance Coordinator'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Finance notifies team'
FROM ai_employee_roles WHERE role_name = 'Finance Coordinator';

-- Finance Coordinator Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not a finance responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Finance Coordinator'
AND tools.tool_name NOT IN ('create_invoice', 'query_database', 'update_database', 'generate_report', 'send_notification');


-- OPERATIONS COORDINATOR - 5 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'query_database', TRUE, 'Ops queries inventory and schedules'
FROM ai_employee_roles WHERE role_name = 'Operations Coordinator'
UNION ALL
SELECT id, 'update_database', TRUE, 'Ops updates inventory and schedules'
FROM ai_employee_roles WHERE role_name = 'Operations Coordinator'
UNION ALL
SELECT id, 'schedule_delivery', TRUE, 'Ops schedules deliveries'
FROM ai_employee_roles WHERE role_name = 'Operations Coordinator'
UNION ALL
SELECT id, 'notify_vendor', TRUE, 'Ops notifies vendors'
FROM ai_employee_roles WHERE role_name = 'Operations Coordinator'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Ops notifies team'
FROM ai_employee_roles WHERE role_name = 'Operations Coordinator';

-- Operations Coordinator Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not an operations responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Operations Coordinator'
AND tools.tool_name NOT IN ('query_database', 'update_database', 'schedule_delivery', 'notify_vendor', 'send_notification');


-- SOCIAL MEDIA MANAGER - 5 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'post_social_media', TRUE, 'Social manager posts content'
FROM ai_employee_roles WHERE role_name = 'Social Media Manager'
UNION ALL
SELECT id, 'schedule_post', TRUE, 'Social manager schedules posts'
FROM ai_employee_roles WHERE role_name = 'Social Media Manager'
UNION ALL
SELECT id, 'analyze_metrics', TRUE, 'Social manager analyzes engagement'
FROM ai_employee_roles WHERE role_name = 'Social Media Manager'
UNION ALL
SELECT id, 'generate_content', TRUE, 'Social manager generates copy'
FROM ai_employee_roles WHERE role_name = 'Social Media Manager'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Social manager notifies team'
FROM ai_employee_roles WHERE role_name = 'Social Media Manager';

-- Social Media Manager Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not a marketing responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Social Media Manager'
AND tools.tool_name NOT IN ('post_social_media', 'schedule_post', 'analyze_metrics', 'generate_content', 'send_notification');


-- CONTENT CREATOR - 5 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'write_blog_post', TRUE, 'Content creator writes blogs'
FROM ai_employee_roles WHERE role_name = 'Content Creator'
UNION ALL
SELECT id, 'create_ad_copy', TRUE, 'Content creator creates ads'
FROM ai_employee_roles WHERE role_name = 'Content Creator'
UNION ALL
SELECT id, 'generate_email_campaign', TRUE, 'Content creator writes emails'
FROM ai_employee_roles WHERE role_name = 'Content Creator'
UNION ALL
SELECT id, 'manage_content_calendar', TRUE, 'Content creator manages calendar'
FROM ai_employee_roles WHERE role_name = 'Content Creator'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Content creator notifies team'
FROM ai_employee_roles WHERE role_name = 'Content Creator';

-- Content Creator Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not a content responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Content Creator'
AND tools.tool_name NOT IN ('write_blog_post', 'create_ad_copy', 'generate_email_campaign', 'manage_content_calendar', 'send_notification');


-- DISPATCH MANAGER - 5 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'dispatch_crew', TRUE, 'Dispatch manager dispatches crews'
FROM ai_employee_roles WHERE role_name = 'Dispatch Manager'
UNION ALL
SELECT id, 'optimize_route', TRUE, 'Dispatch manager optimizes routes'
FROM ai_employee_roles WHERE role_name = 'Dispatch Manager'
UNION ALL
SELECT id, 'query_database', TRUE, 'Dispatch manager checks schedules'
FROM ai_employee_roles WHERE role_name = 'Dispatch Manager'
UNION ALL
SELECT id, 'update_database', TRUE, 'Dispatch manager updates job status'
FROM ai_employee_roles WHERE role_name = 'Dispatch Manager'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Dispatch manager alerts crew'
FROM ai_employee_roles WHERE role_name = 'Dispatch Manager';

-- Dispatch Manager Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not a dispatch responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Dispatch Manager'
AND tools.tool_name NOT IN ('dispatch_crew', 'optimize_route', 'query_database', 'update_database', 'send_notification');


-- CUSTOMER SCHEDULER - 5 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'schedule_appointment', TRUE, 'Scheduler books appointments'
FROM ai_employee_roles WHERE role_name = 'Customer Scheduler'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Scheduler sends reminders'
FROM ai_employee_roles WHERE role_name = 'Customer Scheduler'
UNION ALL
SELECT id, 'query_database', TRUE, 'Scheduler checks availability'
FROM ai_employee_roles WHERE role_name = 'Customer Scheduler'
UNION ALL
SELECT id, 'send_email', TRUE, 'Scheduler sends confirmations'
FROM ai_employee_roles WHERE role_name = 'Customer Scheduler'
UNION ALL
SELECT id, 'handle_reschedule', TRUE, 'Scheduler handles rescheduling'
FROM ai_employee_roles WHERE role_name = 'Customer Scheduler';

-- Customer Scheduler Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not a scheduling responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Customer Scheduler'
AND tools.tool_name NOT IN ('schedule_appointment', 'send_notification', 'query_database', 'send_email', 'handle_reschedule');


-- INSURANCE CLAIMS PROCESSOR - 6 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'create_claim_intake', TRUE, 'Claims processor receives claims'
FROM ai_employee_roles WHERE role_name = 'Insurance Claims Processor'
UNION ALL
SELECT id, 'verify_coverage', TRUE, 'Claims processor verifies coverage'
FROM ai_employee_roles WHERE role_name = 'Insurance Claims Processor'
UNION ALL
SELECT id, 'detect_fraud', TRUE, 'Claims processor detects fraud'
FROM ai_employee_roles WHERE role_name = 'Insurance Claims Processor'
UNION ALL
SELECT id, 'generate_quote', TRUE, 'Claims processor generates quotes'
FROM ai_employee_roles WHERE role_name = 'Insurance Claims Processor'
UNION ALL
SELECT id, 'route_to_adjuster', TRUE, 'Claims processor routes claims'
FROM ai_employee_roles WHERE role_name = 'Insurance Claims Processor'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Claims processor notifies team'
FROM ai_employee_roles WHERE role_name = 'Insurance Claims Processor';

-- Claims Processor Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not a claims responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Insurance Claims Processor'
AND tools.tool_name NOT IN ('create_claim_intake', 'verify_coverage', 'detect_fraud', 'generate_quote', 'route_to_adjuster', 'send_notification');


-- INSURANCE UNDERWRITER ASSISTANT - 6 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'assess_risk', TRUE, 'Underwriter assesses risk'
FROM ai_employee_roles WHERE role_name = 'Insurance Underwriter Assistant'
UNION ALL
SELECT id, 'generate_recommendation', TRUE, 'Underwriter generates recommendation'
FROM ai_employee_roles WHERE role_name = 'Insurance Underwriter Assistant'
UNION ALL
SELECT id, 'create_quote', TRUE, 'Underwriter creates quotes'
FROM ai_employee_roles WHERE role_name = 'Insurance Underwriter Assistant'
UNION ALL
SELECT id, 'analyze_coverage', TRUE, 'Underwriter analyzes coverage'
FROM ai_employee_roles WHERE role_name = 'Insurance Underwriter Assistant'
UNION ALL
SELECT id, 'flag_edge_cases', TRUE, 'Underwriter flags edge cases'
FROM ai_employee_roles WHERE role_name = 'Insurance Underwriter Assistant'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Underwriter notifies team'
FROM ai_employee_roles WHERE role_name = 'Insurance Underwriter Assistant';

-- Underwriter Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not an underwriting responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Insurance Underwriter Assistant'
AND tools.tool_name NOT IN ('assess_risk', 'generate_recommendation', 'create_quote', 'analyze_coverage', 'flag_edge_cases', 'send_notification');


-- RECRUITER - 7 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'screen_candidates', TRUE, 'Recruiter screens candidates'
FROM ai_employee_roles WHERE role_name = 'Recruiter'
UNION ALL
SELECT id, 'schedule_interview', TRUE, 'Recruiter schedules interviews'
FROM ai_employee_roles WHERE role_name = 'Recruiter'
UNION ALL
SELECT id, 'create_job_posting', TRUE, 'Recruiter creates job postings'
FROM ai_employee_roles WHERE role_name = 'Recruiter'
UNION ALL
SELECT id, 'source_candidates', TRUE, 'Recruiter sources candidates'
FROM ai_employee_roles WHERE role_name = 'Recruiter'
UNION ALL
SELECT id, 'track_pipeline', TRUE, 'Recruiter tracks pipeline'
FROM ai_employee_roles WHERE role_name = 'Recruiter'
UNION ALL
SELECT id, 'send_email', TRUE, 'Recruiter emails candidates'
FROM ai_employee_roles WHERE role_name = 'Recruiter'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Recruiter notifies team'
FROM ai_employee_roles WHERE role_name = 'Recruiter';

-- Recruiter Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not a recruiting responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Recruiter'
AND tools.tool_name NOT IN ('screen_candidates', 'schedule_interview', 'create_job_posting', 'source_candidates', 'track_pipeline', 'send_email', 'send_notification');


-- ONBOARDING SPECIALIST - 6 allowed tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'collect_documents', TRUE, 'Onboarding collects documents'
FROM ai_employee_roles WHERE role_name = 'Onboarding Specialist'
UNION ALL
SELECT id, 'schedule_training', TRUE, 'Onboarding schedules training'
FROM ai_employee_roles WHERE role_name = 'Onboarding Specialist'
UNION ALL
SELECT id, 'setup_access', TRUE, 'Onboarding sets up access'
FROM ai_employee_roles WHERE role_name = 'Onboarding Specialist'
UNION ALL
SELECT id, 'create_onboarding_plan', TRUE, 'Onboarding creates timeline'
FROM ai_employee_roles WHERE role_name = 'Onboarding Specialist'
UNION ALL
SELECT id, 'send_email', TRUE, 'Onboarding emails new hires'
FROM ai_employee_roles WHERE role_name = 'Onboarding Specialist'
UNION ALL
SELECT id, 'send_notification', TRUE, 'Onboarding notifies team'
FROM ai_employee_roles WHERE role_name = 'Onboarding Specialist';

-- Onboarding Denied Tools
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, tool_name, FALSE, 'Not an onboarding responsibility'
FROM ai_employee_roles, tools
WHERE ai_employee_roles.role_name = 'Onboarding Specialist'
AND tools.tool_name NOT IN ('collect_documents', 'schedule_training', 'setup_access', 'create_onboarding_plan', 'send_email', 'send_notification');


-- ============================================================================
-- TIER 4: UPDATE AI EMPLOYEES TABLE (Add role_id)
-- ============================================================================

ALTER TABLE ai_employees ADD COLUMN IF NOT EXISTS role_id UUID REFERENCES ai_employee_roles(id);
ALTER TABLE ai_employees ADD COLUMN IF NOT EXISTS nickname TEXT;

-- ============================================================================
-- TIER 5: USER-TO-AI-EMPLOYEE ASSIGNMENTS (Multi-user, multi-agent access)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_ai_employee_assignments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  ai_employee_id TEXT NOT NULL,
  assigned_at TIMESTAMP DEFAULT now(),
  UNIQUE(organization_id, user_id, ai_employee_id)
);

-- ============================================================================
-- TIER 6: AUDIT AND MONITORING
-- ============================================================================

CREATE TABLE IF NOT EXISTS tool_access_attempts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  ai_employee_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  allowed BOOLEAN NOT NULL,
  reason TEXT,
  attempted_at TIMESTAMP DEFAULT now()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_role_tool_permissions_role ON role_tool_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_tool_permissions_tool ON role_tool_permissions(tool_name);
CREATE INDEX IF NOT EXISTS idx_user_assignments_org ON user_ai_employee_assignments(organization_id);
CREATE INDEX IF NOT EXISTS idx_user_assignments_user ON user_ai_employee_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_tool_access_org ON tool_access_attempts(organization_id);
CREATE INDEX IF NOT EXISTS idx_tool_access_user ON tool_access_attempts(user_id);
