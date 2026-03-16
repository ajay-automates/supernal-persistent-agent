"""
Agent module - 3-Tier RAG orchestrator
Pipeline: retrieve org docs → load user+agent memory → generate → save
"""

from config import OPENAI_API_KEY, LANGSMITH_API_KEY, supabase
from tools import route_tool_call  # rich mock implementations
from db import (
    get_or_create_user, save_message,
    get_user_ai_employee_memory, search_organization_chunks,
    get_organization, get_ai_employee,
    log_tool_execution,
    store_conversation_embedding, search_semantic_memory,
    log_llm_call, log_error,
)
from rbac import RoleBasedAccessControl
from openai import OpenAI, AsyncOpenAI
from worker import register_task, submit as worker_submit, submit_async as worker_submit_async
from typing import List, Dict, Tuple, Optional, AsyncGenerator
import os
import json
import time
import uuid

client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
rbac = RoleBasedAccessControl(supabase)


def _llm_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate USD cost for a completion call (gpt-4o-mini pricing)."""
    if "gpt-4o-mini" in model:
        return (prompt_tokens * 0.00000015) + (completion_tokens * 0.0000006)
    return 0.0


def _log_to_langsmith(model: str, prompt_tokens: int, completion_tokens: int, latency_ms: int):
    """Log LLM token usage to Langsmith run context."""
    if not LANGSMITH_API_KEY:
        return
    try:
        from langsmith.run_trees import get_run_tree
        run_tree = get_run_tree()
        if run_tree:
            cost = _llm_cost(model, prompt_tokens, completion_tokens)
            run_tree.add_metadata({
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost_usd": cost,
                "latency_ms": latency_ms
            })
    except Exception as e:
        print(f"Warning: Could not log to Langsmith: {e}")

# Optional LangSmith tracing
if LANGSMITH_API_KEY:
    from langsmith import traceable
    from langsmith.run_trees import RunTree
else:
    def traceable(name=None, run_type=None):
        def decorator(func):
            return func
        return decorator


# ============================================================
# RETRIEVAL
# ============================================================

@traceable(name="retrieve_organization_context", run_type="retriever")
def _retrieve_organization_docs(organization_id: str, query_embedding: List[float], k: int = 4) -> List[dict]:
    """Retrieve docs from organization knowledge base."""
    return search_organization_chunks(organization_id, query_embedding, k=k)


@traceable(name="generate_embeddings", run_type="retriever")
def _generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for a query."""
    embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    # Log embedding tokens to Langsmith
    if hasattr(embedding_response, 'usage'):
        _log_to_langsmith("text-embedding-3-small", embedding_response.usage.prompt_tokens, 0, 0)
    return embedding_response.data[0].embedding


@traceable(name="retrieve_context", run_type="retriever")
def retrieve_context(
    organization_id: str, query: str, k: int = 4
) -> Tuple[str, List[str]]:
    """
    Retrieve relevant context from the organization's shared documents.
    Returns (context_string, sources_list).
    """
    try:
        query_embedding = _generate_query_embedding(query)
        results = _retrieve_organization_docs(organization_id, query_embedding, k=k)

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
# SEMANTIC MEMORY
# ============================================================

