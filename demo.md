You are building a comprehensive demo setup for a multi-tenant AI employee platform.

Create realistic sample data and mock tool implementations so the demo shows how the system works end-to-end, even without real API connections.

═══════════════════════════════════════════════════════════════════════════════

PART 1: CREATE SAMPLE DATA FOR THREE COMPANIES

We need three complete, realistic companies with different use cases:

═══════════════════════════════════════════════════════════════════════════════

COMPANY 1: AMAZON (Sales/SDR Use Case)

Organization Details:
- Name: Amazon
- Industry: E-commerce
- Use Case: Sales Development Representatives (SDRs)
- AI Employees: Sales Bot (SDR), Account Manager Bot

Company Documents/Data:

1. Sales Process SOP:
```
AMAZON SALES PROCESS

Sales Development Representative (SDR) Responsibilities:
1. Identify and research target accounts
2. Find decision makers via LinkedIn research
3. Write personalized outreach emails
4. Add prospects to Salesforce CRM
5. Schedule initial discovery calls
6. Track follow-ups

Key Metrics:
- Target: 30 cold emails/day
- Expected response rate: 5-8%
- Expected meeting booking rate: 1-2%
- Average deal size: $50K-$200K

Email Templates:
Subject: "Quick idea for [Company]'s Q3 sales"
Body:
Hi [First Name],

Quick insight: [Company] is in [Industry]. We've helped similar companies increase [metric] by [%].

Three questions:
1. Are you currently looking to improve [pain point]?
2. If yes, what's your timeline?
3. Who else should be in the conversation?

Best,
[Name]

CRM Integration:
- Salesforce instance: amazon.salesforce.com
- Required fields: Company, Contact Name, Email, Phone, Industry, Company Size
- Opportunity stage: New Lead → Contacted → Qualified → Proposal → Closed Won

Meeting Scheduling:
- Calendar: Calendar.amazon.com
- Book 30-min discovery calls
- Preferred times: Tuesday-Thursday, 10am-4pm PT
- Include Zoom link in calendar invite
```

2. Company Information:
```
AMAZON COMPANY PROFILE

Company Name: Amazon
Founded: 1994
Headquarters: Seattle, WA
Industry: E-commerce, Cloud Services
Revenue: $575B+
Target Markets: B2B SaaS, Retail, Technology
Key Products: AWS, Amazon.com, Advertising Platform

Decision Makers we're targeting:
- VP of Sales
- Sales Operations Manager
- Director of Revenue
- Chief Revenue Officer

Company Size Segments we target:
- Mid-Market (100-500 employees)
- Enterprise (500+ employees)

Pricing Strategy:
- Starter: $20K/month
- Professional: $50K/month
- Enterprise: Custom

Key Differentiators:
- 40% faster deal closure
- 3x lead qualification rate
- AI-powered prospecting
```

3. Product Details:
```
AMAZON AI SALES PLATFORM

Features:
1. Automated prospecting - AI identifies target accounts and decision makers
2. Personalized email generation - AI writes contextual emails based on research
3. CRM sync - Automatically add leads and track interactions
4. Meeting scheduling - Book discovery calls directly
5. Follow-up sequences - Automated multi-touch follow-up campaigns

Use Case: Sales Development Rep (SDR)
- Role: Identify and qualify B2B prospects
- Tools Used: LinkedIn research, email, CRM, calendar
- Success Metrics: Meetings booked, qualification rate, email response rate

Recent Wins:
- Tech startup: 40 qualified meetings in 1 month ($2.5M pipeline)
- Insurance company: 60% faster lead response ($3.8M pipeline)
- B2B SaaS: 25 new customers from AI SDR ($1.5M ARR)
```

═══════════════════════════════════════════════════════════════════════════════

COMPANY 2: STRIPE (Customer Support Use Case)

Organization Details:
- Name: Stripe
- Industry: Financial Services / Payment Processing
- Use Case: Customer Support Automation
- AI Employees: Support Bot (Level 1 Support), Technical Support Bot

Company Documents/Data:

1. Support Process:
```
STRIPE CUSTOMER SUPPORT PROCESS

Level 1 Support Bot Responsibilities:
1. Receive customer inquiries via email, chat, support ticket
2. Classify issue type (billing, technical, account, fraud)
3. Search knowledge base for resolution
4. Generate response or escalate to human
5. Track ticket status
6. Send follow-up

Common Issue Types:
1. Billing Issues
   - Invoice questions
   - Refund requests
   - Subscription changes
   - Price increase notifications

2. Technical Issues
   - API integration problems
   - Webhook failures
   - Authentication errors
   - Rate limiting questions

3. Account Issues
   - Access problems
   - User permission changes
   - MFA setup
   - Account recovery

4. Fraud/Compliance
   - Suspicious activity reports
   - Compliance questions
   - Dispute handling
   - Risk assessment

Response Time Goals:
- Critical: 30 minutes (human only)
- High: 2 hours (bot + human)
- Medium: 8 hours (bot only, escalate if needed)
- Low: 24 hours (bot only)

Knowledge Base Topics:
- API documentation
- Common integration patterns
- Troubleshooting guides
- Billing FAQ
- Compliance information
- Payment method support
```

