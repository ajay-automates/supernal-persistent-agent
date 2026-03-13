"""
Agent module - Core agentic RAG orchestrator
Handles: retrieval, generation, memory management
"""

from config import OPENAI_API_KEY, LANGSMITH_API_KEY
from db import get_or_create_user, save_message, get_user_memory, search_user_chunks
from openai import OpenAI
from typing import List, Dict, Tuple
import os

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Optional LangSmith tracing
if LANGSMITH_API_KEY:
    from langsmith import traceable
else:
    def traceable(name=None, run_type=None):
        """No-op decorator if LangSmith not available"""
        def decorator(func):
            return func
        return decorator


# ============================================================
# RETRIEVAL
# ============================================================

@traceable(name="retrieve_context", run_type="retriever")
def retrieve_context(user_id: str, query: str, k: int = 4) -> Tuple[str, List[Dict]]:
    """
    Retrieve relevant context from user's documents
    Returns: (context_string, list_of_sources)
    """
    try:
        # Get query embedding
        embedding_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Search user's chunks
        results = search_user_chunks(user_id, query_embedding, k=k)
        
        if not results:
            return "No relevant documents found.", []
        
        # Format context
        context_parts = []
        sources = []
        
        for result in results:
            context_parts.append(f"[Source: {result.get('source', 'Unknown')}]\n{result.get('text', '')}")
            if result.get('source') not in sources:
                sources.append(result.get('source'))
        
        context = "\n\n---\n\n".join(context_parts)
        return context, sources
    
    except Exception as e:
        print(f"Error in retrieve_context: {e}")
        return f"Error retrieving context: {str(e)}", []


# ============================================================
# GENERATION
# ============================================================

@traceable(name="generate_answer", run_type="chain")
def generate_answer(
    user_id: str,
    query: str,
    context: str,
    sources: List[str],
    memory: List[Dict]
) -> str:
    """
    Generate answer using:
    - Current query
    - Retrieved context from documents
    - User's past conversations (memory)
    """
    try:
        # Build system prompt
        system_prompt = """You are a helpful AI assistant with persistent memory of past conversations.
When answering questions:
1. Use the provided context from documents as the primary source
2. Reference relevant past conversations when helpful
3. Be concise and direct
4. If you don't know something, say so clearly
5. Always be honest about what you do and don't know from the provided context"""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add relevant past conversations (last 6 turns = 12 messages)
        for msg in memory[-12:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current query with context
        context_prompt = f"""
Retrieved Document Context:
---
{context}
---

Sources: {', '.join(sources) if sources else 'None'}

Question: {query}"""
        
        messages.append({"role": "user", "content": context_prompt})
        
        # Generate response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=800,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        return answer
    
    except Exception as e:
        print(f"Error in generate_answer: {e}")
        return f"Error generating answer: {str(e)}"


# ============================================================
# MAIN AGENT PIPELINE
# ============================================================

@traceable(name="agent_pipeline", run_type="chain")
def answer_question(user_id: str, question: str) -> Dict:
    """
    Main agent pipeline:
    1. Ensure user exists
    2. Retrieve relevant context
    3. Get user's past memory
    4. Generate answer using all context
    5. Save to memory
    """
    result = {
        "user_id": user_id,
        "question": question,
        "answer": None,
        "sources": [],
        "memory_used": False,
        "error": None
    }
    
    try:
        # Ensure user exists
        user = get_or_create_user(user_id)
        if not user:
            result["error"] = "Failed to create/retrieve user"
            return result
        
        # Retrieve context from documents
        context, sources = retrieve_context(user_id, question, k=4)
        result["sources"] = sources
        
        # Get user's past conversations (memory)
        memory = get_user_memory(user_id, limit=20)
        result["memory_used"] = len(memory) > 0
        
        # Generate answer
        answer = generate_answer(user_id, question, context, sources, memory)
        result["answer"] = answer
        
        # Save to memory for future reference
        save_message(user_id, "user", question)
        save_message(user_id, "assistant", answer)
        
        return result
    
    except Exception as e:
        print(f"Error in answer_question: {e}")
        result["error"] = str(e)
        return result


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def chat_with_memory(user_id: str, messages: List[Dict]) -> str:
    """
    Alternative: Accept message history directly
    Useful for multi-turn conversations in a single request
    """
    if not messages:
        return "No messages provided"
    
    last_message = messages[-1].get("content", "")
    return answer_question(user_id, last_message)["answer"]
