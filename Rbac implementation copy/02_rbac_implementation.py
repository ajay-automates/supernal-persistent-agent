"""
ROLE-BASED ACCESS CONTROL (RBAC) FOR AI EMPLOYEES
This module implements complete role-based access control for Supernal's 12 AI employees.
Each AI employee has a role, each role has specific allowed tools, and each user can 
access specific AI employees.
"""

from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# ============================================================================
# RBAC IMPLEMENTATION FOR agent.py
# ============================================================================

class RoleBasedAccessControl:
    """
    Manages role-based access control for AI employees and their tools.
    Ensures only authorized agents can use approved tools.
    """
    
    def __init__(self, supabase_client):
        self.db = supabase_client
        
    # ========================================================================
    # TIER 1: GET AI EMPLOYEE ROLE
    # ========================================================================
    
    def get_ai_employee_role(self, ai_employee_id: str, organization_id: str) -> Dict:
        """Get the role of an AI employee"""
        try:
            result = self.db.table('ai_employees').select(
                'role_id, ai_employees.name'
            ).eq('ai_employee_id', ai_employee_id).eq(
                'organization_id', organization_id
            ).single().execute()
            
            if not result.data:
                return None
            
            role_id = result.data['role_id']
            
            # Get role details
            role_result = self.db.table('ai_employee_roles').select(
                'id, role_name, role_category, description, job_description'
            ).eq('id', role_id).single().execute()
            
            return role_result.data if role_result.data else None
        except Exception as e:
            print(f"Error getting AI employee role: {e}")
            return None
    
    # ========================================================================
    # TIER 2: CHECK IF TOOL IS ALLOWED FOR ROLE
    # ========================================================================
    
    def is_tool_allowed_for_role(self, role_id: str, tool_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a role is allowed to use a specific tool.
        Returns (allowed: bool, reason: str)
        """
        try:
            result = self.db.table('role_tool_permissions').select(
                'allowed, reason'
            ).eq('role_id', role_id).eq('tool_name', tool_name).single().execute()
            
            if result.data:
                allowed = result.data['allowed']
                reason = result.data['reason']
                return (allowed, reason if not allowed else None)
            
            # If permission not found, deny by default
            return (False, "Tool not found in role permissions")
        except Exception as e:
            print(f"Error checking tool permission: {e}")
            return (False, "Error checking permissions")
    
    # ========================================================================
    # TIER 3: GET ALL ALLOWED TOOLS FOR ROLE
    # ========================================================================
    
    def get_allowed_tools_for_role(self, role_id: str) -> List[str]:
        """Get all tools that a role is allowed to use"""
        try:
            result = self.db.table('role_tool_permissions').select(
                'tool_name'
            ).eq('role_id', role_id).eq('allowed', True).execute()
            
            return [item['tool_name'] for item in result.data] if result.data else []
        except Exception as e:
            print(f"Error getting allowed tools: {e}")
            return []
    
    # ========================================================================
    # TIER 4: CHECK USER ACCESS TO AI EMPLOYEE
    # ========================================================================
    
    def can_user_access_ai_employee(self, user_id: str, ai_employee_id: str, 
                                   organization_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a user is assigned to (can access) a specific AI employee.
        Returns (allowed: bool, reason: str)
        """
        try:
            result = self.db.table('user_ai_employee_assignments').select(
                'id'
            ).eq('organization_id', organization_id).eq(
                'user_id', user_id
            ).eq('ai_employee_id', ai_employee_id).execute()
            
            if result.data and len(result.data) > 0:
                return (True, None)
            
            # Get list of assigned agents for user
            assigned_result = self.db.table('user_ai_employee_assignments').select(
                'ai_employee_id'
            ).eq('organization_id', organization_id).eq(
                'user_id', user_id
            ).execute()
            
            assigned_agents = [item['ai_employee_id'] for item in assigned_result.data] if assigned_result.data else []
            
            return (False, f"You don't have access to this AI employee. Assigned: {assigned_agents}")
        except Exception as e:
            print(f"Error checking user access: {e}")
            return (False, "Error checking access permissions")
    
    # ========================================================================
    # TIER 5: VALIDATE COMPLETE PERMISSION CHAIN
    # ========================================================================
    
    def validate_tool_execution(self, user_id: str, ai_employee_id: str, tool_name: str,
                               organization_id: str) -> Tuple[bool, Optional[str]]:
        """
        Complete permission validation:
        1. Can user access this AI employee?
        2. Can this AI employee use this tool?
        
        Returns (allowed: bool, error_message: str)
        """
        
        # CHECK 1: User assigned to this AI employee?
        user_access_allowed, user_error = self.can_user_access_ai_employee(
            user_id, ai_employee_id, organization_id
        )
        
        if not user_access_allowed:
            # Log access attempt
            self.log_access_attempt(organization_id, user_id, ai_employee_id, 
                                   tool_name, False, user_error)
            return (False, user_error)
        
        # CHECK 2: Get AI employee's role
        role = self.get_ai_employee_role(ai_employee_id, organization_id)
        
        if not role:
            error = "AI employee has no role assigned"
            self.log_access_attempt(organization_id, user_id, ai_employee_id, 
                                   tool_name, False, error)
            return (False, error)
        
        # CHECK 3: Can AI employee use this tool?
        tool_allowed, tool_reason = self.is_tool_allowed_for_role(role['id'], tool_name)
        
        if not tool_allowed:
            allowed_tools = self.get_allowed_tools_for_role(role['id'])
            error = f"Role '{role['role_name']}' cannot use '{tool_name}'. Allowed tools: {', '.join(allowed_tools)}"
            self.log_access_attempt(organization_id, user_id, ai_employee_id, 
                                   tool_name, False, error)
            return (False, error)
        
        # ALL CHECKS PASSED
        self.log_access_attempt(organization_id, user_id, ai_employee_id, 
                               tool_name, True, "Tool execution allowed")
        return (True, None)
    
    # ========================================================================
    # TIER 6: LOG ACCESS ATTEMPTS (For audit trail)
    # ========================================================================
    
    def log_access_attempt(self, organization_id: str, user_id: str, 
                          ai_employee_id: str, tool_name: str, 
                          allowed: bool, reason: Optional[str] = None):
        """Log every tool access attempt for audit trail"""
        try:
            self.db.table('tool_access_attempts').insert({
                'organization_id': organization_id,
                'user_id': user_id,
                'ai_employee_id': ai_employee_id,
                'tool_name': tool_name,
                'allowed': allowed,
                'reason': reason,
                'attempted_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error logging access attempt: {e}")
    
    # ========================================================================
    # TIER 7: GET AGENT INFO WITH ROLE
    # ========================================================================
    
    def get_agent_info(self, ai_employee_id: str, organization_id: str) -> Dict:
        """Get AI employee info including their role and allowed tools"""
        try:
            # Get agent details
            agent_result = self.db.table('ai_employees').select('*').eq(
                'ai_employee_id', ai_employee_id
            ).eq('organization_id', organization_id).single().execute()
            
            if not agent_result.data:
                return None
            
            agent = agent_result.data
            
            # Get role
            role = self.get_ai_employee_role(ai_employee_id, organization_id)
            
            if role:
                allowed_tools = self.get_allowed_tools_for_role(role['id'])
                agent['role'] = role
                agent['allowed_tools'] = allowed_tools
            
            return agent
        except Exception as e:
            print(f"Error getting agent info: {e}")
            return None
    
    # ========================================================================
    # TIER 8: GET USER'S ASSIGNED AGENTS
    # ========================================================================
    
    def get_user_assigned_agents(self, user_id: str, organization_id: str) -> List[Dict]:
        """Get all AI employees that a user can access"""
        try:
            # Get assigned agent IDs
            assignments = self.db.table('user_ai_employee_assignments').select(
                'ai_employee_id'
            ).eq('user_id', user_id).eq(
                'organization_id', organization_id
            ).execute()
            
            if not assignments.data:
                return []
            
            agent_ids = [item['ai_employee_id'] for item in assignments.data]
            
            # Get details for each agent
            agents = []
            for agent_id in agent_ids:
                agent_info = self.get_agent_info(agent_id, organization_id)
                if agent_info:
                    agents.append(agent_info)
            
            return agents
        except Exception as e:
            print(f"Error getting user agents: {e}")
            return []


# ============================================================================
# INTEGRATION WITH AGENT EXECUTION
# ============================================================================

def execute_tool_with_rbac_validation(user_id: str, ai_employee_id: str, 
                                     tool_name: str, params: Dict,
                                     organization_id: str,
                                     rbac: RoleBasedAccessControl,
                                     supabase_client) -> Dict:
    """
    Execute a tool ONLY if all RBAC checks pass.
    This function replaces the old tool execution to add permission checks.
    """
    
    # STEP 1: Validate permissions
    allowed, error = rbac.validate_tool_execution(
        user_id, ai_employee_id, tool_name, organization_id
    )
    
    if not allowed:
        return {
            "status": "denied",
            "error": error,
            "tool_name": tool_name,
            "ai_employee_id": ai_employee_id,
            "reason": "role_restriction"
        }
    
    # STEP 2: Tool is allowed - execute it
    try:
        # Route to appropriate tool handler
        result = route_tool_call(ai_employee_id, tool_name, params, supabase_client)
        
        # Log successful execution
        log_tool_execution(
            organization_id, user_id, ai_employee_id, tool_name, 
            True, "Executed successfully", supabase_client
        )
        
        return {
            "status": "success",
            "tool_name": tool_name,
            "ai_employee_id": ai_employee_id,
            "result": result,
            "allowed": True
        }
    
    except Exception as e:
        # Log failed execution
        log_tool_execution(
            organization_id, user_id, ai_employee_id, tool_name,
            False, str(e), supabase_client
        )
        
        return {
            "status": "error",
            "tool_name": tool_name,
            "ai_employee_id": ai_employee_id,
            "error": str(e),
            "reason": "execution_error"
        }


def log_tool_execution(organization_id: str, user_id: str, ai_employee_id: str,
                      tool_name: str, success: bool, message: str,
                      supabase_client):
    """Log tool executions to database"""
    try:
        supabase_client.table('tool_executions').insert({
            'organization_id': organization_id,
            'user_id': user_id,
            'ai_employee_id': ai_employee_id,
            'tool_name': tool_name,
            'success': success,
            'message': message,
            'executed_at': datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        print(f"Error logging execution: {e}")


# ============================================================================
# EXAMPLE USAGE IN AGENT CHAT ENDPOINT
# ============================================================================

"""
# In your main.py or FastAPI endpoints:

from rbac import RoleBasedAccessControl, execute_tool_with_rbac_validation

rbac = RoleBasedAccessControl(supabase)

@app.post("/api/chat")
async def chat(user_id: str, organization_id: str, ai_employee_id: str, 
               question: str):
    
    # Get agent info with role validation
    agent_info = rbac.get_agent_info(ai_employee_id, organization_id)
    
    if not agent_info:
        return {"error": "Agent not found"}
    
    # Build agent prompt with allowed tools
    allowed_tools = agent_info.get('allowed_tools', [])
    role_info = agent_info.get('role', {})
    
    system_prompt = f'''You are {agent_info['name']}.
    Role: {role_info.get('role_name')}
    Job Description: {role_info.get('job_description')}
    
    You can ONLY use these tools: {', '.join(allowed_tools)}
    If user asks you to do something outside your role, politely decline.
    '''
    
    # ... rest of agent logic ...
    
    # When executing tool:
    result = execute_tool_with_rbac_validation(
        user_id, ai_employee_id, tool_name, params,
        organization_id, rbac, supabase
    )
    
    return result
"""