@register_task("embed_turn")
def _embed_turn_background(
    organization_id: str,
    ai_employee_id: str,
    user_id: str,
    question: str,
    answer: str,
    conv_id: str = None
) -> dict:
    """
    Background task: embed a Q&A turn and store in conversation_embeddings.
    Registered as the "embed_turn" worker task so it is tracked in the jobs table.
    """
    try:
        text = f"User: {question}\nAssistant: {answer}"

        # Generate embedding
        _t_emb = int(time.time() * 1000)
        emb_resp = client.embeddings.create(
            model="text-embedding-3-small", input=text
        )
        _latency_emb = int(time.time() * 1000) - _t_emb
        emb = emb_resp.data[0].embedding
        if hasattr(emb_resp, 'usage'):
            log_llm_call(organization_id, ai_employee_id, "text-embedding-3-small",
                        emb_resp.usage.prompt_tokens, 0, emb_resp.usage.prompt_tokens,
                        _latency_emb, 0.0)

        # Generate summary
        _t_sum = int(time.time() * 1000)
        summary_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Summarize this conversation turn in 1-2 sentences:\n{text}"}],
            max_tokens=80,
            temperature=0.1
        )
        _latency_sum = int(time.time() * 1000) - _t_sum
        summary = summary_resp.choices[0].message.content.strip()
        log_llm_call(organization_id, ai_employee_id, "gpt-4o-mini",
                    summary_resp.usage.prompt_tokens, summary_resp.usage.completion_tokens,
                    summary_resp.usage.total_tokens, _latency_sum,
                    _llm_cost("gpt-4o-mini", summary_resp.usage.prompt_tokens, summary_resp.usage.completion_tokens))

        # Extract topics
        _t_top = int(time.time() * 1000)
        topics_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": (
                f"Extract 3-5 key topics from this conversation as a JSON array of strings:\n{text}\n"
                "Respond only with the JSON array, e.g. [\"topic1\", \"topic2\"]."
            )}],
            max_tokens=60,
            temperature=0.1
        )
        _latency_top = int(time.time() * 1000) - _t_top
        try:
            topics = json.loads(topics_resp.choices[0].message.content.strip())
        except Exception:
            topics = []
        log_llm_call(organization_id, ai_employee_id, "gpt-4o-mini",
                    topics_resp.usage.prompt_tokens, topics_resp.usage.completion_tokens,
                    topics_resp.usage.total_tokens, _latency_top,
                    _llm_cost("gpt-4o-mini", topics_resp.usage.prompt_tokens, topics_resp.usage.completion_tokens))

        store_conversation_embedding(
            organization_id, ai_employee_id, user_id,
            emb, summary, topics, conv_id
        )
        return {"status": "embedded", "summary": summary, "topics": topics}
    except Exception as e:
        print(f"Background embedding error: {e}")
        return {"status": "error", "error": str(e)}


@traceable(name="get_semantic_memory_context", run_type="retriever")
def get_semantic_memory_context(
    organization_id: str,
    ai_employee_id: str,
    user_id: str,
    question: str
) -> Dict:
    """
    Return a dict with:
      recent_memory   — last 10 messages (always included)
      relevant_memory — up to 5 semantically similar past turns
    """
    recent = get_user_ai_employee_memory(
        organization_id, ai_employee_id, user_id, limit=10
    )
    try:
        _t_emb = int(time.time() * 1000)
        emb_resp = client.embeddings.create(
            model="text-embedding-3-small", input=question
        )
        _latency_emb = int(time.time() * 1000) - _t_emb
        q_emb = emb_resp.data[0].embedding

        # Log embedding tokens
        if hasattr(emb_resp, 'usage'):
            log_llm_call(organization_id, ai_employee_id, "text-embedding-3-small",
                        emb_resp.usage.prompt_tokens, 0, emb_resp.usage.prompt_tokens,
                        _latency_emb, 0.0)

        semantic = search_semantic_memory(
            organization_id, ai_employee_id, user_id, q_emb, k=5
        )
    except Exception as e:
        print(f"Semantic memory search error: {e}")
        semantic = []

    return {"recent_memory": recent, "relevant_memory": semantic}


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

        _t0 = int(time.time() * 1000)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=800,
            temperature=0.3
        )
        _latency = int(time.time() * 1000) - _t0

        # Log token usage to Langsmith
        _log_to_langsmith("gpt-4o-mini", response.usage.prompt_tokens, response.usage.completion_tokens, _latency)

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


# ============================================================
# TOOL EXECUTION
# ============================================================

# route_tool_call is imported from tools.py above


def _extract_tool_call(response_text: str) -> Optional[dict]:
    """
    Parse TOOL:/PARAMS: block from the LLM response.
    Returns {"tool": str, "params": dict} or None.
    """
    try:
        lines = response_text.strip().splitlines()
        tool_name = None
        params_str = None
        for i, line in enumerate(lines):
            if line.startswith("TOOL:"):
                tool_name = line[len("TOOL:"):].strip()
            elif line.startswith("PARAMS:"):
                params_str = line[len("PARAMS:"):].strip()
                # Collect continuation lines until next blank or end
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        params_str += " " + lines[j].strip()
                    else:
                        break
        if tool_name and params_str:
            params = json.loads(params_str)
            return {"tool": tool_name, "params": params}
    except Exception as e:
        print(f"Error parsing tool call: {e}")
    return None


# ============================================================
# TOOL-AWARE AGENT PIPELINE
# ============================================================

def _build_allowed_tool_lines(agent_info: Dict) -> List[str]:
    """Format the agent's RBAC-allowed tools for the system prompt."""
    details = agent_info.get("allowed_tool_details") or []
    if details:
        return [f"{tool['tool_name']} - {tool.get('description', '')}".strip() for tool in details]
    return [tool_name for tool_name in agent_info.get("allowed_tools", [])]


