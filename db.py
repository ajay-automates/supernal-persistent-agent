"""
Database module - 3-Tier Multi-Tenant Supabase interactions
Architecture: Organization → AI Employees → Users → Conversations
Shared docs live at org level; memory isolated by (org, ai_employee, user).
"""

from config import supabase
from datetime import datetime
from typing import List, Dict, Optional
import uuid as _uuid

ROLE_NAME_ALIASES = {
    "Sales Development Representative": "Sales Development Rep (SDR)",
    "SDR": "Sales Development Rep (SDR)",
    "Level 1 Customer Support": "Customer Support Agent",
    "Technical Support Engineer": "Customer Support Agent",
    "Account Manager": "Sales Development Rep (SDR)",
}


def _normalize_role_name(role_name: str) -> str:
    return ROLE_NAME_ALIASES.get(role_name, role_name)


# ============================================================
# ORGANIZATIONS
# ============================================================

def create_organization(name: str) -> Optional[Dict]:
    try:
        response = supabase.table("organizations").insert({
            "name": name,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating organization: {e}")
        return None


def get_organization(organization_id: str) -> Optional[Dict]:
    try:
        response = supabase.table("organizations").select("*").eq("id", organization_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting organization: {e}")
        return None


def get_organization_by_user(user_id: str) -> Optional[Dict]:
    """Look up the organization a user belongs to"""
    try:
        user_resp = supabase.table("users").select("organization_id").eq("user_id", user_id).execute()
        if not user_resp.data:
            return None
        org_id = user_resp.data[0]["organization_id"]
        return get_organization(org_id)
    except Exception as e:
        print(f"Error in get_organization_by_user: {e}")
        return None


def list_organizations() -> List[Dict]:
    try:
        response = supabase.table("organizations").select("*").order("created_at", desc=False).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error listing organizations: {e}")
        return []


# ============================================================
# AI EMPLOYEES
# ============================================================

def create_ai_employee(organization_id: str, name: str, role: str, job_description: str = "") -> Optional[Dict]:
    try:
        normalized_role = _normalize_role_name(role)
        role_id = get_role_id_by_name(normalized_role)
        response = supabase.table("ai_employees").insert({
            "organization_id": organization_id,
            "name": name,
            "role": normalized_role,
            "role_id": role_id,
            "job_description": job_description,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating AI employee: {e}")
        return None


def get_ai_employees(organization_id: str) -> List[Dict]:
    try:
        response = supabase.table("ai_employees")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=False)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting AI employees: {e}")
        return []


def get_ai_employee(ai_employee_id: str) -> Optional[Dict]:
    try:
        response = supabase.table("ai_employees").select("*").eq("id", ai_employee_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting AI employee: {e}")
        return None


def assign_ai_employee_to_user(user_id: str, ai_employee_id: str) -> bool:
    """Assign an AI employee to a user in both normalized and legacy stores."""
    try:
        user_resp = supabase.table("users").select(
            "organization_id, assigned_ai_employees"
        ).eq("user_id", user_id).execute()
        if not user_resp.data:
            return False
        organization_id = user_resp.data[0]["organization_id"]
        assigned = user_resp.data[0].get("assigned_ai_employees") or []
        if ai_employee_id not in assigned:
            assigned.append(ai_employee_id)
            supabase.table("users").update({"assigned_ai_employees": assigned}).eq("user_id", user_id).execute()
        try:
            supabase.table("user_ai_employee_assignments").insert({
                "organization_id": organization_id,
                "user_id": user_id,
                "ai_employee_id": ai_employee_id,
                "assigned_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"Error assigning AI employee: {e}")
        return False


def get_user_assigned_ai_employees(user_id: str) -> List[Dict]:
    """Return full AI employee records assigned to a user."""
    try:
        assignment_resp = supabase.table("user_ai_employee_assignments").select(
            "ai_employee_id"
        ).eq("user_id", user_id).execute()
        assignment_ids = [row["ai_employee_id"] for row in (assignment_resp.data or [])]

        user_resp = supabase.table("users").select("assigned_ai_employees").eq("user_id", user_id).execute()
        legacy_ids = []
        if user_resp.data:
            legacy_ids = user_resp.data[0].get("assigned_ai_employees") or []

        ids = list(dict.fromkeys(assignment_ids + legacy_ids))
        if not ids:
            return []

        response = supabase.table("ai_employees").select("*").in_("id", ids).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting assigned AI employees: {e}")
        return []


# ============================================================
# USERS
# ============================================================

def create_user(organization_id: str, user_id: str, name: str = "", email: str = "") -> Optional[Dict]:
    """Create a user within an organization"""
    try:
        # Return existing user if already present
        existing = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if existing.data:
            return existing.data[0]
        response = supabase.table("users").insert({
            "organization_id": organization_id,
            "user_id": user_id,
            "name": name,
            "email": email,
            "assigned_ai_employees": [],
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def get_user(user_id: str) -> Optional[Dict]:
    try:
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_org_users(organization_id: str) -> List[Dict]:
    try:
        response = supabase.table("users")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=False)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting org users: {e}")
        return []


def get_or_create_user(organization_id: str, user_id: str, name: str = "", email: str = "") -> Optional[Dict]:
    """Convenience: get existing user or create under specified org"""
    existing = get_user(user_id)
    if existing:
        return existing
    return create_user(organization_id, user_id, name, email)


def delete_user(user_id: str) -> bool:
    """Delete a user and their conversation history (cascades via FK)"""
    try:
        supabase.table("users").delete().eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False


# ============================================================
# RBAC
# ============================================================

def get_role_id_by_name(role_name: str) -> Optional[str]:
    """Get role UUID by canonical role name."""
    try:
        normalized_role = _normalize_role_name(role_name)
        result = supabase.table("ai_employee_roles").select("id").eq(
            "role_name", normalized_role
        ).execute()
        return result.data[0]["id"] if result.data else None
    except Exception as e:
        print(f"Error getting role ID: {e}")
        return None


def get_ai_employee_by_id(ai_employee_id: str, organization_id: str) -> Optional[Dict]:
    """Get AI employee by ID within an organization."""
    try:
        result = supabase.table("ai_employees").select("*").eq(
            "id", ai_employee_id
        ).eq("organization_id", organization_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting AI employee by ID: {e}")
        return None


def get_allowed_tools_for_role(role_id: str) -> List[str]:
    """Return allowed tool names for a role."""
    try:
        result = supabase.table("role_tool_permissions").select("tool_name").eq(
            "role_id", role_id
        ).eq("allowed", True).execute()
        return [item["tool_name"] for item in (result.data or [])]
    except Exception as e:
        print(f"Error getting allowed tools for role: {e}")
        return []


def get_role_permissions(role_id: str) -> List[Dict]:
    """Return all permission rows for a role."""
    try:
        result = supabase.table("role_tool_permissions").select(
            "tool_name, allowed, reason"
        ).eq("role_id", role_id).order("tool_name").execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting role permissions: {e}")
        return []


def log_access_attempt(
    organization_id: str,
    user_id: str,
    ai_employee_id: str,
    tool_name: str,
    allowed: bool,
    reason: str = None,
) -> bool:
    """Log a tool access allow/deny decision."""
    try:
        supabase.table("tool_access_attempts").insert({
            "organization_id": organization_id,
            "user_id": user_id,
            "ai_employee_id": ai_employee_id,
            "tool_name": tool_name,
            "allowed": allowed,
            "reason": reason,
            "attempted_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Error logging access attempt: {e}")
        return False


def check_user_access_to_agent(user_id: str, ai_employee_id: str, organization_id: str) -> bool:
    """Check whether a user is assigned to an AI employee."""
    try:
        result = supabase.table("user_ai_employee_assignments").select("id").eq(
            "organization_id", organization_id
        ).eq("user_id", user_id).eq("ai_employee_id", ai_employee_id).execute()
        if result.data:
            return True

        user_resp = supabase.table("users").select("assigned_ai_employees").eq(
            "user_id", user_id
        ).eq("organization_id", organization_id).execute()
        if not user_resp.data:
            return False
        assigned = user_resp.data[0].get("assigned_ai_employees") or []
        return ai_employee_id in assigned
    except Exception as e:
        print(f"Error checking user access to agent: {e}")
        return False


def check_tool_permission(role_id: str, tool_name: str) -> bool:
    """Check if a role is allowed to use a tool."""
    try:
        result = supabase.table("role_tool_permissions").select("allowed").eq(
            "role_id", role_id
        ).eq("tool_name", tool_name).execute()
        return bool(result.data and result.data[0]["allowed"])
    except Exception as e:
        print(f"Error checking tool permission: {e}")
        return False


def get_user_agent_assignments(organization_id: str, user_id: str) -> List[Dict]:
    """Get normalized assignment rows for a user."""
    try:
        result = supabase.table("user_ai_employee_assignments").select(
            "id, ai_employee_id, assigned_at"
        ).eq("organization_id", organization_id).eq("user_id", user_id).order(
            "assigned_at", desc=False
        ).execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting user agent assignments: {e}")
        return []


def get_access_attempts(
    organization_id: str,
    user_id: Optional[str] = None,
    ai_employee_id: Optional[str] = None,
    limit: int = 100,
) -> List[Dict]:
    """Get recent RBAC access attempts."""
    try:
        query = supabase.table("tool_access_attempts").select("*").eq(
            "organization_id", organization_id
        )
        if user_id:
            query = query.eq("user_id", user_id)
        if ai_employee_id:
            query = query.eq("ai_employee_id", ai_employee_id)
        result = query.order("attempted_at", desc=True).limit(limit).execute()
        return result.data or []
    except Exception as e:
        print(f"Error getting access attempts: {e}")
        return []


# ============================================================
# CONVERSATIONS  (triple-keyed: org + ai_employee + user)
# ============================================================

def save_message(organization_id: str, ai_employee_id: str, user_id: str, role: str, content: str) -> Optional[str]:
    """Save a conversation message and return its UUID (or None on error)."""
    try:
        response = supabase.table("conversations").insert({
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error saving message: {e}")
        return None


def get_user_ai_employee_memory(
    organization_id: str, ai_employee_id: str, user_id: str, limit: int = 20
) -> List[Dict]:
    """Retrieve conversation history for a specific (user, AI employee) pair within an org"""
    try:
        response = supabase.table("conversations")\
            .select("role, content, timestamp")\
            .eq("organization_id", organization_id)\
            .eq("ai_employee_id", ai_employee_id)\
            .eq("user_id", user_id)\
            .order("timestamp", desc=False)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error retrieving memory: {e}")
        return []


def clear_user_ai_employee_memory(organization_id: str, ai_employee_id: str, user_id: str) -> bool:
    try:
        supabase.table("conversations")\
            .delete()\
            .eq("organization_id", organization_id)\
            .eq("ai_employee_id", ai_employee_id)\
            .eq("user_id", user_id)\
            .execute()
        return True
    except Exception as e:
        print(f"Error clearing memory: {e}")
        return False


# ============================================================
# ORGANIZATION DOCUMENTS & CHUNKS (shared across org)
# ============================================================

def save_organization_document(organization_id: str, filename: str, source: str = "") -> Optional[str]:
    try:
        response = supabase.table("organization_documents").insert({
            "organization_id": organization_id,
            "filename": filename,
            "source": source or filename,
            "uploaded_at": datetime.utcnow().isoformat()
        }).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error saving org document: {e}")
        return None


def get_organization_documents(organization_id: str) -> List[Dict]:
    try:
        response = supabase.table("organization_documents")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("uploaded_at", desc=True)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting org documents: {e}")
        return []


def save_organization_chunk(organization_id: str, text: str, embedding: List[float], source: str) -> bool:
    try:
        supabase.table("organization_chunks").insert({
            "organization_id": organization_id,
            "text": text,
            "embedding": embedding,
            "source": source,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Error saving org chunk: {e}")
        return False


def search_organization_chunks(organization_id: str, query_embedding: List[float], k: int = 4) -> List[Dict]:
    """Vector similarity search over org-level shared documents"""
    try:
        response = supabase.rpc(
            "search_organization_chunks",
            {
                "p_organization_id": organization_id,
                "p_query_embedding": query_embedding,
                "p_match_count": k
            }
        ).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error searching org chunks: {e}")
        return []


def get_organization_chunks(organization_id: str, limit: int = 10) -> List[Dict]:
    try:
        response = supabase.table("organization_chunks")\
            .select("id, text, source, created_at")\
            .eq("organization_id", organization_id)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting org chunks: {e}")
        return []


def clear_organization_documents(organization_id: str) -> bool:
    try:
        supabase.table("organization_chunks").delete().eq("organization_id", organization_id).execute()
        supabase.table("organization_documents").delete().eq("organization_id", organization_id).execute()
        return True
    except Exception as e:
        print(f"Error clearing org documents: {e}")
        return False


# ============================================================
# STATISTICS
# ============================================================

def get_stats(organization_id: str, ai_employee_id: str, user_id: str) -> Dict:
    try:
        conv_resp = supabase.table("conversations")\
            .select("id", count="exact")\
            .eq("organization_id", organization_id)\
            .eq("ai_employee_id", ai_employee_id)\
            .eq("user_id", user_id)\
            .execute()

        doc_resp = supabase.table("organization_documents")\
            .select("id", count="exact")\
            .eq("organization_id", organization_id)\
            .execute()

        chunk_resp = supabase.table("organization_chunks")\
            .select("id", count="exact")\
            .eq("organization_id", organization_id)\
            .execute()

        total_msgs = conv_resp.count or 0
        return {
            "conversation_turns": total_msgs // 2,
            "total_messages": total_msgs,
            "org_documents": doc_resp.count or 0,
            "org_chunks": chunk_resp.count or 0
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {"conversation_turns": 0, "total_messages": 0, "org_documents": 0, "org_chunks": 0}


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_hierarchy(organization_id: str, ai_employee_id: str, user_id: str) -> Optional[str]:
    """
    Returns an error message if the three IDs don't form a valid hierarchy,
    or None if everything is valid.
    """
    try:
        # Check org exists
        org = get_organization(organization_id)
        if not org:
            return f"Organization '{organization_id}' not found"

        # Check ai_employee belongs to org
        emp_resp = supabase.table("ai_employees")\
            .select("id")\
            .eq("id", ai_employee_id)\
            .eq("organization_id", organization_id)\
            .execute()
        if not emp_resp.data:
            return f"AI employee '{ai_employee_id}' not found in organization '{organization_id}'"

        # Check user belongs to org
        user_resp = supabase.table("users")\
            .select("id")\
            .eq("user_id", user_id)\
            .eq("organization_id", organization_id)\
            .execute()
        if not user_resp.data:
            return f"User '{user_id}' not found in organization '{organization_id}'"

        return None
    except Exception as e:
        return f"Validation error: {e}"


# ─── Tool Registry ────────────────────────────────────────────────────────────

def register_tool(
    organization_id: str,
    name: str,
    description: str,
    schema: dict,
    endpoint: str
) -> Optional[Dict]:
    """Register a new tool for an organization."""
    try:
        resp = supabase.table("tools").insert({
            "organization_id": organization_id,
            "name": name,
            "description": description,
            "schema": schema,
            "endpoint": endpoint,
        }).execute()
        return resp.data[0] if resp.data else None
    except Exception as e:
        print(f"Error registering tool: {e}")
        return None


def get_organization_tools(organization_id: str) -> List[Dict]:
    """Get all tools available to an organization."""
    try:
        resp = supabase.table("tools")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("created_at")\
            .execute()
        return resp.data or []
    except Exception as e:
        print(f"Error fetching tools: {e}")
        return []


def log_tool_execution(
    organization_id: str,
    ai_employee_id: str,
    user_id: str,
    tool_name: str,
    input_params: dict,
    output_result: dict,
    status: str,
    error_message: str = None,
    latency_ms: int = None
) -> bool:
    """Log a tool execution to the tool_executions table."""
    try:
        supabase.table("tool_executions").insert({
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "user_id": user_id,
            "tool_name": tool_name,
            "input_params": input_params,
            "output_result": output_result,
            "status": status,
            "error_message": error_message,
            "latency_ms": latency_ms,
        }).execute()
        return True
    except Exception as e:
        print(f"Error logging tool execution: {e}")
        return False


def get_tool_execution_history(
    organization_id: str,
    ai_employee_id: str,
    user_id: str
) -> List[Dict]:
    """Get tool execution history for a user + agent pair."""
    try:
        resp = supabase.table("tool_executions")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .eq("ai_employee_id", ai_employee_id)\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        return resp.data or []
    except Exception as e:
        print(f"Error fetching tool execution history: {e}")
        return []


# ─── Semantic Memory ───────────────────────────────────────────────────────────

def store_conversation_embedding(
    organization_id: str,
    ai_employee_id: str,
    user_id: str,
    embedding: List[float],
    summary: str,
    topics: List[str],
    conversation_id: str = None
) -> bool:
    """Store an embedded conversation turn for semantic memory retrieval."""
    try:
        row = {
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "user_id": user_id,
            "embedding": embedding,
            "summary": summary,
            "topics": topics,
        }
        if conversation_id:
            row["conversation_id"] = conversation_id
        supabase.table("conversation_embeddings").insert(row).execute()
        return True
    except Exception as e:
        print(f"Error storing conversation embedding: {e}")
        return False


def search_semantic_memory(
    organization_id: str,
    ai_employee_id: str,
    user_id: str,
    query_embedding: List[float],
    k: int = 5
) -> List[Dict]:
    """Semantic similarity search over the user's conversation history."""
    try:
        response = supabase.rpc(
            "search_memory",
            {
                "p_organization_id": organization_id,
                "p_ai_employee_id": ai_employee_id,
                "p_user_id": user_id,
                "p_query_embedding": query_embedding,
                "p_match_count": k,
            }
        ).execute()
        return response.data or []
    except Exception as e:
        print(f"Error searching semantic memory: {e}")
        return []


# ─── Job Queue ────────────────────────────────────────────────────────────────

def create_job(task_type: str, payload: dict, organization_id: str = None) -> str:
    """Insert a pending job record and return its UUID."""
    try:
        row = {"task_type": task_type, "payload": payload, "status": "pending"}
        if organization_id:
            row["organization_id"] = organization_id
        resp = supabase.table("jobs").insert(row).execute()
        return resp.data[0]["id"] if resp.data else str(_uuid.uuid4())
    except Exception as e:
        print(f"Error creating job: {e}")
        return str(_uuid.uuid4())


def update_job_status(
    job_id: str,
    status: str,
    result: dict = None,
    error: str = None
) -> bool:
    """Update a job's status (and optionally result/error) in-place."""
    try:
        update: Dict = {"status": status}
        if status == "running":
            update["started_at"] = datetime.utcnow().isoformat()
        if status in ("done", "failed"):
            update["completed_at"] = datetime.utcnow().isoformat()
        if result is not None:
            update["result"] = result
        if error is not None:
            update["error_message"] = error
        supabase.table("jobs").update(update).eq("id", job_id).execute()
        return True
    except Exception as e:
        print(f"Error updating job {job_id}: {e}")
        return False


def get_job(job_id: str) -> Optional[Dict]:
    """Fetch a single job record by ID."""
    try:
        resp = supabase.table("jobs").select("*").eq("id", job_id).execute()
        return resp.data[0] if resp.data else None
    except Exception as e:
        print(f"Error getting job: {e}")
        return None


def list_jobs(organization_id: str = None, limit: int = 50) -> List[Dict]:
    """List recent jobs, optionally filtered by org."""
    try:
        q = supabase.table("jobs").select("*").order("created_at", desc=True).limit(limit)
        if organization_id:
            q = q.eq("organization_id", organization_id)
        return q.execute().data or []
    except Exception as e:
        print(f"Error listing jobs: {e}")
        return []


# ─── Observability ─────────────────────────────────────────────────────────────

def log_api_call(
    endpoint: str,
    method: str,
    status_code: int,
    latency_ms: int,
    organization_id: str = None,
) -> None:
    """Log an HTTP request to api_logs. Fire-and-forget; never raises."""
    try:
        row = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "created_at": datetime.utcnow().isoformat(),
        }
        if organization_id:
            row["organization_id"] = organization_id
        supabase.table("api_logs").insert(row).execute()
    except Exception:
        pass


def log_llm_call(
    organization_id: str,
    ai_employee_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    latency_ms: int,
    cost_usd: float,
) -> None:
    """Log an LLM completion call to llm_metrics. Fire-and-forget; never raises."""
    try:
        supabase.table("llm_metrics").insert({
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass


def log_error(
    error_message: str,
    error_type: str = "general",
    stack_trace: str = None,
    organization_id: str = None,
) -> None:
    """Log an error to error_logs. Fire-and-forget; never raises."""
    try:
        row = {
            "error_type": error_type,
            "error_message": str(error_message),
            "created_at": datetime.utcnow().isoformat(),
        }
        if stack_trace:
            row["stack_trace"] = stack_trace
        if organization_id:
            row["organization_id"] = organization_id
        supabase.table("error_logs").insert(row).execute()
    except Exception:
        pass


def get_org_metrics(organization_id: str) -> Dict:
    """Return aggregate observability metrics for an organization."""
    try:
        api_data = (
            supabase.table("api_logs")
            .select("latency_ms,status_code")
            .order("created_at", desc=True)
            .limit(500)
            .execute()
            .data or []
        )
        llm_data = (
            supabase.table("llm_metrics")
            .select("total_tokens,cost_usd,latency_ms,model")
            .eq("organization_id", organization_id)
            .order("created_at", desc=True)
            .limit(500)
            .execute()
            .data or []
        )
        error_data = (
            supabase.table("error_logs")
            .select("error_type,error_message,created_at")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
            .data or []
        )

        total_requests = len(api_data)
        avg_latency = (
            sum(r["latency_ms"] or 0 for r in api_data) / total_requests
            if total_requests else 0
        )
        total_tokens = sum(r["total_tokens"] or 0 for r in llm_data)
        total_cost = sum(float(r["cost_usd"] or 0) for r in llm_data)
        error_count = len(error_data)

        return {
            "organization_id": organization_id,
            "total_requests": total_requests,
            "avg_latency_ms": round(avg_latency, 2),
            "total_llm_calls": len(llm_data),
            "total_tokens_used": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "error_count": error_count,
            "recent_errors": error_data[:10],
        }
    except Exception as e:
        print(f"Error getting org metrics: {e}")
        return {}


# ─── Tool Verification / Logging ───────────────────────────────────────────────

def log_email_sent(
    organization_id: str,
    ai_employee_id: str,
    recipient: str,
    subject: str,
    body: str,
    email_id: str,
    status: str = "sent"
) -> bool:
    """Log an email sent via tools."""
    try:
        from datetime import datetime
        import traceback
        supabase.table("emails_sent").insert({
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "to_email": recipient,
            "subject": subject,
            "body": body,
            "sent_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"ERROR logging email: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def log_crm_lead(
    organization_id: str,
    ai_employee_id: str,
    lead_id: str,
    company: str,
    contact_name: str,
    email: str,
    phone: str = "",
    stage: str = "New Lead"
) -> bool:
    """Log a CRM lead added via tools."""
    try:
        from datetime import datetime
        supabase.table("crm_leads").insert({
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "company_name": company,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "status": stage,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Error logging CRM lead: {e}")
        return False


def log_support_ticket(
    organization_id: str,
    ai_employee_id: str,
    ticket_id: str,
    customer_email: str,
    issue_type: str,
    description: str,
    priority: str = "medium",
    status: str = "open"
) -> bool:
    """Log a support ticket created via tools."""
    try:
        from datetime import datetime
        supabase.table("support_tickets").insert({
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "ticket_id": ticket_id,
            "customer_email": customer_email,
            "subject": issue_type,
            "description": description,
            "priority": priority,
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Error logging support ticket: {e}")
        return False


def log_calendar_event(
    organization_id: str,
    ai_employee_id: str,
    event_id: str,
    attendee_email: str,
    title: str,
    date_time: str,
    duration_minutes: int = 30,
    zoom_link: str = ""
) -> bool:
    """Log a calendar event scheduled via tools."""
    try:
        from datetime import datetime
        supabase.table("calendar_events").insert({
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "title": title,
            "attendee_email": attendee_email,
            "start_time": date_time,
            "end_time": date_time,  # simplified for now
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Error logging calendar event: {e}")
        return False


def log_equipment_order(
    organization_id: str,
    ai_employee_id: str,
    order_id: str,
    equipment: str,
    quantity: int,
    unit_price: float,
    total_cost: float,
    employee_name: str,
    estimated_delivery: str = None,
    status: str = "ordered"
) -> bool:
    """Log an equipment order placed via tools."""
    try:
        from datetime import datetime
        import traceback
        row = {
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "item_name": equipment,
            "quantity": int(quantity),
            "cost_usd": float(unit_price),
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
        }
        if estimated_delivery:
            row["delivery_date"] = estimated_delivery
        print(f"DEBUG: Inserting equipment order: {row}")
        supabase.table("equipment_orders").insert(row).execute()
        return True
    except Exception as e:
        print(f"ERROR logging equipment order: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def get_emails_sent(organization_id: str) -> List[Dict]:
    """Get all emails sent via tools for an organization."""
    try:
        resp = supabase.table("emails_sent")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("sent_at", desc=True)\
            .execute()
        return resp.data or []
    except Exception as e:
        print(f"Error getting emails: {e}")
        return []


def get_crm_leads(organization_id: str) -> List[Dict]:
    """Get all CRM leads added via tools for an organization."""
    try:
        resp = supabase.table("crm_leads")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .execute()
        return resp.data or []
    except Exception as e:
        print(f"Error getting CRM leads: {e}")
        return []


def get_support_tickets(organization_id: str) -> List[Dict]:
    """Get all support tickets created via tools for an organization."""
    try:
        resp = supabase.table("support_tickets")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .execute()
        return resp.data or []
    except Exception as e:
        print(f"Error getting support tickets: {e}")
        return []


def get_calendar_events(organization_id: str) -> List[Dict]:
    """Get all calendar events scheduled via tools for an organization."""
    try:
        resp = supabase.table("calendar_events")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .execute()
        return resp.data or []
    except Exception as e:
        print(f"Error getting calendar events: {e}")
        return []


def get_equipment_orders(organization_id: str) -> List[Dict]:
    """Get all equipment orders placed via tools for an organization."""
    try:
        resp = supabase.table("equipment_orders")\
            .select("*")\
            .eq("organization_id", organization_id)\
            .order("created_at", desc=True)\
            .execute()
        return resp.data or []
    except Exception as e:
        print(f"Error getting equipment orders: {e}")
        return []
