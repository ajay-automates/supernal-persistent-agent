# 🏗️ Supernal Persistent Agent - Complete Architecture

A comprehensive guide to understanding the 3-tier multi-tenant AI agent platform with role-based access control, persistent memory, and tool execution.

---

## 📊 Current Deployment Statistics

### Database Overview
```
├── Organizations:          6
├── AI Employees:          24 (4 per organization)
├── Users:                 13 (distributed across orgs)
├── Roles:                 14 (role types)
├── Tools:                 5 (executable actions)
└── Tool Executions:       (audit trail + verification dashboard)
```

### Organizations Deployed
1. **Amazon** — Sales & operations company
2. **Stripe** — Payment processing company
3. **TechVentus** — Tech startup
4. **InsureAll Inc** — Insurance company
5. **CreativeWorks Agency** — Creative agency
6. **TalentMatch Inc** — Recruiting company

---

## 🎯 Core Concept: 3-Tier Multi-Tenant Architecture

The system is built on three levels of hierarchy with complete data isolation at each level:

```
┌─────────────────────────────────────────────────────────┐
│ ORGANIZATION (Top Level - Tenant)                       │
│ • Amazon, Stripe, TechVentus, etc.                      │
│ • Owns documents/knowledge base (shared by all staff)   │
│ • Has multiple AI employees                            │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐│
│ │ AI EMPLOYEE (Middle Level - Staff Member)            ││
│ │ • Name: "Alex (Sales Bot)"                           ││
│ │ • Role: "Sales Development Rep (SDR)"               ││
│ │ • Assigned to specific users                         ││
│ │ • Has role-based tool permissions                    ││
│ │                                                       ││
│ │ ┌──────────────────────────────────────────────────┐││
│ │ │ USER (Bottom Level - Person)                     │││
│ │ │ • Name: "Ajay"                                   │││
│ │ │ • Belongs to org + assigned to AI employee       │││
│ │ │ • Has conversation history (scoped to this       │││
│ │ │   employee + this org + this user)               │││
│ │ │                                                   │││
│ │ │ ┌──────────────────────────────────────────────┐│││
│ │ │ │ CONVERSATION / MEMORY                        ││││
│ │ │ │ • Question: "Send email to..."               ││││
│ │ │ │ • Answer: "Done! Email sent to..."           ││││
│ │ │ │ • Tool Used: send_email                      ││││
│ │ │ │ • Timestamp: 2026-03-15T10:30:00             ││││
│ │ │ └──────────────────────────────────────────────┘│││
│ │ └──────────────────────────────────────────────────┘││
│ └──────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Organizations (6 Total)

Each organization is a **completely isolated tenant** with its own:
- Knowledge base (documents & vector embeddings)
- AI employees (staff)
- Users (people)
- Tools (registered endpoints)
- Audit trail

### Organization List

| Name | Industry | AI Employees | Users |
|------|----------|--------------|-------|
| Amazon | Sales & Ops | Alex (SDR), Maya (Support), David (Content), Quinn (Ops) | Ajay, Naveen, Dexter |
| Stripe | Payment Processing | Jordan (Support), Sam (Claims), Riley (Finance), Casey (Social) | Emma, James, Michael |
| TechVentus | Tech Startup | Quinn (Dispatch), Riley (Scheduler), Jordan (Ops), Maya (Support) | Sarah, Chris, Pat |
| InsureAll Inc | Insurance | Sam (Claims), Alex (Underwriting), Jordan (Support), Riley (Finance) | Lisa, Tom, Robert |
| CreativeWorks Agency | Creative Agency | Casey (Social), David (Content), Alex (Sales), Quinn (Ops) | Susan |
| TalentMatch Inc | Recruiting | Alex (Recruiter), Maya (Onboarding), David (Sales), Casey (Content) | (Additional users) |

**Key Point:** Users in **Amazon** have completely separate conversations and data from users in **Stripe**. There is no cross-org data leakage.

---

## 🤖 AI Employees (24 Total - 4 Per Organization)

Each AI employee is a **virtual team member** with:
- Unique name and personality
- Specific role (determines tool access)
- Job description
- Persistent conversation memory with each user
- Semantic memory (topic-based) for intelligent context

### All 24 AI Employees by Organization

#### **Amazon** (4 employees)
- **Alex (Sales Bot)** — Role: Sales Development Rep (SDR)
  - Job: Research prospects, send personalized outreach, update CRM, schedule discovery calls
  - Tools: ✓ send_email, ✓ create_crm_lead

- **Maya (Support Bot)** — Role: Customer Support Agent
  - Job: Resolve customer issues, search help content, verify account status, create support tickets
  - Tools: ✓ create_support_ticket, ✓ send_email

- **David (Content Bot)** — Role: Content Creator
  - Job: Write blog posts, create campaign content, manage content calendar
  - Tools: (None - read-only)

- **Quinn (Ops Bot)** — Role: Operations Coordinator
  - Job: Coordinate deliveries, update operational records, notify vendors
  - Tools: (None - read-only)

#### **Stripe** (4 employees)
- **Jordan (Support Bot)** — Role: Customer Support Agent
  - Tools: ✓ create_support_ticket, ✓ send_email

- **Sam (Claims Bot)** — Role: Insurance Claims Processor
  - Tools: (None - specialized for insurance, not general)

- **Riley (Finance Bot)** — Role: Finance Coordinator
  - Tools: (None - financial data handler)

- **Casey (Social Bot)** — Role: Social Media Manager
  - Tools: (None - content-only)

#### **TechVentus** (4 employees)
- **Quinn (Dispatch Bot)** — Role: Dispatch Manager
  - Tools: (None - dispatch-specific)

- **Riley (Scheduler Bot)** — Role: Customer Scheduler
  - Tools: (None - scheduling assistant)

- **Jordan (Ops Bot)** — Role: Operations Coordinator
  - Tools: (None - operations-only)

- **Maya (Support Bot)** — Role: Customer Support Agent
  - Tools: ✓ create_support_ticket, ✓ send_email

#### **InsureAll Inc** (4 employees)
- **Sam (Claims Bot)** — Role: Insurance Claims Processor
  - Tools: (None)

- **Alex (Underwriting Bot)** — Role: Insurance Underwriter Assistant
  - Tools: (None)

- **Jordan (Support Bot)** — Role: Customer Support Agent
  - Tools: ✓ create_support_ticket, ✓ send_email

- **Riley (Finance Bot)** — Role: Finance Coordinator
  - Tools: (None)

#### **CreativeWorks Agency** (4 employees)
- **Casey (Social Bot)** — Role: Social Media Manager
  - Tools: (None)

- **David (Content Bot)** — Role: Content Creator
  - Tools: (None)

- **Alex (Sales Bot)** — Role: Sales Development Rep (SDR)
  - Tools: ✓ send_email, ✓ create_crm_lead

- **Quinn (Ops Bot)** — Role: Operations Coordinator
  - Tools: (None)

#### **TalentMatch Inc** (4 employees)
- **Alex (Recruiter Bot)** — Role: Recruiter
  - Tools: ✓ send_email

- **Maya (Onboarding Bot)** — Role: Onboarding Specialist
  - Tools: (None)

- **David (Sales Bot)** — Role: Sales Development Rep (SDR)
  - Tools: ✓ send_email, ✓ create_crm_lead

- **Casey (Content Bot)** — Role: Content Creator
  - Tools: (None)

---

## 👥 Users (13 Total)

Users are **actual people** who interact with AI employees. Each user:
- Belongs to exactly ONE organization
- Can be assigned to multiple AI employees within their org
- Has separate conversation history with each assigned AI employee
- Cannot see other users' conversations (data isolation)

### User Directory

| User ID | Name | Organization | Assigned AI Employees |
|---------|------|---------------|----------------------|
| ajay | Ajay | Amazon | All 4 Amazon employees |
| naveen | Naveen | Amazon | Alex (Sales), Maya (Support) |
| dexter | Dexter | Amazon | All 4 Amazon employees |
| emma | Emma | Stripe | Jordan (Support), Riley (Finance) |
| james | James | Stripe | All 4 Stripe employees |
| michael | Michael | Stripe | Sam (Claims), Casey (Social) |
| sarah | Sarah | TechVentus | All 4 TechVentus employees |
| chris | Chris | TechVentus | Quinn (Dispatch), Riley (Scheduler) |
| pat | Pat | TechVentus | Jordan (Ops), Maya (Support) |
| lisa | Lisa | InsureAll Inc | Sam (Claims), Alex (Underwriting) |
| tom | Tom | InsureAll Inc | Jordan (Support), Riley (Finance) |
| robert | Robert | InsureAll Inc | All 4 InsureAll employees |
| susan | Susan | CreativeWorks Agency | All 4 Agency employees |

---

## 🎭 Roles (14 Total - Hierarchical Permission System)

Roles are the **key to tool access control**. A role defines:
- What the AI employee can do
- What tools they're authorized to use
- Their permissions and restrictions

### Roles with Tool Access (5 Roles)

#### 1. **Sales Development Rep (SDR)** 🎯 Sales
- **Purpose:** Prospect new customers, send outreach, manage sales pipeline
- **Allowed Tools:**
  - ✓ `send_email` — Send cold outreach emails
  - ✓ `create_crm_lead` — Add prospects to CRM system
- **Example Users:** Ajay talking to Alex (Sales Bot)
- **Conversation Example:**
  ```
  User: "Send an email to john@techcompany.com about our product"
  Alex: "I'll draft and send that for you..."
  Tool Used: send_email
  Result: Email sent successfully ✓
  ```

#### 2. **Customer Support Agent** 🎧 Support
- **Purpose:** Resolve customer issues, handle support tickets
- **Allowed Tools:**
  - ✓ `send_email` — Email customers with solutions
  - ✓ `create_support_ticket` — File tickets for escalation
- **Example Users:** Any user talking to Maya (Support Bot)
- **Conversation Example:**
  ```
  User: "A customer can't login to their account"
  Maya: "I'll create a support ticket for this..."
  Tool Used: create_support_ticket
  Result: Ticket #12345 created ✓
  ```

#### 3. **Sales Manager** 📊 Sales (Full Permissions)
- **Purpose:** Manage sales team, oversee deals, schedule calls
- **Allowed Tools:**
  - ✓ `send_email` — Email customers/team
  - ✓ `create_crm_lead` — Add high-value leads
  - ✓ `schedule_calendar_event` — Schedule sales meetings
- **Highest Sales Permissions** among sales roles

#### 4. **Operations Manager** ⚙️ Operations
- **Purpose:** Manage operations, order equipment, schedule events
- **Allowed Tools:**
  - ✓ `place_equipment_order` — Order equipment/supplies
  - ✓ `schedule_calendar_event` — Schedule operational meetings
- **Example:** Quinn (Ops Bot) coordinating deliveries

#### 5. **Recruiter** 👥 HR
- **Purpose:** Source talent, send recruitment outreach
- **Allowed Tools:**
  - ✓ `send_email` — Send recruitment emails only
- **Minimal Permissions** — recruitment-focused
- **Example:** Alex (Recruiter Bot) at TalentMatch Inc

### Roles WITHOUT Tool Access (9 Roles)

These roles can **read, discuss, and analyze** but cannot execute any tools:

| Role | Category | Reason |
|------|----------|--------|
| Content Creator | Marketing | Content-only, no execution needed |
| Operations Coordinator | Operations | Coordinator (no autonomous decisions) |
| Insurance Claims Processor | Insurance | Highly regulated, manual review required |
| Finance Coordinator | Finance | Financial decisions need approval |
| Social Media Manager | Marketing | Post-only through platform, no tools |
| Dispatch Manager | Operations | Should not autonomously dispatch |
| Customer Scheduler | Support | Booking only, requires confirmation |
| Insurance Underwriter Assistant | Insurance | Regulated industry, needs human approval |
| Onboarding Specialist | HR | HR processes need manager approval |

---

## 🔐 Role-Based Access Control (RBAC) System

### How Tool Access Works

When a user sends a message to an AI employee, the system checks:

```
1. Is the user assigned to this AI employee?
   └─ Check: user_ai_employee_assignments table
   └─ If NO → Return 403 Forbidden

