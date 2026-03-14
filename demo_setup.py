"""
demo_setup.py — Idempotent demo data seeder.

Creates 3 organizations (Amazon, Stripe, TechVentus) each with:
  • 2 AI employees
  • 3 sample users
  • Company documents uploaded to the knowledge base
  • Tools registered

Safe to call multiple times — skips any entity that already exists by name.

Usage:
    python demo_setup.py          # run standalone
    import demo_setup; demo_setup.run()  # call from main.py startup
"""

import os
import time
import logging

from config import OPENAI_API_KEY
from db import (
    create_organization, list_organizations,
    create_ai_employee, get_ai_employees,
    create_user, get_org_users,
    save_organization_document, save_organization_chunk,
    get_organization_documents,
    register_tool, get_organization_tools,
)
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("demo_setup")

client = OpenAI(api_key=OPENAI_API_KEY)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def _chunk(text: str):
    chunks = []
    for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
        c = text[i:i + CHUNK_SIZE]
        if c.strip():
            chunks.append(c.strip())
    return chunks


def _embed_and_store(org_id: str, text: str, filename: str):
    """Embed text chunks and save to org knowledge base."""
    chunks = _chunk(text)
    for chunk in chunks:
        emb = client.embeddings.create(model="text-embedding-3-small", input=chunk)
        save_organization_chunk(org_id, chunk, emb.data[0].embedding, filename)
    return len(chunks)


def _get_or_create_org(name: str) -> dict:
    orgs = list_organizations()
    for o in orgs:
        if o["name"].lower() == name.lower():
            log.info("  Org exists: %s (%s)", name, o["id"])
            return o
    org = create_organization(name)
    log.info("  Created org: %s (%s)", name, org["id"])
    return org


def _get_or_create_agent(org_id: str, name: str, role: str, job_description: str) -> dict:
    agents = get_ai_employees(org_id)
    for a in agents:
        if a["name"].lower() == name.lower():
            log.info("    Agent exists: %s", name)
            return a
    agent = create_ai_employee(org_id, name, role, job_description)
    log.info("    Created agent: %s (%s)", name, agent["id"])
    return agent


def _get_or_create_user(org_id: str, user_id: str, name: str, email: str) -> dict:
    users = get_org_users(org_id)
    for u in users:
        if u["user_id"] == user_id:
            log.info("    User exists: %s", user_id)
            return u
    user = create_user(org_id, user_id, name, email)
    log.info("    Created user: %s", user_id)
    return user


def _upload_doc_if_missing(org_id: str, filename: str, text: str):
    docs = get_organization_documents(org_id)
    if any(d["filename"] == filename for d in docs):
        log.info("    Doc exists: %s", filename)
        return
    save_organization_document(org_id, filename, filename)
    n = _embed_and_store(org_id, text, filename)
    log.info("    Uploaded doc: %s (%d chunks)", filename, n)


def _register_tool_if_missing(org_id: str, name: str, description: str, schema: dict):
    existing = get_organization_tools(org_id)
    if any(t["name"] == name for t in existing):
        return
    register_tool(org_id, name, description, schema, "")
    log.info("    Registered tool: %s", name)


# ══════════════════════════════════════════════════════════════
# COMPANY DATA
# ══════════════════════════════════════════════════════════════

# ── Amazon ────────────────────────────────────────────────────

AMAZON_SALES_SOP = """
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
""".strip()

AMAZON_COMPANY_INFO = """
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

Recent Wins:
- Tech startup: 40 qualified meetings in 1 month ($2.5M pipeline)
- Insurance company: 60% faster lead response ($3.8M pipeline)
- B2B SaaS: 25 new customers from AI SDR ($1.5M ARR)
""".strip()

# ── Stripe ────────────────────────────────────────────────────

STRIPE_SUPPORT_PROCESS = """
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
""".strip()

