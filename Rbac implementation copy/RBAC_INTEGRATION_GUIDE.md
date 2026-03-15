# 🚀 COMPLETE RBAC INTEGRATION GUIDE

**Implementation Time: 2-3 hours**
**Complexity: Medium**
**Impact: MASSIVE for Monday demo**

---

## 📋 FILES PROVIDED

1. **01_supernal_rbac_schema.sql** - Database schema (run in Supabase)
2. **02_rbac_implementation.py** - RBAC logic (copy into your code)
3. **03_demo_setup.py** - Demo data (run on startup)
4. This guide

---

## ✅ STEP-BY-STEP IMPLEMENTATION

### STEP 1: Update Database Schema (10 minutes)

**In Supabase SQL Editor:**

1. Copy content of `01_supernal_rbac_schema.sql`
2. Paste into Supabase SQL Editor
3. Run all queries
4. Verify tables created:
   - `ai_employee_roles` (12 rows)
   - `tools` (40+ rows)
   - `role_tool_permissions` (144+ rows)
   - `user_ai_employee_assignments` (table)
   - `tool_access_attempts` (table)

---

### STEP 2: Update Your `db.py` File (10 minutes)

Add these helper functions to `db.py`:

```python
# Add to db.py

def get_role_id_by_name(role_name: str):
    """Get role ID by role name"""
    try:
        result = supabase.table('ai_employee_roles').select('id').eq(
            'role_name', role_name
        ).single().execute()
        return result.data['id'] if result.data else None
    except:
        return None

def get_ai_employee_by_id(ai_employee_id: str, org_id: str):
    """Get AI employee details including role"""
    try:
        result = supabase.table('ai_employees').select('*').eq(
            'ai_employee_id', ai_employee_id
        ).eq('organization_id', org_id).single().execute()
        return result.data
    except:
        return None

def get_allowed_tools_for_role(role_id: str):
    """Get all tools allowed for a role"""
    try:
        result = supabase.table('role_tool_permissions').select(
            'tool_name'
        ).eq('role_id', role_id).eq('allowed', True).execute()
        return [item['tool_name'] for item in result.data] if result.data else []
    except:
        return []

def log_access_attempt(org_id: str, user_id: str, ai_employee_id: str,
                      tool_name: str, allowed: bool, reason: str = None):
    """Log tool access attempts"""
    try:
        supabase.table('tool_access_attempts').insert({
            'organization_id': org_id,
            'user_id': user_id,
            'ai_employee_id': ai_employee_id,
            'tool_name': tool_name,
            'allowed': allowed,
            'reason': reason
        }).execute()
    except Exception as e:
        print(f"Error logging access: {e}")

def check_user_access_to_agent(user_id: str, ai_employee_id: str, org_id: str):
    """Check if user is assigned to an AI employee"""
    try:
        result = supabase.table('user_ai_employee_assignments').select(
            'id'
        ).eq('organization_id', org_id).eq(
            'user_id', user_id
        ).eq('ai_employee_id', ai_employee_id).execute()
        return len(result.data) > 0 if result.data else False
    except:
        return False

def check_tool_permission(role_id: str, tool_name: str):
    """Check if role can use tool"""
    try:
        result = supabase.table('role_tool_permissions').select(
            'allowed'
        ).eq('role_id', role_id).eq('tool_name', tool_name).single().execute()
        return result.data['allowed'] if result.data else False
    except:
        return False
```

---

### STEP 3: Create RBAC Module (20 minutes)

**Create new file: `rbac.py`**

Copy content from `02_rbac_implementation.py` into a new file called `rbac.py`

---

### STEP 4: Update `agent.py` to Use RBAC (30 minutes)

**Modify your existing `agent.py`:**

```python
# At top of agent.py
from rbac import RoleBasedAccessControl, execute_tool_with_rbac_validation

# In your agent class __init__:
class Agent:
    def __init__(self, supabase_client):
        self.db = supabase_client
        self.rbac = RoleBasedAccessControl(supabase_client)
    
    # Add this method to get agent info with role
    def get_agent_with_role(self, ai_employee_id: str, org_id: str):
        """Get agent details including their role and allowed tools"""
        return self.rbac.get_agent_info(ai_employee_id, org_id)
    
    # Modify your existing chat method
    async def chat(self, user_id: str, organization_id: str, ai_employee_id: str, 
                   question: str):
        """Chat with an AI employee (with RBAC validation)"""
        
        # Get agent info with role
        agent_info = self.rbac.get_agent_info(ai_employee_id, organization_id)
        
        if not agent_info:
            return {"error": "AI employee not found"}
        
        # Get allowed tools for this agent
        allowed_tools = self.rbac.get_allowed_tools_for_role(agent_info['role_id'])
        
        # Build system prompt with role info
        role_info = agent_info.get('role', {})
        system_prompt = f"""You are {agent_info['name']}.

Role: {role_info.get('role_name')}

Job Description:
{role_info.get('job_description')}

You can ONLY use these tools: {', '.join(allowed_tools)}

If the user asks you to do something outside your role or tools, politely decline and explain what you CAN do.
"""
        
        # ... rest of your chat logic ...
        
        # When routing tool calls, use RBAC validation
        tool_result = execute_tool_with_rbac_validation(
            user_id, ai_employee_id, tool_name, params,
            organization_id, self.rbac, self.db
        )
        
        return tool_result
```

