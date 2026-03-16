# 🏗️ Supernal Persistent Agent - Complete Architecture

A comprehensive guide to understanding the 3-tier multi-tenant AI agent platform with role-based access control, persistent memory, and tool execution.

---

## 📊 Current Deployment Statistics

### Database Overview
```
├── Organizations:          3
├── AI Employees:          9 (3 per organization)
├── Users:                 3 (1 per organization)
├── Roles:                 3 (Sales, Support, Operations Manager)
├── Tools:                 5 (executable actions)
└── Tool Executions:       (audit trail + verification dashboard)
```

### Organizations Deployed
1. **Amazon** — Sales & cloud services
2. **Stripe** — Payment processing
3. **TechVentus** — Tech startup

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

## 📚 Organizations (3 Total)

Each organization is a **completely isolated tenant** with its own:
- Knowledge base (documents & vector embeddings)
- AI employees (staff)
- Users (people)
- Tools (registered endpoints)
- Audit trail

### Organization List

| Name | Industry | AI Employees | Users |
|------|----------|--------------|-------|
| Amazon | Sales & Cloud | Alex (Sales), Maya (Support), Quinn (Operations) | Ajay |
| Stripe | Payment Processing | Jordan (Support), Sam (Sales), Riley (Operations) | Emma |
| TechVentus | Tech Startup | Maya (Support), Alex (Sales), Quinn (Operations) | Sarah |

**Key Point:** Users in **Amazon** have completely separate conversations and data from users in **Stripe**. There is no cross-org data leakage.

---

## 🤖 AI Employees (9 Total - 3 Per Organization)

Each AI employee is a **virtual team member** with:
- Unique name
- Specific role (determines tool access)
- Job description
- Persistent conversation memory with each user
- Semantic memory (topic-based) for intelligent context

### All 9 AI Employees by Organization

#### **Amazon** (3 employees)
- **Alex** — Role: Sales Development Rep (SDR)
  - Job: Research prospects, send personalized outreach, update CRM, schedule discovery calls
  - Tools: ✓ send_email, ✓ create_crm_lead

- **Maya** — Role: Customer Support Agent
  - Job: Resolve customer issues, create support tickets, escalate when needed
  - Tools: ✓ create_support_ticket, ✓ send_email

- **Quinn** — Role: Operations Manager
  - Job: Coordinate schedules, place equipment orders, schedule meetings
  - Tools: ✓ place_equipment_order, ✓ schedule_calendar_event

#### **Stripe** (3 employees)
- **Jordan** — Role: Customer Support Agent
  - Job: Handle customer support issues across billing and technical topics
  - Tools: ✓ create_support_ticket, ✓ send_email

- **Sam** — Role: Sales Development Rep (SDR)
  - Job: Prospect new customers, send outreach, manage leads
  - Tools: ✓ send_email, ✓ create_crm_lead

- **Riley** — Role: Operations Manager
  - Job: Schedule meetings, manage operations, place equipment orders
  - Tools: ✓ schedule_calendar_event, ✓ place_equipment_order

#### **TechVentus** (3 employees)
- **Maya** — Role: Customer Support Agent
  - Job: Handle customer service issues and create support tickets
  - Tools: ✓ create_support_ticket, ✓ send_email

- **Alex** — Role: Sales Development Rep (SDR)
  - Job: Prospect and outreach, manage leads, schedule customer calls
  - Tools: ✓ send_email, ✓ create_crm_lead

- **Quinn** — Role: Operations Manager
  - Job: Schedule meetings, coordinate operations, manage equipment
  - Tools: ✓ schedule_calendar_event, ✓ place_equipment_order

---

## 👥 Users (3 Total - 1 Per Organization)

Users are **actual people** who interact with AI employees. Each user:
- Belongs to exactly ONE organization
- Is assigned to all AI employees in their org
- Has separate conversation history with each AI employee
- Cannot see other users' conversations (data isolation)

### User Directory

