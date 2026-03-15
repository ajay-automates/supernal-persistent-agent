# 🚀 IMPLEMENT SUPERNAL'S ACTUAL AI EMPLOYEES WITH ROLE-BASED ACCESS CONTROL

**Objective: Build exact replicas of Supernal's real AI employees with role-based access and tool restrictions**

---

## 📊 SUPERNAL'S ACTUAL AI EMPLOYEES (Research Summary)

Based on the research provided, Supernal has built AI Employees across these categories:

### **CATEGORY 1: SALES/PROSPECTING**
- **AI SDR (Sales Development Representative)**
  - Research target accounts
  - Write personalized outreach (email/LinkedIn)
  - Book meetings
  - Track pipeline

### **CATEGORY 2: CUSTOMER SUPPORT**
- **Support Agent / AI Customer Service Rep**
  - Handle intake via email, chat, phone
  - Answer support tickets
  - Route requests to humans
  - Manage escalations

### **CATEGORY 3: BACK-OFFICE ADMINISTRATION**
- **AI Bookkeeper / Finance Coordinator**
  - Reconcile invoices
  - Update databases
  - Prepare financial reports
  - Track expenses

- **AI Operations Coordinator**
  - Schedule deliveries
  - Manage workflows
  - Coordinate resources

### **CATEGORY 4: MARKETING & CONTENT**
- **AI Social Media Manager (e.g., "Sophie")**
  - Learn brand voice
  - Write posts and campaigns
  - Create marketing content
  - Manage social media strategy

- **AI Content Creator**
  - Blog writing
  - Ad copy creation
  - Content calendar management

### **CATEGORY 5: OPERATIONS & LOGISTICS**
- **AI Dispatch Manager**
  - Dispatch field crews
  - Manage service schedules
  - Route optimization
  - Real-time coordination

- **AI Customer Scheduler**
  - Handle routine customer calls
  - Schedule appointments
  - Manage availability

### **CATEGORY 6: INDUSTRY-SPECIFIC**
- **Insurance: AI Claims Processor**
  - Quote generation
  - Claim intake
  - Document processing
  - Claim routing

- **Insurance: AI Underwriter Assistant**
  - Risk assessment
  - Policy recommendations
  - Coverage analysis

- **HR/Recruiting: AI Recruiter**
  - Candidate screening
  - Interview scheduling
  - Job posting optimization
  - Application processing

- **HR/Recruiting: AI Onboarding Specialist**
  - Onboarding workflow
  - Document collection
  - Training scheduling
  - New hire setup

---

## 🛠️ IMPLEMENTATION PLAN

### **STEP 1: Create AI Employee Roles Table**