2. Company Information:
```
STRIPE COMPANY PROFILE

Company Name: Stripe
Founded: 2010
Headquarters: San Francisco, CA
Industry: Financial Technology
Revenue: $14B+ (valuation)
Customers: 1M+ businesses globally
Support Languages: English, Spanish, French, German, Japanese

Customer Segments:
- Startups (0-10 employees)
- SMBs (10-100 employees)
- Mid-Market (100-1000 employees)
- Enterprise (1000+ employees)

Key Products:
- Payments (online, in-person, mobile)
- Billing (subscriptions, recurring)
- Connect (marketplace payouts)
- Radar (fraud detection)
- Climate (carbon removal)

SLAs:
- First response: 2 hours
- Resolution: 24 hours
- Critical escalation: 30 minutes
```

3. Support Scripts:
```
STRIPE SUPPORT SCRIPTS

Script 1: Billing Inquiry
User: "Why was I charged twice?"
Bot: "I understand you see a duplicate charge. Let me help.

Can you provide:
1. The date of the charge
2. The transaction amount
3. Your Stripe Account ID

This usually happens due to:
- Retry logic (automatic retry after failed payment)
- Double submission (accidental form resubmit)
- Test vs. live mode

I'll investigate and respond within 2 hours."

Script 2: API Integration Error
User: "Getting 'Invalid API Key' error"
Bot: "This error typically means:
1. API key is expired
2. Using wrong API key version (publishable vs. secret)
3. API key permissions don't allow this action

Quick fixes:
1. Verify you're using Secret Key, not Publishable Key
2. Check if key is active in Dashboard
3. Test with fresh API key

Need help? I can escalate to technical support."

Script 3: Fraud Alert
User: "My account is locked"
Bot: "Security alert detected on your account. This is normal if:
1. Unusual activity detected
2. Multiple failed payment attempts
3. Geographic anomaly (login from new location)

Next steps:
1. Verify your identity
2. Review recent transactions
3. We may need to verify your business

For security concerns, connecting you with Fraud team now."
```

═══════════════════════════════════════════════════════════════════════════════

COMPANY 3: TECHVENTUS (Operations/HR Use Case)

Organization Details:
- Name: TechVentus
- Industry: SaaS / Software Development
- Use Case: Operations & HR Automation
- AI Employees: HR Bot (recruiting, onboarding), Ops Bot (scheduling, admin)

Company Documents/Data:

1. HR & Operations Process:
```
TECHVENTUS HR & OPERATIONS

TechVentus Company:
- Size: 85 employees
- Founded: 2019
- Focus: B2B SaaS platform for data analytics
- Revenue: $12M ARR
- Growth rate: 40% YoY

HR Bot Responsibilities:
1. Candidate screening and scheduling
2. Employee onboarding
3. Leave request processing
4. Benefits administration
5. Performance review scheduling

Common HR Tasks:

1. Candidate Screening
   - Receive applications from LinkedIn, email
   - Screen for required skills
   - Schedule interviews
   - Send offer letters
   - Manage offer acceptance

2. Onboarding
   - Create employee profile
   - Setup email & accounts
   - Assign equipment requests
   - Schedule training sessions
   - Generate onboarding checklist

3. Leave Management
   - Receive leave requests
   - Check leave balance
   - Approve/deny based on policy
   - Update calendar
   - Send confirmation

4. Benefits
   - Health insurance questions
   - 401k enrollment
   - Stock option questions
   - Vacation policy
   - Remote work policy

Operations Bot Responsibilities:
1. Meeting room scheduling
2. Equipment procurement
3. Travel booking
4. Office maintenance
5. Vendor management

Common Ops Tasks:

1. Meeting Scheduling
   - Find available times
   - Check room availability
   - Send calendar invites
   - Setup Zoom links
   - Send reminders

2. Equipment Requests
   - Receive equipment requests
   - Check inventory
   - Order from vendors
   - Track delivery
   - Setup new equipment

3. Travel Management
   - Book flights
   - Reserve hotels
   - Arrange ground transport
   - Process expenses
   - Track travel budget

Policies:

Vacation Policy:
- 20 days PTO per year
- 10 paid holidays
- Unlimited sick days
- 10 days parental leave

Remote Work Policy:
- Full remote allowed
- Flexible schedule
- Home office stipend: $500/year
- Quarterly in-person meetings (optional)

Equipment Budget:
- Laptop: $2000
- Monitor: $400
- Peripherals: $300
- Total per employee: $2700
```