STRIPE_SUPPORT_SCRIPTS = """
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

Stripe Company Profile:
- Founded: 2010
- Headquarters: San Francisco, CA
- Industry: Financial Technology
- Customers: 1M+ businesses globally
- Support Languages: English, Spanish, French, German, Japanese
- SLAs: First response 2h, Resolution 24h, Critical 30min

Key Products:
- Payments (online, in-person, mobile)
- Billing (subscriptions, recurring)
- Connect (marketplace payouts)
- Radar (fraud detection)
""".strip()

# ── TechVentus ────────────────────────────────────────────────

TECHVENTUS_HR_PROCESS = """
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
   - Check leave balance (20 days PTO/year)
   - Approve/deny based on policy
   - Update calendar
   - Send confirmation

4. Benefits
   - Health insurance: Blue Shield PPO (employer pays 90%)
   - 401k: 4% match, vests immediately
   - Stock options: 4-year vest, 1-year cliff
   - Vacation: 20 days PTO + 10 holidays
   - Remote: Full remote, $500/year home office stipend

Policies:
- Vacation Policy: 20 days PTO per year + 10 paid holidays
- Unlimited sick days
- 10 days parental leave
- Remote Work: Full remote allowed, flexible schedule
- Equipment Budget: $2,700 per employee (Laptop $2000, Monitor $400, Peripherals $300)
""".strip()

TECHVENTUS_TEAM = """
TECHVENTUS TEAM DIRECTORY

Engineering (30 people)
- VP of Engineering: Sarah Chen (sarah.chen@techventus.com)
- Engineering Managers: Alex Kim, Raj Patel, Maria Lopez
- Senior Engineers: 8 (avg tenure 2.5 years)
- Engineers: 19

Sales & Revenue (20 people)
- VP of Sales: James Rodriguez (james.r@techventus.com)
- Sales Managers: 2
- Account Executives: 6
- SDRs: 10
- Sales Ops: 2

Product & Design (15 people)
- VP of Product: Lisa Wang (lisa.wang@techventus.com)
- Product Managers: 2
- Designers: 4
- Researchers: 3
- Analysts: 6

Operations & Support (20 people)
- VP of Operations: Michael Torres (michael.t@techventus.com)
- HR/People Ops: 5 (HR Bot reports to this team)
- Finance/Accounting: 4
- Customer Success: 8
- IT/Admin: 3

Systems:
- HRIS: BambooHR (bamboohr.com/techventus)
- Job Board: Lever (hire.lever.co/techventus)
- Learning: Coursera for Business
- Payroll: Guidepoint
- Calendar: Google Calendar
- Meetings: Zoom
- Travel: Expedia Corporate
- Procurement: Coupa
- Chat: Slack (#hr-requests, #ops-requests)
""".strip()


# ══════════════════════════════════════════════════════════════
# MAIN SETUP FUNCTION
# ══════════════════════════════════════════════════════════════