```sql
CREATE TABLE ai_employee_roles (
  id UUID PRIMARY KEY,
  role_name TEXT UNIQUE,
  role_category TEXT,  -- Sales, Support, BackOffice, Marketing, Operations, Industry
  description TEXT,
  job_description TEXT,
  icon TEXT,  -- For UI display
  created_at TIMESTAMP
);

-- Insert Supernal's actual roles
INSERT INTO ai_employee_roles (role_name, role_category, description, job_description) VALUES

-- SALES
('Sales Development Rep (SDR)', 'Sales', 
 'AI-powered sales prospecting agent',
 'Research target accounts and decision makers. Write personalized cold emails and LinkedIn outreach. Qualify leads and schedule discovery calls. Track prospect engagement and follow up systematically.'),

-- SUPPORT
('Customer Support Agent', 'Support',
 'AI-powered customer service',
 'Handle customer inquiries across email, chat, and phone. Classify issues, search knowledge base, and provide solutions. Escalate complex issues to humans. Track customer satisfaction.'),

-- BACK-OFFICE
('Finance Coordinator', 'BackOffice',
 'AI-powered accounting and finance',
 'Reconcile invoices and bank statements. Categorize expenses. Prepare financial reports. Monitor cash flow. Flag discrepancies for human review.'),

('Operations Coordinator', 'BackOffice',
 'AI-powered operations management',
 'Schedule and coordinate deliveries. Manage warehouse operations. Track inventory. Coordinate with vendors. Optimize resource allocation.'),

-- MARKETING
('Social Media Manager', 'Marketing',
 'AI-powered social media marketing',
 'Learn and replicate brand voice. Create engaging social media posts. Plan marketing campaigns. Schedule content. Analyze engagement metrics.'),

('Content Creator', 'Marketing',
 'AI-powered content creation',
 'Write blog posts and articles. Create ad copy. Develop email campaigns. Manage content calendar. Optimize for SEO.'),

-- OPERATIONS & LOGISTICS
('Dispatch Manager', 'Operations',
 'AI-powered field service dispatch',
 'Dispatch field crews to jobs. Optimize routing. Manage service schedules. Track technician locations. Handle job assignments.'),

('Customer Scheduler', 'Operations',
 'AI-powered appointment scheduling',
 'Answer customer calls and inquiries. Schedule appointments. Manage availability. Send reminders. Handle cancellations and rescheduling.'),

-- INDUSTRY-SPECIFIC (Insurance)
('Insurance Claims Processor', 'Industry',
 'AI-powered insurance claims handling',
 'Receive and process claims. Generate quotes. Verify coverage. Detect fraud. Route claims to adjusters. Manage claim timeline.'),

('Insurance Underwriter Assistant', 'Industry',
 'AI-powered insurance underwriting',
 'Assess risk from applications. Generate underwriting recommendations. Analyze coverage needs. Create policy quotes. Flag edge cases.'),

-- INDUSTRY-SPECIFIC (HR/Recruiting)
('Recruiter', 'Industry',
 'AI-powered recruiting and talent acquisition',
 'Screen candidates automatically. Schedule interviews. Create job postings. Source candidates. Track applicants through pipeline.'),

('Onboarding Specialist', 'Industry',
 'AI-powered employee onboarding',
 'Collect onboarding documents. Schedule training. Set up systems access. Create onboarding timeline. Answer new hire questions.');
```

---

## 🔐 ROLE-BASED TOOL ACCESS MATRIX

### **Sales Development Rep (SDR)**
Tools allowed:
- ✅ send_email (cold outreach)
- ✅ search_web (prospect research)
- ✅ add_lead_to_crm (add prospects)
- ✅ query_crm (look up leads)
- ✅ schedule_meeting (book meetings)
- ✅ send_notification (notify team)

Tools denied:
- ❌ create_support_ticket
- ❌ process_leave_request
- ❌ order_equipment
- ❌ create_invoice
- ❌ dispatch_crew

### **Customer Support Agent**
Tools allowed:
- ✅ search_knowledge_base (help docs)
- ✅ create_support_ticket (escalate)
- ✅ check_account_status (customer info)
- ✅ send_email (customer communications)
- ✅ send_notification (notify team)

Tools denied:
- ❌ add_lead_to_crm (sales tool)
- ❌ process_leave_request (HR tool)
- ❌ order_equipment
- ❌ create_invoice
- ❌ post_social_media

### **Finance Coordinator**
Tools allowed:
- ✅ create_invoice (generate invoices)
- ✅ query_database (get financial data)
- ✅ update_database (record transactions)
- ✅ generate_report (financial reports)
- ✅ send_notification (notify team)

Tools denied:
- ❌ send_email (use accounting system)
- ❌ add_lead_to_crm
- ❌ dispatch_crew
- ❌ schedule_interview
- ❌ post_social_media

### **Operations Coordinator**
Tools allowed:
- ✅ query_database (warehouse data)
- ✅ update_database (update inventory)
- ✅ schedule_delivery (coordinate deliveries)
- ✅ notify_vendor (contact suppliers)
- ✅ send_notification (team updates)

Tools denied:
- ❌ send_email (use operations system)
- ❌ create_support_ticket
- ❌ post_social_media
- ❌ create_invoice
- ❌ dispatch_crew

### **Social Media Manager**
Tools allowed:
- ✅ post_social_media (create posts)
- ✅ schedule_post (schedule content)
- ✅ analyze_metrics (engagement tracking)
- ✅ generate_content (create copy)
- ✅ send_notification (notify team)

