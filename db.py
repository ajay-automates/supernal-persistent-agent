"""
Database module - 3-Tier Multi-Tenant Supabase interactions
Architecture: Organization → AI Employees → Users → Conversations
Shared docs live at org level; memory isolated by (org, ai_employee, user).
"""

from config import supabase
from datetime import datetime
from typing import List, Dict, Optional


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
        response = supabase.table("ai_employees").insert({
            "organization_id": organization_id,
            "name": name,
            "role": role,
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
    """Add an ai_employee_id to the user's assigned_ai_employees JSONB array"""
    try:
        user_resp = supabase.table("users").select("assigned_ai_employees").eq("user_id", user_id).execute()
        if not user_resp.data:
            return False
        assigned = user_resp.data[0].get("assigned_ai_employees") or []
        if ai_employee_id not in assigned:
            assigned.append(ai_employee_id)
            supabase.table("users").update({"assigned_ai_employees": assigned}).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error assigning AI employee: {e}")
        return False


def get_user_assigned_ai_employees(user_id: str) -> List[Dict]:
    """Return full AI employee records assigned to a user"""
    try:
        user_resp = supabase.table("users").select("assigned_ai_employees").eq("user_id", user_id).execute()
        if not user_resp.data:
            return []
        ids = user_resp.data[0].get("assigned_ai_employees") or []
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


# ============================================================
# CONVERSATIONS  (triple-keyed: org + ai_employee + user)
# ============================================================

def save_message(organization_id: str, ai_employee_id: str, user_id: str, role: str, content: str) -> bool:
    try:
        supabase.table("conversations").insert({
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False


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
