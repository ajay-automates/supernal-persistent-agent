"""
Database module - Handles all Supabase interactions
Manages: users, conversations, documents, chunks, embeddings
"""

from config import supabase
from datetime import datetime
from typing import List, Dict, Optional

# ============================================================
# USER MANAGEMENT
# ============================================================

def get_or_create_user(user_id: str) -> Dict:
    """Get or create a user in the database"""
    try:
        # Try to get existing user
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        # Create new user
        response = supabase.table("users").insert({
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error in get_or_create_user: {e}")
        return None


# ============================================================
# CONVERSATION MANAGEMENT
# ============================================================

def save_message(user_id: str, role: str, content: str) -> bool:
    """Store a single message in the conversation history"""
    try:
        supabase.table("conversations").insert({
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False


def get_user_memory(user_id: str, limit: int = 20) -> List[Dict]:
    """Retrieve user's conversation history (most recent first)"""
    try:
        response = supabase.table("conversations")\
            .select("role, content, timestamp")\
            .eq("user_id", user_id)\
            .order("timestamp", desc=False)\
            .limit(limit)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error retrieving user memory: {e}")
        return []


def clear_user_memory(user_id: str) -> bool:
    """Clear all conversations for a user"""
    try:
        supabase.table("conversations").delete().eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error clearing user memory: {e}")
        return False


# ============================================================
# DOCUMENT & CHUNK MANAGEMENT
# ============================================================

def save_document(user_id: str, filename: str, source: str) -> Optional[str]:
    """Save a document metadata"""
    try:
        response = supabase.table("documents").insert({
            "user_id": user_id,
            "filename": filename,
            "source": source,
            "uploaded_at": datetime.utcnow().isoformat()
        }).execute()
        
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error saving document: {e}")
        return None


def save_chunk(user_id: str, text: str, embedding: List[float], source: str) -> bool:
    """Save a text chunk with its embedding"""
    try:
        supabase.table("chunks").insert({
            "user_id": user_id,
            "text": text,
            "embedding": embedding,  # pgvector will handle this
            "source": source,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Error saving chunk: {e}")
        return False


def search_user_chunks(user_id: str, query_embedding: List[float], k: int = 4) -> List[Dict]:
    """Search user's document chunks using vector similarity"""
    try:
        # Call the Supabase RPC function for vector search
        response = supabase.rpc(
            "search_chunks",
            {
                "p_user_id": user_id,
                "p_query_embedding": query_embedding,
                "p_match_count": k
            }
        ).execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error searching chunks: {e}")
        # Fallback: return empty list instead of failing
        return []


def get_user_documents(user_id: str) -> List[Dict]:
    """Get all documents uploaded by a user"""
    try:
        response = supabase.table("documents")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("uploaded_at", desc=True)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting user documents: {e}")
        return []


def clear_user_documents(user_id: str) -> bool:
    """Clear all documents and chunks for a user"""
    try:
        # Delete all chunks for this user
        supabase.table("chunks").delete().eq("user_id", user_id).execute()
        # Delete all documents for this user
        supabase.table("documents").delete().eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"Error clearing user documents: {e}")
        return False


# ============================================================
# STATISTICS
# ============================================================

def get_user_stats(user_id: str) -> Dict:
    """Get statistics for a user"""
    try:
        # Count conversations
        conv_response = supabase.table("conversations")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        
        # Count documents
        doc_response = supabase.table("documents")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        
        # Count chunks
        chunk_response = supabase.table("chunks")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()
        
        return {
            "conversation_turns": (conv_response.count or 0) // 2,  # Pairs of user/assistant
            "total_messages": conv_response.count or 0,
            "documents": doc_response.count or 0,
            "chunks": chunk_response.count or 0
        }
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {
            "conversation_turns": 0,
            "total_messages": 0,
            "documents": 0,
            "chunks": 0
        }