Tools denied:
- ❌ send_email (use SM platform)
- ❌ add_lead_to_crm
- ❌ process_leave_request
- ❌ create_invoice
- ❌ dispatch_crew

### **Content Creator**
Tools allowed:
- ✅ write_blog_post (blog content)
- ✅ create_ad_copy (ad creation)
- ✅ generate_email_campaign (email content)
- ✅ manage_content_calendar (schedule)
- ✅ send_notification (notify team)

Tools denied:
- ❌ send_email (use email platform)
- ❌ add_lead_to_crm
- ❌ create_support_ticket
- ❌ dispatch_crew
- ❌ process_leave_request

### **Dispatch Manager**
Tools allowed:
- ✅ dispatch_crew (send technicians)
- ✅ optimize_route (routing)
- ✅ query_database (schedules)
- ✅ update_database (job status)
- ✅ send_notification (crew alerts)

Tools denied:
- ❌ send_email (use dispatch system)
- ❌ create_support_ticket
- ❌ post_social_media
- ❌ process_leave_request
- ❌ create_invoice

### **Customer Scheduler**
Tools allowed:
- ✅ schedule_appointment (book appointments)
- ✅ send_notification (send reminders)
- ✅ query_database (availability)
- ✅ send_email (confirmation emails)
- ✅ handle_reschedule (manage changes)

Tools denied:
- ❌ add_lead_to_crm
- ❌ post_social_media
- ❌ create_invoice
- ❌ dispatch_crew
- ❌ process_leave_request

### **Insurance Claims Processor**
Tools allowed:
- ✅ create_claim_intake (receive claims)
- ✅ verify_coverage (check policies)
- ✅ detect_fraud (flag suspicious claims)
- ✅ generate_quote (create estimates)
- ✅ route_to_adjuster (escalate)
- ✅ send_notification (team alerts)

Tools denied:
- ❌ send_email (use insurance system)
- ❌ create_support_ticket
- ❌ post_social_media
- ❌ order_equipment
- ❌ process_leave_request

### **Insurance Underwriter Assistant**
Tools allowed:
- ✅ assess_risk (evaluate applications)
- ✅ generate_recommendation (underwriting decision)
- ✅ create_quote (policy quotes)
- ✅ analyze_coverage (coverage needs)
- ✅ flag_edge_cases (complex scenarios)
- ✅ send_notification (team alerts)

Tools denied:
- ❌ send_email (use insurance system)
- ❌ create_support_ticket
- ❌ post_social_media
- ❌ dispatch_crew
- ❌ process_leave_request

### **Recruiter**
Tools allowed:
- ✅ screen_candidates (auto-screening)
- ✅ schedule_interview (interview scheduling)
- ✅ create_job_posting (job ads)
- ✅ source_candidates (find prospects)
- ✅ track_pipeline (applicant tracking)
- ✅ send_email (candidate communications)
- ✅ send_notification (team alerts)

Tools denied:
- ❌ process_leave_request (HR tool)
- ❌ create_support_ticket
- ❌ post_social_media
- ❌ dispatch_crew
- ❌ create_invoice

### **Onboarding Specialist**
Tools allowed:
- ✅ collect_documents (onboarding docs)
- ✅ schedule_training (training schedule)
- ✅ setup_access (system access)
- ✅ create_onboarding_plan (timeline)
- ✅ send_email (new hire communications)
- ✅ send_notification (team alerts)

Tools denied:
- ❌ add_lead_to_crm
- ❌ create_support_ticket
- ❌ post_social_media
- ❌ dispatch_crew
- ❌ create_invoice

---

## 📝 CREATE ROLE-TOOL PERMISSION TABLE

