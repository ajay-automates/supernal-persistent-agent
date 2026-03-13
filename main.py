"""
Supernal Persistent Agent - FastAPI Application
3-Tier Multi-Tenant: Organization → AI Employees → Users → Conversations
"""

import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from openai import OpenAI

from config import OPENAI_API_KEY
from agent import answer_question
from db import (
    # Organization
    create_organization, get_organization, list_organizations,
    # AI Employees
    create_ai_employee, get_ai_employees, get_ai_employee,
    assign_ai_employee_to_user, get_user_assigned_ai_employees,
    # Users
    create_user, get_user, get_org_users, get_or_create_user,
    # Conversations / memory
    get_user_ai_employee_memory, clear_user_ai_employee_memory,
    # Documents
    save_organization_document, save_organization_chunk,
    get_organization_documents, clear_organization_documents,
    # Stats & validation
    get_stats, validate_hierarchy
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

client = OpenAI(api_key=OPENAI_API_KEY)

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
    return {"ai_employees": get_ai_employees(org_id), "organization": org}


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
    return {"ai_employees": get_user_assigned_ai_employees(user_id), "user_id": user_id}


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

        require_valid_hierarchy(organization_id, ai_employee_id, user_id)

        result = answer_question(organization_id, ai_employee_id, user_id, question)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "organization_id": organization_id,
            "ai_employee_id": ai_employee_id,
            "user_id": user_id,
            "question": question,
            "answer": result.get("answer"),
            "sources": result.get("sources", []),
            "memory_used": result.get("memory_used", False)
        }

    except HTTPException:
        raise
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
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0", "service": "Supernal Persistent Agent"}


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