@traceable(name="agent_pipeline_with_tools", run_type="chain")
def answer_question_with_tools(
    organization_id: str,
    ai_employee_id: str,
    user_id: str,
    question: str
) -> Dict:
    """
    Tool-aware agent pipeline:
    1. Fetch org / AI employee metadata for persona
    2. Retrieve relevant org-level documents
    3. Load user's past conversations with THIS agent
    4. Load org's registered tools
    5. First LLM call: decide if a tool is needed
    6. If tool needed: execute it and log the execution
    7. Second LLM call (if tool used): generate final answer using tool result
    8. Persist conversation
    """
    result = {
        "organization_id": organization_id,
        "ai_employee_id": ai_employee_id,
        "user_id": user_id,
        "question": question,
        "answer": None,
        "tool_used": None,
        "tool_result": None,
        "sources": [],
        "memory_used": False,
        "error": None
    }

    try:
        # Ensure user exists
        user = get_or_create_user(organization_id, user_id)
        if not user:
            result["error"] = "Failed to create/retrieve user"
            return result

        org = get_organization(organization_id) or {}
        agent = get_ai_employee(ai_employee_id) or {}
        agent_info = rbac.get_agent_info(ai_employee_id, organization_id)
        if not agent_info:
            result["error"] = "AI employee not found"
            return result

        user_access_allowed, user_access_error = rbac.can_user_access_ai_employee(
            user_id, ai_employee_id, organization_id
        )
        if not user_access_allowed:
            result["error"] = user_access_error
            return result

        org_name = org.get("name", "the organization")
        ai_name = agent.get("name", "AI Assistant")
        ai_role = agent.get("role", "Assistant")
        job_desc = agent.get("job_description", "")
        user_name = user.get("name", "")
        role_info = agent_info.get("role_details") or {}

        # Retrieve org docs + memory (recent + semantic)
        context, sources = retrieve_context(organization_id, question, k=4)
        result["sources"] = sources

        mem_ctx = get_semantic_memory_context(organization_id, ai_employee_id, user_id, question)
        recent_memory   = mem_ctx["recent_memory"]
        relevant_memory = mem_ctx["relevant_memory"]
        result["memory_used"] = len(recent_memory) > 0 or len(relevant_memory) > 0
        result["semantic_memory"] = relevant_memory

        allowed_tool_lines = _build_allowed_tool_lines(agent_info)
        tools_list = "\n".join(f"- {t}" for t in allowed_tool_lines) if allowed_tool_lines else "- No tools available"

        # Format relevant past memories for the prompt
        relevant_mem_text = ""
        if relevant_memory:
            snippets = "\n".join(
                f"- {m['summary']} (topics: {', '.join(m.get('topics') or [])})"
                for m in relevant_memory
            )
            relevant_mem_text = f"\nRelevant past discussions:\n{snippets}\n"

        system_prompt = f"""You are {ai_name}, an AI employee at {org_name}.
Your role: {role_info.get('role_name', ai_role)}
Your responsibilities: {role_info.get('job_description', job_desc) or 'Help users with their questions.'}

🚀 CRITICAL RULES FOR TOOL USAGE - EXECUTE IMMEDIATELY, NO QUESTIONS:

📧 SEND_EMAIL tool - Use when user asks to:
  • "send an email" / "send email" / "send an e-mail"
  • "email someone" / "contact via email" / "notify by email"
  • "send a message" (if it's email context)
  ALWAYS execute - never say "I can't send emails"

🎫 CREATE_SUPPORT_TICKET tool - Use when user asks to:
  • "create a ticket" / "create a support ticket"
  • "open a ticket" / "file a ticket" / "report an issue"
  • "create a case" / "submit a complaint"
  ALWAYS execute - never decline

📅 SCHEDULE_CALENDAR_EVENT tool - Use when user asks to:
  • "schedule a meeting" / "schedule a call" / "book a meeting"
  • "schedule an event" / "set up a meeting" / "arrange a call"
  • "send a calendar invite" / "add to calendar"
  ALWAYS execute - never hesitate

👤 CREATE_CRM_LEAD tool - Use when user asks to:
  • "add a lead" / "create a lead" / "add a prospect"
  • "add a customer" / "record a lead" / "add to CRM"
  • "add a contact for sales" / "add a company"
  ALWAYS execute - never refuse

📦 PLACE_EQUIPMENT_ORDER tool - Use when user asks to:
  • "order equipment" / "place an order" / "order supplies"
  • "buy equipment" / "order items" / "request equipment"
  • "order supplies" / "purchase" / "get equipment"
  ALWAYS execute - never say you can't

GOLDEN RULES:
✓ ALWAYS execute the tool when requested
✓ NEVER refuse, hesitate, or offer alternatives
✓ NEVER say "I'm unable to..." or "I can't..."
✓ Execute tool first, explain results after
✓ If tool not available, say "I don't have access to that tool"

Available tools:
{tools_list}

When using a tool, respond ONLY with this exact format (no other text):
TOOL: <tool_name>
PARAMS: {{"key": "value", ...}}

If user asks for something NOT in your tools, decline and explain.
If no tool is needed, answer directly.
{relevant_mem_text}
Organization Knowledge Base:
---
{context}
---
Sources: {', '.join(sources) if sources else 'None'}"""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in recent_memory[-12:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": question})

        # First LLM call: decide if tool needed
        _t0 = int(time.time() * 1000)
        first_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.2
        )
        _first_latency = int(time.time() * 1000) - _t0
        first_text = first_response.choices[0].message.content.strip()
        _u = first_response.usage

        # Log to both database and Langsmith
        log_llm_call(
            organization_id, ai_employee_id, "gpt-4o-mini",
            _u.prompt_tokens, _u.completion_tokens, _u.total_tokens,
            _first_latency, _llm_cost("gpt-4o-mini", _u.prompt_tokens, _u.completion_tokens),
        )
        _log_to_langsmith("gpt-4o-mini", _u.prompt_tokens, _u.completion_tokens, _first_latency)

        tool_call = _extract_tool_call(first_text)

        if tool_call:
            tool_name = tool_call["tool"]
            tool_params = tool_call["params"]

            # Execute the tool and time it
            start_ms = int(time.time() * 1000)
            try:
                allowed, error_msg = rbac.validate_tool_execution(
                    user_id, ai_employee_id, tool_name, organization_id
                )
                if not allowed:
                    tool_result = {"status": "denied", "error": error_msg}
                    status = "denied"
                else:
                    tool_result = route_tool_call(
                        tool_name, tool_params, organization_id, ai_employee_id, user_id
                    )
                    status = "success"
                    error_msg = None
            except Exception as te:
                tool_result = {"error": str(te)}
                status = "failed"
                error_msg = str(te)
            latency_ms = int(time.time() * 1000) - start_ms

            log_tool_execution(
                organization_id=organization_id,
                ai_employee_id=ai_employee_id,
                user_id=user_id,
                tool_name=tool_name,
                input_params=tool_params,
                output_result=tool_result,
                status=status,
                error_message=error_msg,
                latency_ms=latency_ms
            )

            result["tool_used"] = tool_name
            result["tool_result"] = tool_result

            # Second LLM call: explain result in natural language
            messages.append({"role": "assistant", "content": first_text})
            messages.append({
                "role": "user",
                "content": (
                    f"Tool '{tool_name}' returned: {json.dumps(tool_result)}. "
                    "Now respond to the user's original request naturally. "
                    "If the tool was denied, explain the restriction and offer role-appropriate alternatives."
                )
            })

            _t1 = int(time.time() * 1000)
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            _final_latency = int(time.time() * 1000) - _t1
            answer = final_response.choices[0].message.content.strip()
            _u2 = final_response.usage

            # Log to both database and Langsmith
            log_llm_call(
                organization_id, ai_employee_id, "gpt-4o-mini",
                _u2.prompt_tokens, _u2.completion_tokens, _u2.total_tokens,
                _final_latency, _llm_cost("gpt-4o-mini", _u2.prompt_tokens, _u2.completion_tokens),
            )
            _log_to_langsmith("gpt-4o-mini", _u2.prompt_tokens, _u2.completion_tokens, _final_latency)
        else:
            answer = first_text

        result["answer"] = answer

        # Persist conversation; capture assistant message ID for embedding reference
        save_message(organization_id, ai_employee_id, user_id, "user", question)
        asst_id = save_message(organization_id, ai_employee_id, user_id, "assistant", answer)

        # Background: embed this turn for future semantic memory retrieval
        worker_submit(
            "embed_turn",
            {"organization_id": organization_id, "ai_employee_id": ai_employee_id,
             "user_id": user_id, "question": question, "answer": answer, "conv_id": asst_id},
            organization_id=organization_id
        )

        return result

    except Exception as e:
        print(f"Error in answer_question_with_tools: {e}")
        result["error"] = str(e)
        return result