```sql
CREATE TABLE role_tool_permissions (
  id UUID PRIMARY KEY,
  role_id UUID REFERENCES ai_employee_roles(id),
  tool_name TEXT,
  allowed BOOLEAN,
  reason TEXT,
  created_at TIMESTAMP
);

-- Insert all permissions (see matrix above)
-- Example:
INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason) 
SELECT id, 'send_email', TRUE, 'SDRs need to send cold emails' 
FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)';

INSERT INTO role_tool_permissions (role_id, tool_name, allowed, reason)
SELECT id, 'process_leave_request', FALSE, 'Not HR responsibility'
FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)';

-- ... (continue for all role-tool combinations)
```

---

## 🏢 CREATE AI EMPLOYEES FOR MULTIPLE CUSTOMER TYPES

Now create realistic AI employee setups for different company types:

### **FOR AMAZON (Sales/Enterprise B2B SaaS)**

Create these AI employees:
1. **Sales Development Rep** - Prospect research and outreach
2. **Customer Support Agent** - Technical and account support
3. **Content Creator** - Marketing materials and case studies
4. **Operations Coordinator** - Account management and renewals

### **FOR STRIPE (FinTech/SaaS)**

Create these AI employees:
1. **Customer Support Agent** - 24/7 support
2. **Insurance Claims Processor** - Fraud and chargebacks
3. **Finance Coordinator** - Payment reconciliation
4. **Developer Onboarding Specialist** - Integrate with API

### **FOR TECHVENTUS (Service Company - HVAC/Plumbing)**

Create these AI employees:
1. **Dispatch Manager** - Schedule and dispatch technicians
2. **Customer Scheduler** - Book appointments
3. **Operations Coordinator** - Inventory and scheduling
4. **Customer Support Agent** - Handle service calls

### **FOR INSURANCE COMPANY (Example)**

Create these AI employees:
1. **Insurance Claims Processor** - Process claims
2. **Insurance Underwriter Assistant** - Underwrite policies
3. **Customer Support Agent** - Handle inquiries
4. **Finance Coordinator** - Premium management

### **FOR MARKETING AGENCY (Example)**

Create these AI employees:
1. **Social Media Manager** - Content creation and posting
2. **Content Creator** - Blog and ad copy
3. **Sales Development Rep** - Prospect outreach
4. **Operations Coordinator** - Project management

### **FOR RECRUITING FIRM (Example)**

Create these AI employees:
1. **Recruiter** - Candidate screening and scheduling
2. **Onboarding Specialist** - Placement onboarding
3. **Sales Development Rep** - Business development
4. **Content Creator** - Job descriptions and marketing

---

## 🔄 UPDATE ai_employees TABLE WITH ROLES

Modify the ai_employees table to link to roles:

```sql
ALTER TABLE ai_employees ADD COLUMN role_id UUID REFERENCES ai_employee_roles(id);

-- When creating an AI employee, assign a role:
INSERT INTO ai_employees (organization_id, ai_employee_id, name, role_id, job_description)
SELECT 
  'amazon_org_id',
  'sales_rep_1',
  'Sales SDR - Alex',
  (SELECT id FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)'),
  (SELECT job_description FROM ai_employee_roles WHERE role_name = 'Sales Development Rep (SDR)')
;
```

---

## 🔐 IMPLEMENT ROLE-BASED TOOL ACCESS IN agent.py

```python
def get_ai_employee_allowed_tools(ai_employee_id, organization_id):
    """Get all tools this AI employee's role allows"""
    
    # Get the AI employee
    ai_employee = get_ai_employee(ai_employee_id, organization_id)
    
    # Get their role
    role_id = ai_employee['role_id']
    
    # Get all tools allowed for this role
    allowed_tools = get_role_tools(role_id, allowed=True)
    
    return [tool['tool_name'] for tool in allowed_tools]

def can_ai_employee_use_tool(ai_employee_id, tool_name, organization_id):
    """Check if this AI employee's role allows this tool"""
    
    ai_employee = get_ai_employee(ai_employee_id, organization_id)
    role_id = ai_employee['role_id']
    
    # Check if this role is allowed to use this tool
    permission = get_role_tool_permission(role_id, tool_name)
    
    if not permission or not permission['allowed']:
        allowed_tools = get_ai_employee_allowed_tools(ai_employee_id, organization_id)
        return False, f"This role cannot use {tool_name}. Allowed tools: {allowed_tools}"
    
    return True, None

def execute_tool_with_role_check(user_id, ai_employee_id, tool_name, params, organization_id):
    """Execute tool only if role allows it"""
    
    # Check if AI employee's role allows this tool
    can_use, error = can_ai_employee_use_tool(ai_employee_id, tool_name, organization_id)
    
    if not can_use:
        return {
            "status": "denied",
            "error": error,
            "reason": "role_restriction"
        }
    
    # Tool is allowed, execute it
    result = route_tool_call(ai_employee_id, tool_name, params)
    
    return result
```

