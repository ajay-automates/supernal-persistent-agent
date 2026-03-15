"""
Supernal Persistent Agent - FastAPI Application
3-Tier Multi-Tenant: Organization → AI Employees → Users → Conversations
"""

import os
import io
import time
import traceback
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from openai import OpenAI

from config import OPENAI_API_KEY, supabase
from agent import answer_question_with_tools, stream_answer_with_tools
from rbac import RoleBasedAccessControl
import demo_setup
from db import (
    # Organization
    create_organization, get_organization, list_organizations,
    # AI Employees
    create_ai_employee, get_ai_employees, get_ai_employee,
    assign_ai_employee_to_user, get_user_assigned_ai_employees,
    get_role_id_by_name, get_access_attempts,
    # Users
    create_user, get_user, get_org_users, get_or_create_user,
    delete_user,
    # Conversations / memory
    get_user_ai_employee_memory, clear_user_ai_employee_memory,
    # Documents
    save_organization_document, save_organization_chunk,
    get_organization_documents, clear_organization_documents,
    # Tools
    register_tool, get_organization_tools, get_tool_execution_history,
    # Jobs
    get_job, list_jobs,
    # Observability
    log_api_call, log_error, get_org_metrics,
    # Stats & validation
    get_stats, validate_hierarchy,
    # Tool Verification
    get_emails_sent, get_crm_leads, get_support_tickets,
    get_calendar_events, get_equipment_orders
)