2. Does the AI employee have a role?
   └─ Check: ai_employees.role_id
   └─ If NO → No tool access (read-only)

3. Does this role have permission for the requested tool?
   └─ Check: role_tool_permissions table
   └─ WHERE role_id = AI_EMPLOYEE.role_id
   └─ AND tool_name = REQUESTED_TOOL
   └─ AND allowed = TRUE
   └─ If NO → Return 403 Denied

4. Execute the tool with full logging
   └─ Log: input parameters, output result, latency
   └─ Store in: tool_executions table
```

### Example: Access Denied

```
User: Ajay
AI Employee: David (Content Bot)
Role: Content Creator
Requested Tool: send_email
```

**Flow:**
```
✓ Is Ajay assigned to David? YES
✓ Does David have a role? YES (Content Creator)
✗ Can Content Creator use send_email? NO
  └─ Reason: Content Creator has NO tools
└─ Result: 403 Forbidden
   Message: "This role does not have access to send_email"
```

### Example: Access Allowed

```
User: Ajay
AI Employee: Alex (Sales Bot)
Role: Sales Development Rep (SDR)
Requested Tool: send_email
```

**Flow:**
```
✓ Is Ajay assigned to Alex? YES
✓ Does Alex have a role? YES (SDR)
✓ Can SDR use send_email? YES
  └─ Confirmed in role_tool_permissions
