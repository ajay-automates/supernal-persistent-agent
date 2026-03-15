-- Add missing RBAC roles for demo setup

INSERT INTO ai_employee_roles (role_name, role_category, description, job_description, icon, example_task)
VALUES
  ('Content Creator', 'content', 'Content creator for marketing', 'Create marketing content', '📝', 'Write blog posts'),
  ('Operations Coordinator', 'ops', 'Operations coordinator', 'Coordinate operations', '📋', 'Manage schedules'),
  ('Insurance Claims Processor', 'insurance', 'Claims processor', 'Process insurance claims', '📄', 'Review claims'),
  ('Finance Coordinator', 'finance', 'Finance coordinator', 'Manage finances', '💰', 'Reconcile accounts'),
  ('Social Media Manager', 'marketing', 'Social media manager', 'Manage social media', '📱', 'Post on social'),
  ('Dispatch Manager', 'ops', 'Dispatch manager', 'Manage dispatching', '🚚', 'Schedule deliveries'),
  ('Customer Scheduler', 'support', 'Customer scheduler', 'Schedule appointments', '📅', 'Book appointments'),
  ('Insurance Underwriter Assistant', 'insurance', 'Underwriting assistant', 'Assist with underwriting', '🔍', 'Assess risk'),
  ('Onboarding Specialist', 'hr', 'Onboarding specialist', 'Handle employee onboarding', '👋', 'Process onboarding')
ON CONFLICT (role_name) DO NOTHING;