app = FastAPI(
    title="Supernal Persistent Agent",
    description="3-Tier Multi-Tenant RAG Agent: Organization → AI Employees → Users",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Track latency for every request and log to api_logs."""
    t0 = time.time()
    try:
        response = await call_next(request)
        latency_ms = int((time.time() - t0) * 1000)
        log_api_call(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )
        response.headers["X-Process-Time"] = str(latency_ms)
        return response
    except Exception as exc:
        latency_ms = int((time.time() - t0) * 1000)
        log_error(
            error_message=str(exc),
            error_type=type(exc).__name__,
            stack_trace=traceback.format_exc(),
        )
        raise


client = OpenAI(api_key=OPENAI_API_KEY)
rbac = RoleBasedAccessControl(supabase)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ============================================================
# UTILITIES
# ============================================================

def chunk_text(text: str) -> list:
    chunks = []
    for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = text[i:i + CHUNK_SIZE]
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks


def require_valid_hierarchy(organization_id: str, ai_employee_id: str, user_id: str):
    """Raise 422 if the three IDs don't form a valid hierarchy"""
    error = validate_hierarchy(organization_id, ai_employee_id, user_id)
    if error:
        raise HTTPException(status_code=422, detail=error)


# ============================================================
# PYDANTIC MODELS
# ============================================================

class OrganizationCreate(BaseModel):
    name: str

class AIEmployeeCreate(BaseModel):
    organization_id: str
    name: str
    role: str
    job_description: str = ""

class UserCreate(BaseModel):
    organization_id: str
    user_id: str
    name: str = ""
    email: str = ""

class AssignAIEmployee(BaseModel):
    user_id: str
    ai_employee_id: str


# ============================================================
# ORGANIZATION ENDPOINTS
# ============================================================

@app.post("/api/organization", status_code=201)
async def create_org(body: OrganizationCreate):
    """Create a new organization (top-level tenant)"""
    org = create_organization(body.name)
    if not org:
        raise HTTPException(status_code=500, detail="Failed to create organization")
    return org


@app.get("/api/organization/{org_id}")
async def get_org(org_id: str):
    """Get organization details + its AI employees and users"""
    org = get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    employees = get_ai_employees(org_id)
    users = get_org_users(org_id)
    return {**org, "ai_employees": employees, "users": users}


@app.get("/api/organizations")
async def list_orgs():
    """List all organizations"""
    return {"organizations": list_organizations()}


# ============================================================
# AI EMPLOYEE ENDPOINTS
# ============================================================

@app.post("/api/ai-employee", status_code=201)
async def create_agent(body: AIEmployeeCreate):
    """Create an AI employee within an organization"""
    org = get_organization(body.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not get_role_id_by_name(body.role):
        raise HTTPException(status_code=422, detail=f"Unsupported RBAC role '{body.role}'")
    employee = create_ai_employee(
        body.organization_id, body.name, body.role, body.job_description
    )
    if not employee:
        raise HTTPException(status_code=500, detail="Failed to create AI employee")
    return employee


@app.get("/api/ai-employees/{org_id}")
async def list_agents(org_id: str):
    """List all AI employees in an organization"""
    org = get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    agents = [
        rbac.get_agent_info(agent["id"], org_id) or agent
        for agent in get_ai_employees(org_id)
    ]
    return {"ai_employees": agents, "organization": org}


@app.get("/api/agents/{organization_id}/{user_id}")
async def get_user_agents(organization_id: str, user_id: str):
    """Get RBAC-enriched AI employees assigned to a user."""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    user = get_user(user_id)
    if not user or user.get("organization_id") != organization_id:
        raise HTTPException(status_code=404, detail="User not found in this organization")
    agents = rbac.get_user_assigned_agents(user_id, organization_id)
    return {"ai_employees": agents, "count": len(agents), "user_id": user_id}


@app.get("/api/agent-info/{organization_id}/{ai_employee_id}")
async def get_agent_info_endpoint(organization_id: str, ai_employee_id: str):
    """Get one AI employee with RBAC role and allowed tools."""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    agent = rbac.get_agent_info(ai_employee_id, organization_id)
    if not agent:
        raise HTTPException(status_code=404, detail="AI employee not found")
    return agent


@app.get("/api/access-log/{organization_id}")
async def get_access_log_endpoint(
    organization_id: str,
    user_id: str = None,
    ai_employee_id: str = None,
    limit: int = 100,
):
    """Return recent RBAC tool access attempts."""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    attempts = get_access_attempts(
        organization_id, user_id=user_id, ai_employee_id=ai_employee_id, limit=limit
    )
    return {"attempts": attempts, "count": len(attempts)}


# ============================================================
# USER ENDPOINTS
# ============================================================

@app.post("/api/user", status_code=201)
async def create_user_endpoint(body: UserCreate):
    """Create a user within an organization"""
    org = get_organization(body.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    user = create_user(body.organization_id, body.user_id, body.name, body.email)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return user


@app.get("/api/users/{org_id}")
async def list_users(org_id: str):
    """List all users in an organization"""
    org = get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"users": get_org_users(org_id), "organization": org}


@app.delete("/api/user/{user_id}")
async def delete_user_endpoint(user_id: str):
    """Delete a user and all their conversation history"""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    success = delete_user(user_id)
    return {"status": "success" if success else "failed"}


@app.post("/api/assign-ai-employee")
async def assign_agent(body: AssignAIEmployee):
    """Assign an AI employee to a user"""
    user = get_user(body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    agent = get_ai_employee(body.ai_employee_id)
    if not agent:
        raise HTTPException(status_code=404, detail="AI employee not found")
    if agent["organization_id"] != user["organization_id"]:
        raise HTTPException(status_code=422, detail="AI employee and user must belong to the same organization")
    success = assign_ai_employee_to_user(body.user_id, body.ai_employee_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to assign AI employee")
    return {"status": "assigned", "user_id": body.user_id, "ai_employee_id": body.ai_employee_id}


@app.get("/api/user/{user_id}/ai-employees")
async def get_assigned_agents(user_id: str):
    """Get all AI employees assigned to a user"""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    org_id = user.get("organization_id")
    agents = rbac.get_user_assigned_agents(user_id, org_id) if org_id else get_user_assigned_ai_employees(user_id)
    return {"ai_employees": agents, "user_id": user_id}


# ============================================================
# DOCUMENT ENDPOINTS  (org-scoped, shared by all employees/users)
# ============================================================

@app.post("/api/upload-text")
async def upload_text(
    organization_id: str = Form(...),
    filename: str = Form(default="pasted_text"),
    text: str = Form(...)
):
    """Upload text to org knowledge base (accessible by all AI employees)"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Empty text")

        org = get_organization(organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        doc_id = save_organization_document(organization_id, filename, filename)
        chunks = chunk_text(text)

        for chunk in chunks:
            emb = client.embeddings.create(model="text-embedding-3-small", input=chunk)
            save_organization_chunk(organization_id, chunk, emb.data[0].embedding, filename)

        return {"status": "success", "chunks_created": len(chunks), "characters": len(text), "doc_id": doc_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-file")
async def upload_file(
    organization_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload PDF/TXT/MD to org knowledge base"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        org = get_organization(organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        contents = await file.read()

        if file.filename.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(contents))
            text = "".join(
                (page.extract_text() or "") + "\n" for page in reader.pages
            ).strip()
            if not text:
                raise HTTPException(status_code=400, detail="No text extracted from PDF")

        elif file.filename.lower().endswith((".txt", ".md")):
            text = contents.decode("utf-8", errors="ignore").strip()
            if not text:
                raise HTTPException(status_code=400, detail="Empty file")

        else:
            raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files supported")

        doc_id = save_organization_document(organization_id, file.filename, file.filename)
        chunks = chunk_text(text)

        for chunk in chunks:
            emb = client.embeddings.create(model="text-embedding-3-small", input=chunk)
            save_organization_chunk(organization_id, chunk, emb.data[0].embedding, file.filename)

        return {"status": "success", "filename": file.filename, "chunks_created": len(chunks), "doc_id": doc_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents(organization_id: str):
    """List all documents in the org knowledge base"""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    docs = get_organization_documents(organization_id)
    return {"documents": docs, "count": len(docs), "organization": org.get("name")}


@app.delete("/api/documents")
async def delete_documents(organization_id: str):
    """Delete all documents and chunks from the org knowledge base"""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    success = clear_organization_documents(organization_id)
    return {"status": "success" if success else "failed"}


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post("/api/chat")
async def chat(
    organization_id: str = Form(...),
    ai_employee_id: str = Form(...),
    user_id: str = Form(...),
    question: str = Form(...)
):
    """
    Main chat endpoint with 3-tier isolation.
    Memory is scoped to (organization_id, ai_employee_id, user_id).
    """
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Empty question")

        # Validate org + agent; auto-create user in this org if new
        org = get_organization(organization_id)
        if not org:
            raise HTTPException(status_code=422, detail=f"Organization not found")
        agent = get_ai_employee(ai_employee_id)
        if not agent or agent.get("organization_id") != organization_id:
            raise HTTPException(status_code=422, detail="AI employee not found in this organization")
        user = get_or_create_user(organization_id, user_id)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create/retrieve user")
        if user.get("organization_id") != organization_id:
            raise HTTPException(status_code=422, detail=f"User '{user_id}' belongs to a different organization")
        user_access_allowed, user_access_error = rbac.can_user_access_ai_employee(
            user_id, ai_employee_id, organization_id
        )
        if not user_access_allowed:
            raise HTTPException(status_code=403, detail=user_access_error)

        result = answer_question_with_tools(organization_id, ai_employee_id, user_id, question)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "user_id": user_id,
            "question": question,
            "answer": result.get("answer"),
            "tool_used": result.get("tool_used"),
            "tool_result": result.get("tool_result"),
            "sources": result.get("sources", []),
            "memory_used": result.get("memory_used", False)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(
    organization_id: str = Form(...),
    ai_employee_id: str = Form(...),
    user_id: str = Form(...),
    question: str = Form(...)
):
    """
    Stream chat responses token-by-token using Server-Sent Events.
    Each line is a JSON object: {"type":"token","content":"..."} etc.
    Final line: {"type":"done","sources":[...],"tool_used":...,"memory_used":bool}
    """
    if not question.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=422, detail="Organization not found")
    agent = get_ai_employee(ai_employee_id)
    if not agent or agent.get("organization_id") != organization_id:
        raise HTTPException(status_code=422, detail="AI employee not found in this organization")
    user = get_or_create_user(organization_id, user_id)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create/retrieve user")
    user_access_allowed, user_access_error = rbac.can_user_access_ai_employee(
        user_id, ai_employee_id, organization_id
    )
    if not user_access_allowed:
        raise HTTPException(status_code=403, detail=user_access_error)

    async def generate():
        async for event in stream_answer_with_tools(
            organization_id, ai_employee_id, user_id, question
        ):
            yield f"data: {event}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ============================================================
# TOOL ENDPOINTS
# ============================================================

class ToolRegister(BaseModel):
    organization_id: str
    name: str
    description: str = ""
    schema: dict = {}
    endpoint: str = ""


@app.post("/api/tools/register", status_code=201)
async def register_tool_endpoint(body: ToolRegister):
    """Register a new tool for an organization"""
    org = get_organization(body.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    try:
        tool = register_tool(
            body.organization_id, body.name, body.description,
            body.schema, body.endpoint
        )
        if not tool:
            raise HTTPException(status_code=500, detail="Failed to register tool")
        return {"status": "success", "tool": tool}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools/{organization_id}")
async def list_tools(organization_id: str):
    """List all tools available to an organization"""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    try:
        tools = get_organization_tools(organization_id)
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tool-executions/{organization_id}/{ai_employee_id}")
async def get_tool_executions(organization_id: str, ai_employee_id: str, user_id: str):
    """Get tool execution history for a (org, agent, user) triple"""
    require_valid_hierarchy(organization_id, ai_employee_id, user_id)
    try:
        executions = get_tool_execution_history(organization_id, ai_employee_id, user_id)
        return {"executions": executions, "count": len(executions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# TOOL VERIFICATION ENDPOINTS
# ============================================================

@app.get("/api/verify/emails/{organization_id}")
async def get_verified_emails(organization_id: str):
    """Get all emails sent by AI employees (verification dashboard)"""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    try:
        emails = get_emails_sent(organization_id)
        return {
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/verify/crm-leads/{organization_id}")
async def get_verified_crm_leads(organization_id: str):
    """Get all CRM leads added by AI employees (verification dashboard)"""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    try:
        leads = get_crm_leads(organization_id)
        return {
            "count": len(leads),
            "leads": leads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/verify/tickets/{organization_id}")
async def get_verified_tickets(organization_id: str):
    """Get all support tickets created by AI employees (verification dashboard)"""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    try:
        tickets = get_support_tickets(organization_id)
        return {
            "count": len(tickets),
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/verify/calendar/{organization_id}")
async def get_verified_calendar(organization_id: str):
    """Get all calendar events scheduled by AI employees (verification dashboard)"""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    try:
        events = get_calendar_events(organization_id)
        return {
            "count": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/verify/equipment/{organization_id}")
async def get_verified_equipment(organization_id: str):
    """Get all equipment orders placed by AI employees (verification dashboard)"""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    try:
        orders = get_equipment_orders(organization_id)
        return {
            "count": len(orders),
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# JOB QUEUE ENDPOINTS
# ============================================================

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Fetch the status and result of a background job by its ID."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return job


@app.get("/api/jobs")
async def list_jobs_endpoint(organization_id: str = None, limit: int = 50):
    """List recent background jobs, optionally filtered by organization."""
    return {"jobs": list_jobs(organization_id, limit), "count": limit}


# ============================================================
# TTS ENDPOINT
# ============================================================

@app.post("/api/tts")
async def text_to_speech(
    text: str = Form(...),
    voice: str = Form(default="nova"),
    speed: float = Form(default=1.0)
):
    """High-quality TTS using OpenAI tts-1-hd model"""
    try:
        speed = max(0.25, min(4.0, speed))
        if voice not in {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}:
            voice = "nova"
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text[:4096],
            speed=speed
        )
        audio_bytes = response.read()
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/mpeg",
            headers={"Content-Length": str(len(audio_bytes))}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# MEMORY ENDPOINTS
# ============================================================

@app.get("/api/memory")
async def get_memory(organization_id: str, ai_employee_id: str, user_id: str):
    """Get conversation history for a specific (org, agent, user) triple"""
    require_valid_hierarchy(organization_id, ai_employee_id, user_id)
    memory = get_user_ai_employee_memory(organization_id, ai_employee_id, user_id, limit=50)
    return {"memory": memory, "count": len(memory)}


@app.delete("/api/memory")
async def delete_memory(organization_id: str, ai_employee_id: str, user_id: str):
    """Clear conversation history for a specific (org, agent, user) triple"""
    require_valid_hierarchy(organization_id, ai_employee_id, user_id)
    success = clear_user_ai_employee_memory(organization_id, ai_employee_id, user_id)
    return {"status": "success" if success else "failed"}


# ============================================================
# STATS ENDPOINT
# ============================================================

@app.get("/api/stats")
async def get_statistics(organization_id: str, ai_employee_id: str, user_id: str):
    """Get statistics scoped to (org, agent, user) triple"""
    require_valid_hierarchy(organization_id, ai_employee_id, user_id)
    return get_stats(organization_id, ai_employee_id, user_id)


# ============================================================
# OBSERVABILITY ENDPOINTS
# ============================================================

def _get_recommendations(metrics: dict) -> list:
    recs = []
    if metrics.get("avg_latency_ms", 0) > 2000:
        recs.append("High latency detected. Consider caching frequently accessed documents.")
    if metrics.get("error_count", 0) > 5:
        recs.append(f"High error rate ({metrics['error_count']} errors). Check error logs.")
    if metrics.get("total_cost_usd", 0) > 100:
        recs.append(f"High LLM costs (${metrics['total_cost_usd']}). Consider longer memory windows.")
    return recs


@app.get("/api/observability/metrics/{organization_id}")
async def get_metrics(organization_id: str):
    """Aggregate observability metrics for an organization."""
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    metrics = get_org_metrics(organization_id)
    if not metrics:
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")
    return metrics


@app.get("/api/observability/dashboard/{organization_id}")
async def get_dashboard(organization_id: str):
    """Full observability dashboard with health status and recommendations."""
    from datetime import datetime
    org = get_organization(organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    metrics = get_org_metrics(organization_id)
    if not metrics:
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "organization": org.get("name"),
        "metrics": metrics,
        "health_status": "healthy" if metrics.get("error_count", 0) < 10 else "warning",
        "recommendations": _get_recommendations(metrics),
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0", "service": "Supernal Persistent Agent"}


# ============================================================
# DEMO SETUP ENDPOINT
# ============================================================

@app.post("/api/demo/setup")
async def run_demo_setup():
    """Seed the database with Amazon, Stripe, and TechVentus demo data."""
    try:
        result = demo_setup.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ROOT — serve the UI
# ============================================================

@app.get("/")
async def root():
    return FileResponse("index.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
