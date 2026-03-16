"""
RBAC helpers for AI employees.

This layer enforces two things before a tool can run:
1. the user is assigned to the AI employee
2. the AI employee's role is allowed to use the tool
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

# Optional LangSmith tracing
LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY")
if LANGSMITH_API_KEY:
    from langsmith import traceable
else:
    def traceable(name=None, run_type=None):
        def decorator(func):
            return func
        return decorator


class RoleBasedAccessControl:
    """Validate user-to-agent access and role-to-tool permissions."""

    def __init__(self, supabase_client):
        self.db = supabase_client

    def get_ai_employee_role(self, ai_employee_id: str, organization_id: str) -> Optional[Dict]:
        """Fetch the RBAC role for an AI employee."""
        try:
            employee_result = self.db.table("ai_employees").select(
                "id, name, role_id, role, job_description"
            ).eq("id", ai_employee_id).eq("organization_id", organization_id).execute()
            if not employee_result.data:
                return None

            employee = employee_result.data[0]
            if not employee.get("role_id"):
                return None

            role_result = self.db.table("ai_employee_roles").select(
                "id, role_name, role_category, description, job_description, icon, example_task"
            ).eq("id", employee["role_id"]).execute()
            return role_result.data[0] if role_result.data else None
        except Exception as e:
            print(f"Error getting AI employee role: {e}")
            return None

    def is_tool_allowed_for_role(self, role_id: str, tool_name: str) -> Tuple[bool, Optional[str]]:
        """Check whether a tool is allowed for a role."""
        try:
            result = self.db.table("role_tool_permissions").select(
                "allowed, reason"
            ).eq("role_id", role_id).eq("tool_name", tool_name).execute()
            if not result.data:
                return False, "Tool not found in role permissions"

            row = result.data[0]
            if row["allowed"]:
                return True, None
            return False, row["reason"]
        except Exception as e:
            print(f"Error checking tool permission: {e}")
            return False, "Error checking role permissions"

    def get_allowed_tools_for_role(self, role_id: str) -> List[str]:
        """Get all tool names a role can use."""
        try:
            result = self.db.table("role_tool_permissions").select(
                "tool_name"
            ).eq("role_id", role_id).eq("allowed", True).order("tool_name").execute()
            return [row["tool_name"] for row in (result.data or [])]
        except Exception as e:
            print(f"Error getting allowed tools for role: {e}")
            return []

    def get_allowed_tool_details_for_role(self, role_id: str) -> List[Dict]:
        """Get allowed tool names with descriptions for prompting and APIs."""
        try:
            permissions = self.db.table("role_tool_permissions").select(
                "tool_name"
            ).eq("role_id", role_id).eq("allowed", True).execute()
            tool_names = [row["tool_name"] for row in (permissions.data or [])]
            if not tool_names:
                return []

            tools = self.db.table("rbac_tools").select(
                "tool_name, description, category"
            ).in_("tool_name", tool_names).order("tool_name").execute()
            return tools.data or []
        except Exception as e:
            print(f"Error getting allowed tool details: {e}")
            return []

    @traceable(name="can_user_access_ai_employee", run_type="chain")
    def can_user_access_ai_employee(
        self, user_id: str, ai_employee_id: str, organization_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Check whether the user is assigned to this AI employee."""
        try:
            assignment = self.db.table("user_ai_employee_assignments").select(
                "id"
            ).eq("user_id", user_id).eq(
                "ai_employee_id", ai_employee_id
            ).execute()
            if assignment.data:
                return True, None

            user_result = self.db.table("users").select(
                "assigned_ai_employees"
            ).eq("organization_id", organization_id).eq("user_id", user_id).execute()
            assigned = []
            if user_result.data:
                assigned = user_result.data[0].get("assigned_ai_employees") or []
            if ai_employee_id in assigned:
                return True, None

            assigned_agents = self.get_user_assigned_agents(user_id, organization_id)
            assigned_ids = [agent["id"] for agent in assigned_agents]
            return False, f"You don't have access to this AI employee. Assigned agents: {assigned_ids}"
        except Exception as e:
            print(f"Error checking user access: {e}")
            return False, "Error checking access permissions"

    def log_access_attempt(
        self,
        organization_id: str,
        user_id: str,
        ai_employee_id: str,
        tool_name: str,
        allowed: bool,
        reason: Optional[str] = None,
    ) -> None:
        """Persist allow/deny decisions for auditability."""
        try:
            self.db.table("tool_access_attempts").insert({
                "organization_id": organization_id,
                "user_id": user_id,
                "ai_employee_id": ai_employee_id,
                "tool_name": tool_name,
                "allowed": allowed,
                "reason": reason,
                "attempted_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            print(f"Error logging access attempt: {e}")

    @traceable(name="validate_tool_execution", run_type="chain")
    def validate_tool_execution(
        self, user_id: str, ai_employee_id: str, tool_name: str, organization_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Run the full RBAC chain for a tool execution."""
        user_allowed, user_error = self.can_user_access_ai_employee(
            user_id, ai_employee_id, organization_id
        )
        if not user_allowed:
            self.log_access_attempt(
                organization_id, user_id, ai_employee_id, tool_name, False, user_error
            )
            return False, user_error

        role = self.get_ai_employee_role(ai_employee_id, organization_id)
        if not role:
            error = "AI employee has no RBAC role assigned"
            self.log_access_attempt(
                organization_id, user_id, ai_employee_id, tool_name, False, error
            )
            return False, error

        allowed, deny_reason = self.is_tool_allowed_for_role(role["id"], tool_name)
        if not allowed:
            allowed_tools = self.get_allowed_tools_for_role(role["id"])
            error = (
                f"Role '{role['role_name']}' cannot use '{tool_name}'. "
                f"Allowed tools: {', '.join(allowed_tools)}"
            )
            if deny_reason:
                error = f"{error}. Reason: {deny_reason}"
            self.log_access_attempt(
                organization_id, user_id, ai_employee_id, tool_name, False, error
            )
            return False, error

        self.log_access_attempt(
            organization_id, user_id, ai_employee_id, tool_name, True, "Tool execution allowed"
        )
        return True, None

    @traceable(name="get_agent_info", run_type="chain")
    def get_agent_info(self, ai_employee_id: str, organization_id: str) -> Optional[Dict]:
        """Return AI employee info enriched with RBAC role metadata."""
        try:
            agent_result = self.db.table("ai_employees").select("*").eq(
                "id", ai_employee_id
            ).eq("organization_id", organization_id).execute()
            if not agent_result.data:
                return None

            agent = agent_result.data[0]
            role = self.get_ai_employee_role(ai_employee_id, organization_id)
            if role:
                agent["role_details"] = role
                agent["allowed_tools"] = self.get_allowed_tools_for_role(role["id"])
                agent["allowed_tool_details"] = self.get_allowed_tool_details_for_role(role["id"])
            else:
                agent["role_details"] = None
                agent["allowed_tools"] = []
                agent["allowed_tool_details"] = []
            return agent
        except Exception as e:
            print(f"Error getting agent info: {e}")
            return None

    def get_user_assigned_agents(self, user_id: str, organization_id: str) -> List[Dict]:
        """Return all agents a user can access."""
        try:
            assignments = self.db.table("user_ai_employee_assignments").select(
                "ai_employee_id"
            ).eq("user_id", user_id).execute()
            agent_ids = [row["ai_employee_id"] for row in (assignments.data or [])]

            if not agent_ids:
                legacy_user = self.db.table("users").select(
                    "assigned_ai_employees"
                ).eq("organization_id", organization_id).eq("user_id", user_id).execute()
                if legacy_user.data:
                    agent_ids = legacy_user.data[0].get("assigned_ai_employees") or []

            if not agent_ids:
                return []

            agents: List[Dict] = []
            for agent_id in agent_ids:
                agent_info = self.get_agent_info(agent_id, organization_id)
                if agent_info:
                    agents.append(agent_info)
            return agents
        except Exception as e:
            print(f"Error getting user assigned agents: {e}")
            return []