# Keep original as alias for backwards compatibility
answer_question = answer_question_with_tools


# ============================================================
# STREAMING PIPELINE
# ============================================================

async def stream_answer_with_tools(
    organization_id: str,
    ai_employee_id: str,
    user_id: str,
    question: str
) -> AsyncGenerator[str, None]:
    """
    Async streaming version of the tool-aware pipeline.
    Yields newline-delimited JSON SSE events:
      {"type":"token","content":"..."}        — streamed answer tokens
      {"type":"tool_start","tool_name":"..."}  — tool about to execute
      {"type":"tool_result","tool_name":"...","result":{...}}  — tool done
      {"type":"done","sources":[...],"tool_used":"...","tool_result":{...},"memory_used":bool}
      {"type":"error","message":"..."}        — on failure
    """
    try:
        user = get_or_create_user(organization_id, user_id)
        if not user:
            yield json.dumps({"type": "error", "message": "Failed to create/retrieve user"}) + "\n"
            return

        org = get_organization(organization_id) or {}
        agent = get_ai_employee(ai_employee_id) or {}
        agent_info = rbac.get_agent_info(ai_employee_id, organization_id)
        if not agent_info:
            yield json.dumps({"type": "error", "message": "AI employee not found"}) + "\n"
            return

        user_access_allowed, user_access_error = rbac.can_user_access_ai_employee(
            user_id, ai_employee_id, organization_id
        )
        if not user_access_allowed:
            yield json.dumps({"type": "error", "message": user_access_error}) + "\n"
            return

        org_name  = org.get("name", "the organization")
        ai_name   = agent.get("name", "AI Assistant")
        ai_role   = agent.get("role", "Assistant")
        job_desc  = agent.get("job_description", "")
        role_info = agent_info.get("role_details") or {}

        context, sources = retrieve_context(organization_id, question, k=4)

        mem_ctx = get_semantic_memory_context(organization_id, ai_employee_id, user_id, question)
        recent_memory   = mem_ctx["recent_memory"]
        relevant_memory = mem_ctx["relevant_memory"]
        memory_used = len(recent_memory) > 0 or len(relevant_memory) > 0

        allowed_tool_lines = _build_allowed_tool_lines(agent_info)
        tools_list = "\n".join(f"- {t}" for t in allowed_tool_lines) if allowed_tool_lines else "- No tools available"

        relevant_mem_text = ""
        if relevant_memory:
            snippets = "\n".join(
                f"- {m['summary']} (topics: {', '.join(m.get('topics') or [])})"
                for m in relevant_memory
            )
            relevant_mem_text = f"\nRelevant past discussions:\n{snippets}\n"

        system_prompt = f"""You are {ai_name}, an AI employee at {org_name}.
Your role: {role_info.get('role_name', ai_role)}
Your responsibilities: {role_info.get('job_description', job_desc) or 'Help users with their questions.'}

🚀 CRITICAL RULES FOR TOOL USAGE - EXECUTE IMMEDIATELY, NO QUESTIONS:

📧 SEND_EMAIL tool - Use when user asks to:
  • "send an email" / "send email" / "send an e-mail"
  • "email someone" / "contact via email" / "notify by email"
  • "send a message" (if it's email context)
  ALWAYS execute - never say "I can't send emails"

🎫 CREATE_SUPPORT_TICKET tool - Use when user asks to:
  • "create a ticket" / "create a support ticket"
  • "open a ticket" / "file a ticket" / "report an issue"
  • "create a case" / "submit a complaint"
  ALWAYS execute - never decline

📅 SCHEDULE_CALENDAR_EVENT tool - Use when user asks to:
  • "schedule a meeting" / "schedule a call" / "book a meeting"
  • "schedule an event" / "set up a meeting" / "arrange a call"
  • "send a calendar invite" / "add to calendar"
  ALWAYS execute - never hesitate

👤 CREATE_CRM_LEAD tool - Use when user asks to:
  • "add a lead" / "create a lead" / "add a prospect"
  • "add a customer" / "record a lead" / "add to CRM"
  • "add a contact for sales" / "add a company"
  ALWAYS execute - never refuse

📦 PLACE_EQUIPMENT_ORDER tool - Use when user asks to:
  • "order equipment" / "place an order" / "order supplies"
  • "buy equipment" / "order items" / "request equipment"
  • "order supplies" / "purchase" / "get equipment"
  ALWAYS execute - never say you can't

GOLDEN RULES:
✓ ALWAYS execute the tool when requested
✓ NEVER refuse, hesitate, or offer alternatives
✓ NEVER say "I'm unable to..." or "I can't..."
✓ Execute tool first, explain results after
✓ If tool not available, say "I don't have access to that tool"

Available tools:
{tools_list}

When using a tool, respond ONLY with this exact format (no other text):
TOOL: <tool_name>
PARAMS: {{"key": "value", ...}}

If user asks for something NOT in your tools, decline and explain.
If no tool is needed, answer directly.
{relevant_mem_text}
Organization Knowledge Base:
---
{context}
---
Sources: {', '.join(sources) if sources else 'None'}"""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in recent_memory[-12:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": question})

        # --- Step 1: async non-streaming tool-detection call (cheap, 150 tokens) ---
        _td0 = int(time.time() * 1000)
        detect_response = await async_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.2
        )
        _td_lat = int(time.time() * 1000) - _td0
        detect_text = detect_response.choices[0].message.content.strip()
        _du = detect_response.usage
        log_llm_call(
            organization_id, ai_employee_id, "gpt-4o-mini",
            _du.prompt_tokens, _du.completion_tokens, _du.total_tokens,
            _td_lat, _llm_cost("gpt-4o-mini", _du.prompt_tokens, _du.completion_tokens),
        )
        tool_call = _extract_tool_call(detect_text)

        tool_used = None
        tool_result = None

        if tool_call:
            tool_name   = tool_call["tool"]
            tool_params = tool_call["params"]

            yield json.dumps({"type": "tool_start", "tool_name": tool_name}) + "\n"

            start_ms = int(time.time() * 1000)
            try:
                allowed, error_msg = rbac.validate_tool_execution(
                    user_id, ai_employee_id, tool_name, organization_id
                )
                if not allowed:
                    tool_result = {"status": "denied", "error": error_msg}
                    status = "denied"
                else:
                    tool_result = route_tool_call(
                        tool_name, tool_params, organization_id, ai_employee_id, user_id
                    )
                    status = "success"
                    error_msg = None
            except Exception as te:
                tool_result = {"error": str(te)}
                status = "failed"
                error_msg = str(te)
            latency_ms = int(time.time() * 1000) - start_ms

            log_tool_execution(
                organization_id=organization_id,
                ai_employee_id=ai_employee_id,
                user_id=user_id,
                tool_name=tool_name,
                input_params=tool_params,
                output_result=tool_result,
                status=status,
                error_message=error_msg,
                latency_ms=latency_ms
            )
            tool_used = tool_name
            yield json.dumps({"type": "tool_result", "tool_name": tool_name, "result": tool_result}) + "\n"

            messages.append({"role": "assistant", "content": detect_text})
            messages.append({
                "role": "user",
                "content": (
                    f"Tool '{tool_name}' returned: {json.dumps(tool_result)}. "
                    "Now respond to the user's original request naturally. "
                    "If the tool was denied, explain the restriction and offer role-appropriate alternatives."
                )
            })

        # --- Step 2: async streaming call for the final answer ---
        stream = await async_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=800,
            temperature=0.3,
            stream=True
        )

        full_answer = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices[0].delta else None
            if delta:
                full_answer += delta
                yield json.dumps({"type": "token", "content": delta}) + "\n"

        # --- Step 3: persist + background embedding + signal done ---
        save_message(organization_id, ai_employee_id, user_id, "user", question)
        asst_id = save_message(organization_id, ai_employee_id, user_id, "assistant", full_answer)

        await worker_submit_async(
            "embed_turn",
            {"organization_id": organization_id, "ai_employee_id": ai_employee_id,
             "user_id": user_id, "question": question, "answer": full_answer, "conv_id": asst_id},
            organization_id=organization_id
        )

        yield json.dumps({
            "type": "done",
            "sources": sources,
            "tool_used": tool_used,
            "tool_result": tool_result,
            "memory_used": memory_used,
            "semantic_memory": relevant_memory,
        }) + "\n"

    except Exception as e:
        print(f"Error in stream_answer_with_tools: {e}")
        yield json.dumps({"type": "error", "message": str(e)}) + "\n"
