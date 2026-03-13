"""
Supernal Persistent Agent - FastAPI Application
Real-time voice & text agent with persistent multi-user memory
"""

import os
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader
from openai import OpenAI

from config import OPENAI_API_KEY
from agent import answer_question
from db import (
    save_document, save_chunk, get_user_documents,
    get_user_stats, clear_user_memory, clear_user_documents,
    get_user_memory, get_or_create_user
)

# Initialize FastAPI
app = FastAPI(
    title="Supernal Persistent Agent",
    description="Multi-user persistent memory RAG agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Split text into overlapping chunks"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks


# ============================================================
# DOCUMENT ENDPOINTS
# ============================================================

@app.post("/api/upload-text")
async def upload_text(user_id: str = Form(...), text: str = Form(...)):
    """Upload text directly"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Empty text")

        # Ensure user exists (required for FK constraint)
        get_or_create_user(user_id)

        # Save document metadata
        doc_id = save_document(user_id, "pasted_text", "User Pasted Text")
        
        # Chunk and embed
        chunks = chunk_text(text)
        
        for chunk in chunks:
            # Get embedding
            embedding_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            )
            embedding = embedding_response.data[0].embedding
            
            # Save chunk
            save_chunk(user_id, chunk, embedding, "User Pasted Text")
        
        return {
            "status": "success",
            "chunks_created": len(chunks),
            "characters": len(text),
            "doc_id": doc_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-file")
async def upload_file(user_id: str = Form(...), file: UploadFile = File(...)):
    """Upload PDF or text file"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Ensure user exists (required for FK constraint)
        get_or_create_user(user_id)

        contents = await file.read()
        
        # Handle PDF
        if file.filename.lower().endswith(".pdf"):
            try:
                reader = PdfReader(io.BytesIO(contents))
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if not text.strip():
                    raise HTTPException(status_code=400, detail="No text extracted from PDF")
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
        
        # Handle text files
        elif file.filename.lower().endswith((".txt", ".md")):
            text = contents.decode("utf-8", errors="ignore").strip()
            if not text:
                raise HTTPException(status_code=400, detail="Empty file")
        
        else:
            raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files supported")
        
        # Save document metadata
        doc_id = save_document(user_id, file.filename, file.filename)
        
        # Chunk and embed
        chunks = chunk_text(text)
        
        for chunk in chunks:
            embedding_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            )
            embedding = embedding_response.data[0].embedding
            
            save_chunk(user_id, chunk, embedding, file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": len(chunks),
            "doc_id": doc_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents(user_id: str):
    """List all documents for a user"""
    try:
        documents = get_user_documents(user_id)
        return {"documents": documents, "count": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents")
async def delete_documents(user_id: str):
    """Delete all documents for a user"""
    try:
        success = clear_user_documents(user_id)
        return {"status": "success" if success else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# CONVERSATION ENDPOINTS
# ============================================================

@app.post("/api/chat")
async def chat(user_id: str = Form(...), question: str = Form(...)):
    """Main chat endpoint - with persistent memory"""
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Empty question")
        
        result = answer_question(user_id, question)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
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


@app.get("/api/memory")
async def get_memory(user_id: str):
    """Get user's conversation history"""
    try:
        memory = get_user_memory(user_id, limit=20)
        return {"memory": memory, "count": len(memory)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/memory")
async def delete_memory(user_id: str):
    """Clear user's conversation history"""
    try:
        success = clear_user_memory(user_id)
        return {"status": "success" if success else "failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# STATISTICS
# ============================================================

@app.get("/api/stats")
async def get_stats(user_id: str):
    """Get statistics for a user"""
    try:
        stats = get_user_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Supernal Persistent Agent"
    }


# ============================================================
# ROOT ENDPOINT — serve the UI
# ============================================================

@app.get("/")
async def root():
    """Serve the main UI"""
    return FileResponse("index.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