---

## 🎯 UPDATE DEMO SETUP

When creating demo data, include actual Supernal roles:

```python
def setup_supernal_demo_companies():
    """Create companies with their actual Supernal AI employees"""
    
    # AMAZON (SaaS Sales Company)
    create_ai_employee_with_role(
        org_id='amazon',
        name='Sales SDR - Alex',
        role='Sales Development Rep (SDR)',
        nickname='Alex'
    )
    create_ai_employee_with_role(
        org_id='amazon',
        name='Customer Support - Maya',
        role='Customer Support Agent',
        nickname='Maya'
    )
    
    # STRIPE (FinTech)
    create_ai_employee_with_role(
        org_id='stripe',
        name='Support Agent - Jordan',
        role='Customer Support Agent',
        nickname='Jordan'
    )
    create_ai_employee_with_role(
        org_id='stripe',
        name='Claims Processor - Sam',
        role='Insurance Claims Processor',
        nickname='Sam'
    )
    
    # TECHVENTUS (Service Company)
    create_ai_employee_with_role(
        org_id='techventus',
        name='Dispatch Manager - Quinn',
        role='Dispatch Manager',
        nickname='Quinn'
    )
    create_ai_employee_with_role(
        org_id='techventus',
        name='Customer Scheduler - Riley',
        role='Customer Scheduler',
        nickname='Riley'
    )
    
    # ... create more companies with their specific AI employees
```

---

## 📊 UPDATE UI TO SHOW ROLES

In index.html, when displaying AI employees, show their role:

```html
<div id="ai-employee-selector">
  <label>AI Employee:</label>
  <div id="ai-employees-list">
    <!-- Dynamically populated -->
  </div>
</div>

<script>
function loadAIEmployees(organizationId) {
    fetch(`/api/ai-employees/${organizationId}`)
        .then(r => r.json())
        .then(data => {
            document.getElementById('ai-employees-list').innerHTML = data.employees
                .map(emp => `
                    <div class="ai-employee-card">
                        <strong>${emp.name}</strong>
                        <small>Role: ${emp.role_name}</small>
                        <p>${emp.role_description}</p>
                    </div>
                `).join('');
        });
}
</script>
```

---

## 🎯 DEMO IMPACT ON MONDAY

When Dexter sees this, he'll think:

*"Wait... he researched OUR AI employees. He's not just showing a generic system. He built a prototype WITH OUR ACTUAL PRODUCTS IN IT. He understands what we're building at a deep level."*

This is the difference between:
- "Good technical interview" → Nice prototype
- "Wow" → He understands our business

---

## 📋 IMPLEMENTATION CHECKLIST

```
☐ Create ai_employee_roles table with Supernal's 12+ actual roles
☐ Create role_tool_permissions table
☐ Insert all role-tool mappings
☐ Update ai_employees table to include role_id
☐ Implement can_ai_employee_use_tool() check
☐ Update execute_tool_with_role_check()
☐ Create demo data for 6+ company types
☐ Update API to return role information
☐ Update UI to display role with AI employee name
☐ Test role-based restrictions work
☐ Verify error messages are helpful
☐ Add role descriptions to chat (so user knows what agent can do)
```

This implementation shows:
✅ You researched Supernal's actual products
✅ You understand their business model
✅ You built enterprise-grade role-based access
✅ You think about production needs (security, clarity, compliance)
✅ You're ready to be a founding engineer

---

This is how you win the interview.