✓ Execute tool
├─ Input: recipient="john@company.com", subject="...", body="..."
├─ Latency: 245ms
└─ Result: {"status": "sent", "message_id": "msg_123"}
```

---

## 🔧 Tools (5 Available)

All tools are **mocked** (safe for demo) but fully logged in the verification dashboard:

### 1. `send_email` 📧
- **Description:** Send emails to contacts
- **Allowed for Roles:** SDR, Support Agent, Sales Manager, Recruiter
- **Parameters:**
  ```json
  {
    "to_email": "recipient@example.com",
    "subject": "Your Subject Here",
    "body": "Email body content...",
    "cc": "optional@example.com"
  }
  ```
- **Verification Dashboard:** `/api/verify/emails/{org_id}`
- **Log Location:** `emails_sent` table

### 2. `create_crm_lead` 🎯
- **Description:** Add leads to CRM system
- **Allowed for Roles:** SDR, Sales Manager
- **Parameters:**
  ```json
  {
    "company_name": "Company Name",
    "contact_name": "Contact Name",
    "email": "contact@company.com",
    "phone": "+1-555-0100",
    "status": "new"
  }
  ```
- **Verification Dashboard:** `/api/verify/crm-leads/{org_id}`
- **Log Location:** `crm_leads` table

### 3. `create_support_ticket` 🎫
- **Description:** Create support tickets for escalation
- **Allowed for Roles:** Support Agent
- **Parameters:**
  ```json
  {
    "customer_email": "customer@example.com",
    "subject": "Issue Title",
    "description": "Detailed issue description",
    "priority": "high",
    "category": "billing"
  }
  ```
- **Verification Dashboard:** `/api/verify/tickets/{org_id}`
- **Log Location:** `support_tickets` table

### 4. `schedule_calendar_event` 📅
- **Description:** Schedule calendar events (meetings, calls)
- **Allowed for Roles:** Sales Manager, Operations Manager
- **Parameters:**
  ```json
  {
    "title": "Sales Call with Acme Corp",
    "description": "Discuss implementation timeline",
    "start_time": "2026-03-20T10:00:00",
    "end_time": "2026-03-20T11:00:00",
    "attendee_email": "contact@acme.com"
  }
  ```
- **Verification Dashboard:** `/api/verify/calendar/{org_id}`
- **Log Location:** `calendar_events` table

### 5. `place_equipment_order` 📦
- **Description:** Place equipment orders
- **Allowed for Roles:** Operations Manager
- **Parameters:**
  ```json
  {
    "item_name": "Office Chairs",
    "quantity": 10,
    "cost_usd": 1500.00,
    "delivery_date": "2026-04-01"
  }
  ```
- **Verification Dashboard:** `/api/verify/equipment/{org_id}`
- **Log Location:** `equipment_orders` table

---

## 💾 Database Schema (Data Isolation)

### Key Tables

#### `organizations`
- Stores tenant information
- Every other table has `organization_id` foreign key
- Complete data isolation per org

```sql
id UUID PRIMARY KEY
name TEXT UNIQUE NOT NULL
created_at TIMESTAMP DEFAULT now()
```

#### `ai_employees`
- Virtual team members
- Links to organization + role
- Has job_description for persona building

```sql
id UUID PRIMARY KEY
organization_id UUID (FK → organizations)
name TEXT NOT NULL
role TEXT
role_id UUID (FK → ai_employee_roles)
job_description TEXT
```

#### `users`
- Real people using the system
- Belongs to exactly ONE organization

```sql
id UUID PRIMARY KEY
organization_id UUID (FK → organizations)
user_id TEXT UNIQUE (within org)
name TEXT
email TEXT
assigned_ai_employees UUID[] (array of IDs)
```

#### `conversations`
- Persistent memory for each (org, employee, user) triple
- Used for semantic search and context retrieval

```sql
id UUID PRIMARY KEY
organization_id UUID (FK)
ai_employee_id UUID (FK)
user_id TEXT
role TEXT ('user' or 'assistant')
content TEXT
timestamp TIMESTAMP DEFAULT now()

