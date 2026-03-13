"""
Agent module - 3-Tier RAG orchestrator
Pipeline: retrieve org docs → load user+agent memory → generate → save
"""

from config import OPENAI_API_KEY, LANGSMITH_API_KEY
from db import (
    get_or_create_user, save_message,
    get_user_ai_employee_memory, search_organization_chunks,
    get_organization, get_ai_employee
)
from openai import OpenAI
from typing import List, Dict, Tuple
import os

client = OpenAI(api_key=OPENAI_API_KEY)

# Optional LangSmith tracing
if LANGSMITH_API_KEY:
    from langsmith import traceable
else:
    def traceable(name=None, run_type=None):
        def decorator(func):
            return func
        return decorator


# ============================================================
# RETRIEVAL
# ============================================================

@traceable(name="retrieve_context", run_type="retriever")
def retrieve_context(
    organization_id: str, query: str, k: int = 4
) -> Tuple[str, List[str]]:
    """
    Retrieve relevant context from the organization's shared documents.
    Returns (context_string, sources_list).
    """
    try:
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = embedding_response.data[0].embedding

        results = search_organization_chunks(organization_id, query_embedding, k=k)

        if not results:
            return "No relevant documents found in the organization knowledge base.", []

        context_parts = []
        sources = []
        for result in results:
            src = result.get("source", "Unknown")
            context_parts.append(f"[Source: {src}]\n{result.get('text', '')}")
            if src not in sources:
                sources.append(src)

        return "\n\n---\n\n".join(context_parts), sources

    except Exception as e:
        print(f"Error in retrieve_context: {e}")
        return f"Error retrieving context: {str(e)}", []


# ============================================================
# GENERATION
# ============================================================

@traceable(name="generate_answer", run_type="chain")
def generate_answer(
    org_name: str,
    ai_employee_name: str,
    ai_employee_role: str,
    job_description: str,
    user_name: str,
    query: str,
    context: str,
    sources: List[str],
    memory: List[Dict]
) -> str:
    """
    Generate answer using:
    - Organization context (name, shared docs)
    - AI employee persona (name, role, job description)
    - User's past conversations with this specific agent
    """
    try:
        system_prompt = f"""You are {ai_employee_name}, an AI employee at {org_name}.
Your role: {ai_employee_role}
Your responsibilities: {job_description or 'Help users with their questions.'}

When answering:
1. Stay in character as {ai_employee_name} — a knowledgeable {ai_employee_role} at {org_name}
2. Use the provided organization documents as your primary knowledge source
3. Reference the user's past conversations with you when relevant
4. Be concise, helpful, and professional
5. Address the user{f" ({user_name})" if user_name else ""} directly
6. If you don't know something from the provided context, say so clearly"""

        messages = [{"role": "system", "content": system_prompt}]

        # Last 12 messages (6 turns) from this user's history with this agent
        for msg in memory[-12:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        context_prompt = f"""Organization Knowledge Base:
---
{context}
---

Sources: {', '.join(sources) if sources else 'None'}

Question: {query}"""

        messages.append({"role": "user", "content": context_prompt})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=800,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error in generate_answer: {e}")
        return f"Error generating answer: {str(e)}"


# ============================================================
# MAIN AGENT PIPELINE
# ============================================================

@traceable(name="agent_pipeline", run_type="chain")
def answer_question(
    organization_id: str,
    ai_employee_id: str,
    user_id: str,
    question: str
) -> Dict:
    """
    3-tier agent pipeline:
    1. Ensure user exists in the org
    2. Fetch org / AI employee metadata for persona
    3. Retrieve relevant org-level documents
    4. Load user's past conversations with THIS agent
    5. Generate answer with full context
    6. Persist to conversations table
    """
    result = {
        "organization_id": organization_id,
        "ai_employee_id": ai_employee_id,
        "user_id": user_id,
        "question": question,
        "answer": None,
        "sources": [],
        "memory_used": False,
        "error": None
    }

    try:
        # Ensure user exists (create under this org if new)
        user = get_or_create_user(organization_id, user_id)
        if not user:
            result["error"] = "Failed to create/retrieve user"
            return result

        # Load org + AI employee metadata for persona building
        org = get_organization(organization_id) or {}
        agent = get_ai_employee(ai_employee_id) or {}

        org_name = org.get("name", "the organization")
        ai_name = agent.get("name", "AI Assistant")
        ai_role = agent.get("role", "Assistant")
        job_desc = agent.get("job_description", "")
        user_name = user.get("name", "")

        # Retrieve relevant shared org docs
        context, sources = retrieve_context(organization_id, question, k=4)
        result["sources"] = sources

        # Load memory: this user's conversations with THIS specific agent
        memory = get_user_ai_employee_memory(organization_id, ai_employee_id, user_id, limit=20)
        result["memory_used"] = len(memory) > 0

        # Generate answer
        answer = generate_answer(
            org_name=org_name,
            ai_employee_name=ai_name,
            ai_employee_role=ai_role,
            job_description=job_desc,
            user_name=user_name,
            query=question,
            context=context,
            sources=sources,
            memory=memory
        )
        result["answer"] = answer

        # Persist conversation
        save_message(organization_id, ai_employee_id, user_id, "user", question)
        save_message(organization_id, ai_employee_id, user_id, "assistant", answer)

        return result

    except Exception as e:
        print(f"Error in answer_question: {e}")
        result["error"] = str(e)
        return result