def run():
    log.info("=" * 60)
    log.info("DEMO SETUP — starting")
    log.info("=" * 60)

    # ── 1. AMAZON ──────────────────────────────────────────────
    log.info("\n[1/3] Amazon (Sales / SDR)")
    amazon = _get_or_create_org("Amazon")
    org_id = amazon["id"]

    _get_or_create_agent(
        org_id,
        name="Alex (Sales Bot)",
        role="Sales Development Representative",
        job_description=(
            "You are Alex, an SDR at Amazon. Your job is to research target accounts, "
            "find decision makers, write personalized outreach emails, add leads to Salesforce CRM, "
            "and schedule discovery calls. Always be professional, concise, and data-driven. "
            "Use search_web to research companies before reaching out. "
            "Use add_lead_to_crm to track every prospect you contact. "
            "Use send_email to send personalized outreach. "
            "Use schedule_meeting to book discovery calls. "
            "Target: VPs of Sales, Directors of Revenue, CROs at mid-market and enterprise companies."
        ),
    )
    _get_or_create_agent(
        org_id,
        name="Morgan (Account Manager)",
        role="Account Manager",
        job_description=(
            "You are Morgan, an Account Manager at Amazon. You manage existing client relationships, "
            "handle renewals, upsells, and ensure customer success. "
            "Use query_crm to look up account details. "
            "Use send_email to communicate with clients. "
            "Use schedule_meeting to book QBRs and check-in calls."
        ),
    )

    _get_or_create_user(org_id, "sarah_sdr",    "Sarah Miller",  "sarah@amazon-sales.com")
    _get_or_create_user(org_id, "tom_manager",  "Tom Chen",      "tom@amazon-sales.com")
    _get_or_create_user(org_id, "demo_user",    "Demo User",     "demo@amazon.com")

    _upload_doc_if_missing(org_id, "amazon_sales_sop.txt",     AMAZON_SALES_SOP)
    _upload_doc_if_missing(org_id, "amazon_company_info.txt",  AMAZON_COMPANY_INFO)

    for t in [
        ("send_email",      "Send a personalized sales email to a prospect",
         {"parameters": {"to": "string", "subject": "string", "body": "string"}}),
        ("add_lead_to_crm", "Add a new prospect lead to Salesforce CRM",
         {"parameters": {"company": "string", "contact_name": "string", "email": "string", "opportunity_stage": "string"}}),
        ("schedule_meeting","Book a discovery call with a prospect",
         {"parameters": {"attendee_email": "string", "date": "string", "time": "string", "duration_min": "integer"}}),
        ("query_crm",       "Search CRM for existing leads and opportunities",
         {"parameters": {"query": "string", "stage": "string"}}),
        ("search_web",      "Research a company or person on the web",
         {"parameters": {"query": "string", "num_results": "integer"}}),
    ]:
        _register_tool_if_missing(org_id, *t)

    # ── 2. STRIPE ──────────────────────────────────────────────
    log.info("\n[2/3] Stripe (Customer Support)")
    stripe = _get_or_create_org("Stripe")
    org_id = stripe["id"]

    _get_or_create_agent(
        org_id,
        name="Sam (Support Bot)",
        role="Level 1 Customer Support",
        job_description=(
            "You are Sam, a Level 1 Support agent at Stripe. "
            "You handle billing questions, API integration issues, account problems, and fraud alerts. "
            "Always classify the issue first, then search the knowledge base, then respond or escalate. "
            "Use search_knowledge_base to find relevant articles. "
            "Use check_account_status to look up customer accounts. "
            "Use create_support_ticket to log and track issues. "
            "Use send_notification to confirm actions with customers. "
            "Escalate critical/security issues immediately to the human team."
        ),
    )
    _get_or_create_agent(
        org_id,
        name="Jordan (Technical Support)",
        role="Technical Support Engineer",
        job_description=(
            "You are Jordan, a Technical Support Engineer at Stripe specializing in API integrations. "
            "You handle complex API errors, webhook issues, and integration debugging. "
            "Use search_knowledge_base with category='technical' for technical articles. "
            "Use check_account_status to verify account configuration. "
            "Use create_support_ticket with priority='high' for complex technical issues."
        ),
    )

    _get_or_create_user(org_id, "alice_support",  "Alice Johnson",  "alice@stripe-support.com")
    _get_or_create_user(org_id, "bob_tech",       "Bob Williams",   "bob@stripe-support.com")
    _get_or_create_user(org_id, "demo_user",      "Demo User",      "demo@stripe.com")

    _upload_doc_if_missing(org_id, "stripe_support_process.txt", STRIPE_SUPPORT_PROCESS)
    _upload_doc_if_missing(org_id, "stripe_support_scripts.txt", STRIPE_SUPPORT_SCRIPTS)

    for t in [
        ("search_knowledge_base",  "Search Stripe's internal knowledge base for issue resolution",
         {"parameters": {"query": "string", "category": "string"}}),
        ("check_account_status",   "Check a customer's Stripe account status and health",
         {"parameters": {"account_id": "string"}}),
        ("create_support_ticket",  "Create a support ticket for a customer issue",
         {"parameters": {"customer_id": "string", "issue_type": "string", "description": "string", "priority": "string"}}),
        ("send_notification",      "Send an email/Slack/SMS notification to a customer or team",
         {"parameters": {"channel": "string", "recipient": "string", "message": "string"}}),
    ]:
        _register_tool_if_missing(org_id, *t)

    # ── 3. TECHVENTUS ──────────────────────────────────────────
    log.info("\n[3/3] TechVentus (HR & Operations)")
    techventus = _get_or_create_org("TechVentus")
    org_id = techventus["id"]

    _get_or_create_agent(
        org_id,
        name="Riley (HR Bot)",
        role="HR & People Operations",
        job_description=(
            "You are Riley, the HR Bot at TechVentus. You handle recruiting, onboarding, "
            "leave requests, benefits questions, and performance reviews. "
            "Use schedule_interview to book candidate interviews. "
            "Use process_leave_request to approve or deny employee leave. "
            "Use send_notification to communicate with employees and managers. "
            "Be empathetic, professional, and follow company HR policies. "
            "Always check leave balances before approving requests. "
            "Default PTO policy: 20 days/year, unlimited sick days."
        ),
    )
    _get_or_create_agent(
        org_id,
        name="Casey (Ops Bot)",
        role="Operations & Admin",
        job_description=(
            "You are Casey, the Operations Bot at TechVentus. You handle meeting room bookings, "
            "equipment procurement, travel arrangements, and office logistics. "
            "Use schedule_meeting_room to book conference rooms. "
            "Use order_equipment to procure hardware for employees. "
            "Use send_notification to update stakeholders. "
            "Equipment budget: $2,700 per employee. Always confirm with manager for orders over $1,000."
        ),
    )

    _get_or_create_user(org_id, "priya_hr",     "Priya Sharma",  "priya@techventus.com")
    _get_or_create_user(org_id, "david_ops",    "David Park",    "david@techventus.com")
    _get_or_create_user(org_id, "demo_user",    "Demo User",     "demo@techventus.com")

    _upload_doc_if_missing(org_id, "techventus_hr_process.txt", TECHVENTUS_HR_PROCESS)
    _upload_doc_if_missing(org_id, "techventus_team.txt",       TECHVENTUS_TEAM)

    for t in [
        ("schedule_interview",    "Schedule a candidate interview with Zoom link",
         {"parameters": {"candidate_name": "string", "candidate_email": "string", "position": "string", "date": "string", "time": "string"}}),
        ("process_leave_request", "Process an employee PTO/sick/parental leave request",
         {"parameters": {"employee_name": "string", "leave_type": "string", "start_date": "string", "end_date": "string"}}),
        ("schedule_meeting_room", "Book a conference room for a team meeting",
         {"parameters": {"date": "string", "start_time": "string", "end_time": "string", "attendees": "integer", "purpose": "string"}}),
        ("order_equipment",       "Order equipment/hardware for an employee via Coupa",
         {"parameters": {"employee_name": "string", "items": "array"}}),
        ("send_notification",     "Send a Slack or email notification to an employee or team",
         {"parameters": {"channel": "string", "recipient": "string", "message": "string"}}),
    ]:
        _register_tool_if_missing(org_id, *t)

    log.info("\n" + "=" * 60)
    log.info("DEMO SETUP — complete")
    log.info("Organizations: Amazon | Stripe | TechVentus")
    log.info("=" * 60)

    return {
        "status": "success",
        "organizations": {
            "amazon":     amazon["id"],
            "stripe":     stripe["id"],
            "techventus": techventus["id"],
        },
    }


if __name__ == "__main__":
    run()