-- Index for fast lookup
CREATE INDEX conversations_org_ai_user
ON conversations(organization_id, ai_employee_id, user_id)
```

#### `organization_documents` & `organization_chunks`
- Shared knowledge base per org
- Documents are split into chunks for vector search
- Embeddings stored for semantic retrieval

```sql
-- organization_documents
id UUID PRIMARY KEY
organization_id UUID (FK)
filename TEXT
source TEXT
uploaded_at TIMESTAMP

-- organization_chunks
id UUID PRIMARY KEY
organization_id UUID (FK)
text TEXT
embedding VECTOR(1536)  -- OpenAI embeddings
source TEXT
created_at TIMESTAMP
```

#### `tool_executions`
- Audit trail for all tool calls
- Shows what was executed, result, latency

```sql
id UUID PRIMARY KEY
organization_id UUID (FK)
ai_employee_id UUID (FK)
user_id TEXT
tool_name TEXT
input_params JSONB
output_result JSONB
status TEXT ('success', 'denied', 'failed')
error_message TEXT
latency_ms INT
executed_at TIMESTAMP DEFAULT now()
```

#### RBAC Tables
- `ai_employee_roles` — Role definitions
- `role_tool_permissions` — Which roles can use which tools
- `rbac_tools` — Tool catalog

---

## 🔄 Conversation Flow

### Step-by-Step: User Chats with AI Employee

```
1. USER SENDS MESSAGE
   POST /api/chat
   {
     "organization_id": "org_123",
     "ai_employee_id": "emp_456",
     "user_id": "ajay",
     "question": "Send an email to John"
   }