| User ID | Name | Organization | Assigned AI Employees |
|---------|------|---------------|----------------------|
| ajay | Ajay | Amazon | Alex, Maya, Quinn |
| emma | Emma | Stripe | Jordan, Sam, Riley |
| sarah | Sarah | TechVentus | Maya, Alex, Quinn |

---

## 🎭 Roles (3 Total - Simplified Permission System)

Roles are the **key to tool access control**. A role defines:
- What the AI employee can do
- What tools they're authorized to use
- Their permissions and restrictions

### 3 Core Roles

#### 1. **Sales Development Rep (SDR)** 🎯 Sales
- **Purpose:** Prospect new customers, send outreach, manage sales pipeline
- **Allowed Tools:**
  - ✓ `send_email` — Send outreach emails
  - ✓ `create_crm_lead` — Add prospects to CRM
- **Example Users:** Ajay talking to Alex (Sales Bot)

#### 2. **Customer Support Agent** 🎧 Support
- **Purpose:** Resolve customer issues, handle support tickets
- **Allowed Tools:**
  - ✓ `send_email` — Email customers with solutions
  - ✓ `create_support_ticket` — Create support tickets
- **Example Users:** Ajay talking to Maya (Support Bot)

#### 3. **Operations Manager** ⚙️ Operations/Content
- **Purpose:** Manage operations, schedule meetings, order equipment
- **Allowed Tools:**
  - ✓ `schedule_calendar_event` — Schedule meetings/calls
  - ✓ `place_equipment_order` — Order equipment/supplies
- **Example Users:** Ajay talking to Quinn (Ops Bot)

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

## 🔧 Tools (5 Essential)

All tools are **mocked** (safe for demo) but fully logged in the verification dashboard:

### 1. `send_email` 📧
- **Description:** Send emails to contacts
- **Allowed for Roles:** Sales Development Rep, Customer Support Agent
- **Parameters:**
  ```json
  {
    "to": "recipient@example.com",
    "subject": "Your Subject Here",
    "body": "Email body content...",
    "cc": "optional@example.com"
  }
  ```
- **Verification Dashboard:** `/api/verify/emails/{org_id}`

### 2. `create_crm_lead` 🎯
- **Description:** Add leads to CRM system
- **Allowed for Roles:** Sales Development Rep
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

### 3. `create_support_ticket` 🎫
- **Description:** Create support tickets for escalation
- **Allowed for Roles:** Customer Support Agent
- **Parameters:**
  ```json
  {
    "customer_email": "customer@example.com",
    "subject": "Issue Title",
    "description": "Detailed issue description",
    "priority": "medium"
  }
  ```
- **Verification Dashboard:** `/api/verify/tickets/{org_id}`

### 4. `schedule_calendar_event` 📅
- **Description:** Schedule calendar events (meetings, calls)
- **Allowed for Roles:** Operations Manager
- **Parameters:**
  ```json
  {
    "title": "Sales Call with Acme Corp",
    "attendee_email": "contact@acme.com",
    "start_time": "2026-03-20T10:00:00",
    "end_time": "2026-03-20T11:00:00"
  }
  ```
- **Verification Dashboard:** `/api/verify/calendar/{org_id}`

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

### Scenario 3: Operations Manager Scheduling Event

```
Organization: TechVentus
User: Sarah
AI Employee: Quinn (Operations Bot)
Role: Operations Manager

User: "Schedule a meeting with our client for next Tuesday at 2pm"

System checks:
✓ Sarah is in TechVentus org
✓ Sarah is assigned to Quinn
✓ Quinn is an Operations Manager
✓ Operations Manager has permission to use schedule_calendar_event

Result:
✓ Meeting scheduled
✓ Logged in calendar_events table
✓ Visible in /api/verify/calendar/techventus_org_id
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
**Deployment:** Supernal Persistent Agent v2.1.0 (Simplified)
**Architecture:** 3-Tier Multi-Tenant with RBAC (3 orgs, 9 employees, 3 users, 3 roles, 5 tools)