2. Employee Directory:
```
TECHVENTUS TEAM

Engineering (30 people)
- VP of Engineering: Sarah Chen
- Engineering Managers: 3
- Senior Engineers: 8
- Engineers: 19

Sales & Revenue (20 people)
- VP of Sales: James Rodriguez
- Sales Managers: 2
- Account Executives: 6
- SDRs: 10
- Sales Ops: 2

Product & Design (15 people)
- VP of Product: Lisa Wang
- Product Managers: 2
- Designers: 4
- Researchers: 3
- Analysts: 6

Operations & Support (20 people)
- VP of Operations: Michael Torres
- HR/People Ops: 5
- Finance/Accounting: 4
- Customer Success: 8
- IT/Admin: 3
```

3. Integration Details:
```
TECHVENTUS SYSTEMS

HR Systems:
- HRIS: BambooHR
- Job Board: Lever
- Learning: Coursera
- Payroll: Guidepoint

Operations:
- Calendar: Google Calendar
- Meetings: Zoom
- Travel: Expedia Corporate
- Procurement: Coupa
- Chat: Slack

Database:
- Employee records: BambooHR
- Leave balances: BambooHR
- Equipment inventory: Airtable
- Budget tracking: Spreadsheet
- Vendor contacts: Salesforce
```

═══════════════════════════════════════════════════════════════════════════════

PART 2: DEFINE MOCK TOOL IMPLEMENTATIONS

Since we don't have real API connections, create mock tools that simulate real behavior but with fake data.

Create tools.py with:

1. Amazon Sales Tools:
   - send_email_tool(params) → Returns email_id, recipient, timestamp
   - add_lead_to_crm_tool(params) → Returns lead_id, crm_url
   - schedule_meeting_tool(params) → Returns zoom_link, calendar_event_id
   - query_crm_tool(params) → Returns list of leads/opportunities
   - search_web_tool(params) → Returns mock search results

2. Stripe Support Tools:
   - search_knowledge_base_tool(params) → Returns article, url, relevance
   - create_support_ticket_tool(params) → Returns ticket_id, priority
   - check_account_status_tool(params) → Returns account status, balance, volume
   - send_notification_tool(params) → Returns confirmation

3. TechVentus HR/Ops Tools:
   - schedule_interview_tool(params) → Returns interview_id, zoom_link
   - process_leave_request_tool(params) → Returns leave_id, approval_status
   - schedule_meeting_room_tool(params) → Returns room_id, amenities
   - order_equipment_tool(params) → Returns order_id, estimated_delivery
   - send_notification_tool(params) → Returns confirmation

4. Generic Tools:
   - search_web_tool(params)
   - update_database_tool(params)
   - send_notification_tool(params)

Each tool should:
- Accept params dict
- Simulate 0.5-2 second latency
- Return realistic response with IDs, timestamps, confirmation
- Log execution for observability
- Have error handling

═══════════════════════════════════════════════════════════════════════════════

PART 3: CREATE DEMO SETUP SCRIPT

Create demo_setup.py that:

1. Creates 3 organizations (Amazon, Stripe, TechVentus)
2. Creates AI employees for each org
3. Creates 3 users per organization
4. Uploads company documents
5. Populates vector database with sample chunks
6. Pre-seeds sample conversations

The setup function should run on app startup and be idempotent (safe to run multiple times).

═══════════════════════════════════════════════════════════════════════════════

PART 4: UPDATE UI FOR COMPANY SWITCHER

Update index.html to show:

1. Organization dropdown (Amazon, Stripe, TechVentus)
2. When org changes:
   - Load org-specific AI employees
   - Load org-specific users
   - Show company info card (use case, AI employees, tools)
   - Update example questions

3. Add company info panel showing:
   - Company name
   - Use case description
   - AI employee roles
   - Key tools available
   - Success metrics

═══════════════════════════════════════════════════════════════════════════════

EXPECTED DEMO FLOW:

1. Load system → Dropdown shows 3 companies
2. Select Amazon → Shows Sales Bot
3. Demo tool execution:
   "Research and reach out to john@techcorp.com about our Q2 offering"
   Agent uses tools:
   - search_web("TechCorp company info")
   - send_email(to=john@techcorp.com, ...)
   - add_lead_to_crm(company="TechCorp", ...)
   - schedule_meeting(attendee="john@techcorp.com", ...)

4. Switch to Stripe → Shows Support Bot
5. Demo support:
   "Customer says their payment failed. What should we do?"
   Agent uses tools:
   - search_knowledge_base("payment failed error")
   - check_account_status(account=customer_id)
   - create_support_ticket(issue_type="technical", ...)

6. Switch to TechVentus → Shows HR Bot
7. Demo HR:
   "Process leave request for Sarah for next week"
   Agent uses tools:
   - process_leave_request(employee="Sarah", dates=...)
   - send_notification(channel="hr-team", message=...)
   - schedule_meeting_room(for_training=...)

═══════════════════════════════════════════════════════════════════════════════

This creates a production-like demo experience without needing real API integrations.