2. SYSTEM VALIDATES
   ✓ Organization exists
   ✓ AI employee exists in this org
   ✓ User exists in this org
   ✓ User is assigned to this AI employee

3. RETRIEVE CONTEXT
   └─ Get org's documents (vector search)
   └─ Get this user's conversation history with this employee
   └─ Retrieve semantically similar past turns

4. BUILD PERSONA
   └─ org_name: "Amazon"
   └─ employee_name: "Alex"
   └─ employee_role: "Sales Development Rep (SDR)"
   └─ job_description: "Research prospects, send outreach..."

5. FIRST LLM CALL
   └─ Model: GPT-4o-mini
   └─ Task: "Should I use a tool for this request?"
   └─ Response: "I'll use send_email tool"

6. EXTRACT TOOL CALL
   └─ Parse response for: TOOL: send_email
   └─ Parse response for: PARAMS: { "to_email": "...", ... }

7. VALIDATE TOOL ACCESS (RBAC)
   ├─ Is user assigned to employee? ✓
   ├─ Does employee have a role? ✓
   ├─ Can this role use send_email? ✓
   └─ All checks pass → Proceed

8. EXECUTE TOOL
   └─ Call tool_functions["send_email"](params)
   └─ Log execution with timestamp and latency

9. SECOND LLM CALL (if tool used)
   └─ Return: "Email sent successfully"
   └─ Model generates natural language response