---

### STEP 5: Update `main.py` FastAPI Endpoints (30 minutes)

**Modify your existing endpoints to include RBAC:**

```python
# In main.py

from rbac import RoleBasedAccessControl

# Initialize RBAC at startup
rbac = RoleBasedAccessControl(supabase)

@app.post("/api/chat")
async def chat_with_validation(
    user_id: str,
    organization_id: str,
    ai_employee_id: str,
    question: str
):
    """Chat endpoint with full RBAC validation"""
    
    # Get agent with role info
    agent_info = rbac.get_agent_info(ai_employee_id, organization_id)
    
    if not agent_info:
        return {"error": "AI employee not found"}
    
    # Get user's assigned agents
    user_agents = rbac.get_user_assigned_agents(user_id, organization_id)
    user_agent_ids = [a['ai_employee_id'] for a in user_agents]
    
    # Check if user has access
    if ai_employee_id not in user_agent_ids:
        return {
            "error": f"You don't have access to {agent_info['name']}",
            "assigned_agents": user_agent_ids
        }
    
    # Get allowed tools
    allowed_tools = agent_info.get('allowed_tools', [])
    
    # ... rest of your chat logic ...
    
    return response

@app.get("/api/agents/{organization_id}/{user_id}")
async def get_user_assigned_agents(organization_id: str, user_id: str):
    """Get all agents that a user can access"""
    agents = rbac.get_user_assigned_agents(user_id, organization_id)
    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "assigned_agents": agents,
        "count": len(agents)
    }

@app.get("/api/agent-info/{organization_id}/{ai_employee_id}")
async def get_agent_info(organization_id: str, ai_employee_id: str):
    """Get detailed agent info including role and tools"""
    agent_info = rbac.get_agent_info(ai_employee_id, organization_id)
    if not agent_info:
        return {"error": "Agent not found"}
    return agent_info

@app.get("/api/access-log/{organization_id}")
async def get_access_log(organization_id: str):
    """Get access attempt log"""
    try:
        result = supabase.table('tool_access_attempts').select('*').eq(
            'organization_id', organization_id
        ).order('attempted_at', desc=True).limit(100).execute()
        return {"attempts": result.data if result.data else []}
    except Exception as e:
        return {"error": str(e)}
```

---

### STEP 6: Setup Demo Data (5 minutes)

**In your startup code (main.py):**

```python
from demo_setup import setup_supernal_demo_companies

@app.on_event("startup")
async def startup():
    # Setup demo companies on first run
    print("Initializing Supernal demo companies...")
    setup_supernal_demo_companies(supabase)
    print("✅ Demo companies ready!")
```

---

### STEP 7: Update Frontend `index.html` (30 minutes)

**Add role display to AI employee selector:**

```html
<!-- Update AI Employee selector section -->

<div id="ai-employee-selector" class="form-group">
    <label>AI Employee</label>
    <select id="ai-employee-dropdown">
        <option value="">Select AI Employee...</option>
    </select>
    <div id="ai-employee-details" style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 5px; display: none;">
        <strong id="agent-name"></strong>
        <p id="agent-role" style="color: #666; margin: 5px 0;"></p>
        <p id="agent-tools" style="color: #666; margin: 5px 0;"></p>
        <p id="agent-job" style="margin: 5px 0;"></p>
    </div>
</div>

<script>
// Load agents for selected organization
async function loadAgentsForOrg() {
    const org = document.getElementById('organization-dropdown').value;
    const user = document.getElementById('user-dropdown').value;
    
    if (!org || !user) return;
    
    try {
        const response = await fetch(`/api/agents/${org}/${user}`);
        const data = await response.json();
        
        const dropdown = document.getElementById('ai-employee-dropdown');
        dropdown.innerHTML = '<option value="">Select AI Employee...</option>';
        
        data.assigned_agents.forEach(agent => {
            const option = document.createElement('option');
            option.value = agent.ai_employee_id;
            option.textContent = `${agent.name} (${agent.role ? agent.role.role_name : 'No role'})`;
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading agents:', error);
    }
}

// Show agent details when selected
document.getElementById('ai-employee-dropdown').addEventListener('change', async (e) => {
    const org = document.getElementById('organization-dropdown').value;
    const agentId = e.target.value;
    
    if (!org || !agentId) return;
    
    try {
        const response = await fetch(`/api/agent-info/${org}/${agentId}`);
        const agent = await response.json();
        
        const details = document.getElementById('ai-employee-details');
        document.getElementById('agent-name').textContent = agent.name;
        document.getElementById('agent-role').textContent = `Role: ${agent.role?.role_name || 'N/A'}`;
        document.getElementById('agent-tools').textContent = `Tools: ${agent.allowed_tools?.join(', ') || 'None'}`;
        document.getElementById('agent-job').textContent = agent.job_description;
        
        details.style.display = 'block';
    } catch (error) {
        console.error('Error loading agent info:', error);
    }
});
</script>
```

