-- Mock verification tables for tool side effects shown in the Verification UI.
CREATE TABLE IF NOT EXISTS mock_emails_sent (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email_id TEXT UNIQUE,
  recipient TEXT,
  subject TEXT,
  body TEXT,
  status TEXT,
  sent_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mock_crm_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  lead_id TEXT UNIQUE,
  company TEXT,
  contact_name TEXT,
  email TEXT,
  phone TEXT,
  stage TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mock_support_tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ticket_id TEXT UNIQUE,
  customer_email TEXT,
  issue_type TEXT,
  description TEXT,
  priority TEXT,
  status TEXT,
  assigned_to TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mock_calendar_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  event_id TEXT UNIQUE,
  attendee_email TEXT,
  title TEXT,
  date_time TIMESTAMP,
  duration_minutes INTEGER,
  zoom_link TEXT,
  status TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mock_equipment_orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  order_id TEXT UNIQUE,
  equipment TEXT,
  quantity INTEGER,
  unit_price DECIMAL,
  total_cost DECIMAL,
  employee_name TEXT,
  status TEXT,
  estimated_delivery DATE,
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mock_emails_org ON mock_emails_sent(organization_id);
CREATE INDEX IF NOT EXISTS idx_mock_crm_org ON mock_crm_leads(organization_id);
CREATE INDEX IF NOT EXISTS idx_mock_tickets_org ON mock_support_tickets(organization_id);
CREATE INDEX IF NOT EXISTS idx_mock_calendar_org ON mock_calendar_events(organization_id);
CREATE INDEX IF NOT EXISTS idx_mock_equipment_org ON mock_equipment_orders(organization_id);