10. SAVE CONVERSATION
    ├─ Save user message to conversations table
    ├─ Save assistant response to conversations table
    └─ Trigger background job to embed the turn for semantic memory

11. RETURN RESPONSE
    {
      "answer": "I've sent the email to John...",
      "tool_used": "send_email",
      "tool_result": {
        "status": "sent",
        "message_id": "msg_789"
      },
      "sources": ["document.pdf"],
      "memory_used": true
    }
```

---

## 📊 Observability & Auditing

### API Logs
Every API request is logged:
- Endpoint, method, status code
- Latency in milliseconds
- Timestamp

### Tool Execution Logs
Every tool execution is logged with:
- Who called it (org, employee, user)
- What tool was called
- Input parameters
- Output result
- Execution status
- Latency

### Verification Dashboards
View all executions for an organization:
- `/api/verify/emails/{org_id}` — All emails sent
- `/api/verify/crm-leads/{org_id}` — All CRM leads added
- `/api/verify/tickets/{org_id}` — All support tickets created
- `/api/verify/calendar/{org_id}` — All calendar events scheduled
- `/api/verify/equipment/{org_id}` — All equipment orders placed

### LLM Call Tracking
- Model name (gpt-4o-mini)
- Token counts (prompt, completion, total)
- Latency per request
- Cost estimation

---

## 🔒 Security & Data Isolation

### Complete Data Isolation

Every query includes `WHERE organization_id = ?` automatically:

```python
# Getting conversations
conversations = supabase.table("conversations") \
  .select("*") \
  .eq("organization_id", org_id) \
  .eq("ai_employee_id", employee_id) \
  .eq("user_id", user_id) \
  .execute()

# User A cannot see User B's data
# Organization A cannot see Organization B's data
```

### Three Levels of Permission Checking

1. **Organization Level** — Is the org valid?
2. **User Level** — Is the user in this org?
3. **Role Level** — Can this role use this tool?

### No Credential Leakage
- `.env` is NOT committed to Git
- API keys stored only in environment variables
- Database credentials never in logs
- All secrets rotated per deployment

---

## 🚀 API Endpoints Overview

### Organizations
```
POST   /api/organization
GET    /api/organization/{org_id}
GET    /api/organizations
```

### AI Employees
```
POST   /api/ai-employee
GET    /api/ai-employees/{org_id}
GET    /api/agents/{organization_id}/{user_id}
GET    /api/agent-info/{organization_id}/{ai_employee_id}
```

### Users
```
POST   /api/user
GET    /api/users/{org_id}
DELETE /api/user/{user_id}
POST   /api/assign-ai-employee
```

### Chat (Core Feature)
```
POST   /api/chat                    (single request-response)
POST   /api/chat/stream             (streaming SSE)
```

### Memory
```
GET    /api/memory?organization_id=...&ai_employee_id=...&user_id=...
DELETE /api/memory?organization_id=...&ai_employee_id=...&user_id=...
```

### Tools & Verification
```
POST   /api/tools/register
GET    /api/tools/{organization_id}
GET    /api/verify/emails/{organization_id}
GET    /api/verify/crm-leads/{organization_id}
GET    /api/verify/tickets/{organization_id}
GET    /api/verify/calendar/{organization_id}
GET    /api/verify/equipment/{organization_id}
```

---

## 📈 Scaling Considerations

### Horizontal Scaling ✓
- Each request is independent
- No shared state between requests
- Can add more server instances

### Database Indexing ✓
```sql
-- Key indexes for performance
idx_conversations_org_ai_user
idx_organization_chunks_org
idx_tool_executions_org_ai_user
idx_llm_calls_organization
```

### Vector Search Optimization ✓
- pgvector extension with HNSW indexes
- Efficient similarity search
- Scales to millions of chunks

### Cost Optimization ✓
- OpenAI embeddings: ~$0.00002 per token
- GPT-4o-mini: ~$0.00015 per prompt token, $0.0006 per completion token
- Supabase free tier: 1M tokens/month
- Cost tracking built-in

---

## 🎓 Example Scenarios

### Scenario 1: SDR Sending Cold Email

```
Organization: Amazon
User: Ajay
AI Employee: Alex (Sales Bot)
Role: Sales Development Rep (SDR)