---

### STEP 8: Testing (30 minutes)

**Test scenarios:**

1. **Test Permission Denied:**
   ```
   Try to make Sales Bot order equipment
   Expected: ❌ Error "Finance tool - not applicable to SDR"
   ```

2. **Test User Access Denied:**
   ```
   Try to access agent not assigned to user
   Expected: ❌ Error "You don't have access to this AI employee"
   ```

3. **Test Allowed Access:**
   ```
   Ask Sales Bot to send an email
   Expected: ✅ Tool executes successfully
   ```

4. **Check Audit Log:**
   ```
   GET /api/access-log/amazon
   Expected: List of all access attempts (allowed and denied)
   ```

---

## 🎯 WHAT THIS GIVES YOU FOR MONDAY

### Before Implementation
```
Amazon Organization
├── Sales Bot (can do ANYTHING)
├── Support Bot (can do ANYTHING)
├── HR Bot (can do ANYTHING)
└── Ajay can access ALL agents and ask them to do ANYTHING
```

### After Implementation (RBAC)
```
Amazon Organization
├── Sales Bot (Sales Development Rep role)
│   ├── Tools allowed: send_email ✅, add_lead_to_crm ✅, schedule_meeting ✅
│   └── Tools denied: process_leave ❌, order_equipment ❌
│
├── Support Bot (Customer Support Agent role)
│   ├── Tools allowed: search_kb ✅, create_ticket ✅
│   └── Tools denied: add_lead_to_crm ❌, post_social ❌
│
├── HR Bot (Operations role)
│   ├── Tools allowed: process_leave ✅, order_equipment ✅
│   └── Tools denied: send_email ❌, add_lead_to_crm ❌
│
└── Ajay (assigned to Sales Bot + HR Bot)
    ├── Can access: Sales Bot, HR Bot
    ├── Cannot access: Support Bot
    └── Audit trail: Every action logged
```

---

## 📊 WHAT DEXTER WILL SEE

**When you show this:**

```
Sales Bot tries to process leave request
→ Permission denied
→ Shows: "Sales Development Rep role cannot use process_leave_request"
→ Shows allowed tools: [send_email, add_lead_to_crm, schedule_meeting]

User tries to access Support Bot (not assigned)
→ Permission denied
→ Shows: "You're assigned to: [Sales Bot, HR Bot]"

Ajay asks Sales Bot to send email
→ Permission allowed
→ Tool executes
→ Shows in verification dashboard
```

**His reaction:**

*"Wait... he implemented full role-based access control? With 12 actual roles? With user assignments? With audit logging? This guy doesn't just understand our business, he built it to SCALE."*

---

## ✅ FINAL CHECKLIST

```
Database Setup:
☐ Run SQL schema in Supabase
☐ Verify 12 roles created
☐ Verify 40+ tools created
☐ Verify permissions table populated (144+ rows)

Code Integration:
☐ Add helper functions to db.py
☐ Create rbac.py module
☐ Update agent.py to use RBAC
☐ Update main.py endpoints
☐ Update index.html frontend

Demo Data:
☐ Create demo_setup.py
☐ Run setup_supernal_demo_companies() on startup
☐ Verify all 6 companies created
☐ Verify all 12 AI employees created
☐ Verify all user assignments created

Testing:
☐ Test permission denied scenario
☐ Test user access denied scenario
☐ Test allowed tool execution
☐ Check access log endpoint
☐ Verify audit trail working

Monday:
☐ Test live URL works with RBAC
☐ Demo role-based restrictions
☐ Show access log/audit trail
☐ Explain Supernal's 12 actual roles
☐ Walk through permission matrix
```

---

## 🚀 EXECUTION TIME

- Database setup: 5 minutes
- Code integration: 90 minutes
- Demo data setup: 5 minutes
- Frontend updates: 30 minutes
- Testing: 30 minutes
- **Total: ~2.5 hours**

You can have this fully implemented and tested tonight!

---

## 💡 THE REAL IMPACT

Most candidates: "I built a system with role-based access"

**You:** Shows Dexter exactly how Supernal works. With their actual 12 roles. With full RBAC. With all demo companies configured. With audit logging.

That's the difference between "interesting" and "when can you start?"

Good luck! 🚀