User: "Send an email to john@techcompany.com about our enterprise plan"

System checks:
✓ Ajay is in Amazon org
✓ Ajay is assigned to Alex
✓ Alex is a Sales Development Rep (SDR)
✓ SDR has permission to use send_email

Result:
✓ Email sent to john@techcompany.com
✓ Logged in emails_sent table
✓ Visible in /api/verify/emails/amazon_org_id
```

### Scenario 2: Support Agent Creating Ticket

```
Organization: Stripe
User: Emma
AI Employee: Jordan (Support Bot)
Role: Customer Support Agent

User: "A customer reported a billing issue, create a support ticket"

System checks:
✓ Emma is in Stripe org
✓ Emma is assigned to Jordan
✓ Jordan is a Customer Support Agent
✓ Support Agent has permission to use create_support_ticket

Result:
✓ Ticket created in support_tickets table
✓ Logged with ticket_id, priority, status
✓ Visible in /api/verify/tickets/stripe_org_id
```

### Scenario 3: Content Creator (No Tool Access)

```
Organization: CreativeWorks Agency
User: Susan
AI Employee: David (Content Bot)
Role: Content Creator

User: "Send an email to the client about the new campaign"

System checks:
✓ Susan is in CreativeWorks Agency
✓ Susan is assigned to David
✓ David is a Content Creator
✗ Content Creator has NO tool permissions

Result:
✗ Request DENIED
Message: "Content Creator role does not have access to send_email"
David can still respond with: "I can draft the email for you to send..."
```

---

## 📝 Key Takeaways

1. **3-Tier Hierarchy** — Organization → AI Employee → User provides complete data isolation
2. **Role-Based Access** — Tools are gated by AI employee role, not user type
3. **Persistent Memory** — Conversations persist across sessions and are searchable
4. **Complete Audit Trail** — Every tool execution is logged for compliance
5. **Semantic Search** — Past conversations are embedded and searchable by topic
6. **Scalable Architecture** — Designed for horizontal scaling with proper indexing
7. **Security First** — Multiple layers of permission checking, no credential leakage
8. **Production Ready** — FastAPI async, database indexes, cost tracking, error logging

---

## 🔗 Related Documentation

- [README.md](README.md) — Setup and deployment
- [DATABASE_SETUP.sql](DATABASE_SETUP.sql) — Schema creation
- [FIX_SCHEMA.sql](FIX_SCHEMA.sql) — Schema fixes and RBAC seeding
- [ADD_MISSING_ROLES.sql](ADD_MISSING_ROLES.sql) — Additional role definitions

---

**Last Updated:** March 15, 2026
**Deployment:** Supernal Persistent Agent v2.0.0
**Architecture:** 3-Tier Multi-Tenant with RBAC
