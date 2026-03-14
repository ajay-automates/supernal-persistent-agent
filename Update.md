You are an expert AI systems engineer building a production-grade multi-tenant AI employee platform. Build ALL missing features for the Supernal Persistent Agent system to make it competitive with enterprise AI platforms.

CURRENT STATE:
✅ Multi-tenant architecture (organization → AI employee → user)
✅ Persistent memory (PostgreSQL conversations)
✅ RAG pipeline (pgvector semantic search)
✅ Persona-based agents (Sales Bot, Support Bot, etc.)
✅ Clean 3-tier isolation

MISSING FEATURES TO BUILD:
This prompt covers 5 critical features that transform the system from a chatbot to an autonomous AI employee platform.

═══════════════════════════════════════════════════════════════════════════════

FEATURE #1: TOOL CALLING & EXECUTION (HIGHEST PRIORITY)

This is the single most important feature. It transforms your system from "chatbot that answers questions" to "autonomous agent that does work."

Current: Agent only answers questions
New: Agent decides which tool to use, executes it, reports result

1. DATABASE SCHEMA (Add to README SQL):

Create new tables:
```sql
-- Tools registry
CREATE TABLE tools (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  schema JSONB,  -- parameter definitions
  endpoint TEXT,  -- API endpoint
  created_at TIMESTAMP DEFAULT now()
);

-- Tool executions log
CREATE TABLE tool_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  ai_employee_id UUID NOT NULL,
  user_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  input_params JSONB,
  output_result JSONB,
  status TEXT,  -- 'pending', 'success', 'failed'
  error_message TEXT,
  latency_ms INTEGER,
  created_at TIMESTAMP DEFAULT now()
);

-- Index for fast lookups
CREATE INDEX idx_tool_executions_org_agent ON tool_executions(organization_id, ai_employee_id);
```

2. IMPLEMENT TOOLS IN db.py:

Add functions:
```python
def register_tool(organization_id, name, description, schema, endpoint):
    """Register a new tool for an organization"""
    
def get_organization_tools(organization_id):
    """Get all tools available to an org"""
    
def execute_tool(organization_id, ai_employee_id, user_id, tool_name, params):
    """Execute a tool and log the execution"""
    
def get_tool_execution_history(organization_id, ai_employee_id, user_id):
    """Get tool execution history for a user"""
```

3. IMPLEMENT TOOL ROUTER IN agent.py:

Add tool execution logic:
```python
def route_tool_call(organization_id, ai_employee_id, user_id, tool_name, params):
    """
    Route tool calls to appropriate executors.
    Supported tools:
    - send_email(to, subject, body)
    - create_ticket(customer, issue, priority)
    - query_crm(customer_id)
    - search_web(query)
    - update_database(table, record_id, data)
    - add_calendar_event(user, date, time, description)
    """
    
    # Tool implementations:
    if tool_name == "send_email":
        return send_email_tool(params)
    elif tool_name == "create_ticket":
        return create_ticket_tool(params)
    elif tool_name == "query_crm":
        return query_crm_tool(params)
    # ... etc
    
def answer_question_with_tools(organization_id, ai_employee_id, user_id, question):
    """
    New agent pipeline:
    1. Get user memory + documents
    2. Ask LLM if tool is needed
    3. If yes: Execute tool
    4. Use tool result in final answer
    5. Save tool execution + answer to memory
    """
    
    # Retrieve memory and documents
    memory = get_user_ai_employee_memory(organization_id, ai_employee_id, user_id)
    documents = search_organization_chunks(organization_id, question_embedding)
    
    # Build prompt that can trigger tools
    system_prompt = """
    You are an AI employee. You can use tools to perform work.
    
    Available tools:
    - send_email(to, subject, body) - Send an email
    - create_ticket(customer, issue, priority) - Create support ticket
    - query_crm(customer_id) - Look up customer info
    - search_web(query) - Search the internet
    - update_database(table, record_id, data) - Update database
    - add_calendar_event(user, date, time, description) - Schedule meeting
    
    When you need to use a tool, respond in this format:
    TOOL: <tool_name>
    PARAMS: <json_params>
    
    After the tool executes, explain the result naturally.
    """
    
    # First LLM call: decide if tool is needed
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=build_messages(memory, documents, question, system_prompt),
        max_tokens=500
    )
    
    # Check if tool was called
    if "TOOL:" in response.content:
        tool_section = extract_tool_call(response.content)
        tool_name = tool_section["tool"]
        params = tool_section["params"]
        
        # Execute the tool
        tool_result = route_tool_call(
            organization_id, ai_employee_id, user_id, 
            tool_name, params
        )
        
        # Second LLM call: explain result
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                ...previous_messages,
                {"role": "user", "content": f"Tool {tool_name} returned: {tool_result}. Now answer the user's original question."}
            ],
            max_tokens=500
        )
        
        final_answer = final_response.content
    else:
        final_answer = response.content
    
    # Save to memory
    save_conversation(organization_id, ai_employee_id, user_id, "user", question)
    save_conversation(organization_id, ai_employee_id, user_id, "assistant", final_answer)
    
    return {
        "answer": final_answer,
        "tool_used": tool_name if "TOOL:" in response.content else None,
        "tool_result": tool_result if "TOOL:" in response.content else None,
        "sources": documents
    }
```

4. ADD TOOL ENDPOINTS IN main.py:
```python
@app.post("/api/tools/register")
async def register_tool(
    organization_id: str,
    name: str,
    description: str,
    schema: dict,
    endpoint: str
):
    """Register a new tool for an organization"""
    try:
        success = register_tool(organization_id, name, description, schema, endpoint)
        return {"status": "success", "tool_name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools/{organization_id}")
async def list_tools(organization_id: str):
    """List all tools available to an organization"""
    try:
        tools = get_organization_tools(organization_id)
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tool-executions/{organization_id}/{ai_employee_id}")
async def get_executions(organization_id: str, ai_employee_id: str, user_id: str):
    """Get tool execution history"""
    try:
        executions = get_tool_execution_history(organization_id, ai_employee_id, user_id)
        return {"executions": executions, "count": len(executions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

5. UPDATE /api/chat ENDPOINT:

Modify existing endpoint to use new tool-aware agent:
```python
@app.post("/api/chat")
async def chat(
    organization_id: str = Form(...),
    ai_employee_id: str = Form(...),
    user_id: str = Form(...),
    question: str = Form(...)
):
    """Chat with AI employee (now with tool execution)"""
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Empty question")
        
        # Use new tool-aware pipeline
        result = answer_question_with_tools(
            organization_id, 
            ai_employee_id, 
            user_id, 
            question
        )
        
        return {
            "user_id": user_id,
            "question": question,
            "answer": result["answer"],
            "tool_used": result.get("tool_used"),
            "tool_result": result.get("tool_result"),
            "sources": result.get("sources", []),
            "memory_used": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

═══════════════════════════════════════════════════════════════════════════════

FEATURE #2: STREAMING RESPONSES

Make responses feel fast and responsive by streaming tokens as they're generated.

1. UPDATE agent.py:
```python
async def stream_answer_with_tools(organization_id, ai_employee_id, user_id, question):
    """
    Stream tokens as they're generated instead of waiting for full response.
    Yields tokens one at a time for real-time display.
    """
    
    memory = get_user_ai_employee_memory(organization_id, ai_employee_id, user_id)
    documents = search_organization_chunks(organization_id, question_embedding)
    
    # Create streaming LLM call
    with client.chat.completions.create(
        model="gpt-4o-mini",
        messages=build_messages(memory, documents, question),
        max_tokens=800,
        stream=True  # Enable streaming
    ) as response:
        full_answer = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_answer += token
                yield token  # Yield each token
    
    # Save full answer to memory after streaming completes
    save_conversation(organization_id, ai_employee_id, user_id, "user", question)
    save_conversation(organization_id, ai_employee_id, user_id, "assistant", full_answer)
```

2. UPDATE main.py ENDPOINT:
```python
from fastapi.responses import StreamingResponse

@app.post("/api/chat/stream")
async def chat_stream(
    organization_id: str = Form(...),
    ai_employee_id: str = Form(...),
    user_id: str = Form(...),
    question: str = Form(...)
):
    """Stream chat responses token by token"""
    try:
        async def generate():
            async for token in stream_answer_with_tools(
                organization_id, ai_employee_id, user_id, question
            ):
                yield f"data: {token}\n\n"
        
        return StreamingResponse(
            generate(), 
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

3. UPDATE index.html:

Add streaming support to chat UI:
```javascript
async function sendMessageWithStreaming(organizationId, aiEmployeeId, userId, question) {
    const response = await fetch('/api/chat/stream', {
        method: 'POST',
        body: new FormData(Object.assign(new FormData(), {
            organization_id: organizationId,
            ai_employee_id: aiEmployeeId,
            user_id: userId,
            question: question
        }))
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullAnswer = "";
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const token = line.slice(6);
                fullAnswer += token;
                // Update UI with token (appears in real-time)
                updateChatMessage(fullAnswer);
            }
        }
    }
    
    return fullAnswer;
}
```

═══════════════════════════════════════════════════════════════════════════════

FEATURE #3: SEMANTIC MEMORY SEARCH

Instead of just retrieving last 20 messages, embed conversations and retrieve by semantic similarity.

1. DATABASE SCHEMA:

Add to README SQL:
```sql
-- Conversation embeddings for semantic search
CREATE TABLE conversation_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  ai_employee_id UUID NOT NULL,
  user_id TEXT NOT NULL,
  conversation_id UUID NOT NULL REFERENCES conversations(id),
  embedding VECTOR(1536),
  summary TEXT,  -- Brief summary of conversation
  topics JSONB,  -- ["sales", "pricing", "implementation"]
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_conversation_embeddings_org_agent_user 
  ON conversation_embeddings(organization_id, ai_employee_id, user_id);

-- RPC function for semantic memory search
CREATE OR REPLACE FUNCTION search_memory(
  p_organization_id UUID,
  p_ai_employee_id UUID,
  p_user_id TEXT,
  p_query_embedding VECTOR(1536),
  p_match_count INT DEFAULT 5
) RETURNS TABLE(
  conversation_id UUID,
  summary TEXT,
  topics JSONB,
  similarity FLOAT8
) AS $$
  SELECT
    conversation_id,
    summary,
    topics,
    1 - (embedding <=> p_query_embedding) as similarity
  FROM conversation_embeddings
  WHERE organization_id = p_organization_id
    AND ai_employee_id = p_ai_employee_id
    AND user_id = p_user_id
  ORDER BY embedding <=> p_query_embedding
  LIMIT p_match_count;
$$ LANGUAGE SQL STABLE;
```

2. IMPLEMENT IN db.py:
```python
def embed_conversation(organization_id, ai_employee_id, user_id, conversation_id, conversation_text):
    """Embed a conversation for semantic search"""
    
    # Create embedding
    embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=conversation_text
    )
    embedding = embedding_response.data[0].embedding
    
    # Extract summary and topics using LLM
    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Summarize this conversation in 1-2 sentences:\n{conversation_text}"
        }],
        max_tokens=100
    )
    summary = summary_response.content
    
    topics_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Extract 3-5 key topics from this conversation: {conversation_text}\nRespond as JSON: ['topic1', 'topic2', ...]"
        }],
        max_tokens=100
    )
    topics = json.loads(topics_response.content)
    
    # Store embedding
    response = supabase.table('conversation_embeddings').insert({
        'organization_id': organization_id,
        'ai_employee_id': ai_employee_id,
        'user_id': user_id,
        'conversation_id': conversation_id,
        'embedding': embedding,
        'summary': summary,
        'topics': topics
    }).execute()
    
    return response.data[0] if response.data else None

def search_semantic_memory(organization_id, ai_employee_id, user_id, question):
    """Search memory using semantic similarity"""
    
    # Embed the question
    embedding_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    query_embedding = embedding_response.data[0].embedding
    
    # Search memory using RPC
    response = supabase.rpc(
        'search_memory',
        {
            'p_organization_id': organization_id,
            'p_ai_employee_id': ai_employee_id,
            'p_user_id': user_id,
            'p_query_embedding': query_embedding,
            'p_match_count': 5
        }
    ).execute()
    
    return response.data

def get_semantic_memory_context(organization_id, ai_employee_id, user_id, question):
    """
    Retrieve semantically relevant memories instead of just last N messages.
    This is episodic memory retrieval.
    """
    
    # Get recent memory (last 10 messages)
    recent = get_user_ai_employee_memory(organization_id, ai_employee_id, user_id, limit=10)
    
    # Get semantically relevant memory
    semantic = search_semantic_memory(organization_id, ai_employee_id, user_id, question)
    
    # Combine and deduplicate
    context = {
        "recent_memory": recent,
        "relevant_memory": semantic,
        "topics_discussed": extract_topics(semantic)
    }
    
    return context
```

3. INTEGRATE INTO agent.py:
```python
def answer_question_with_semantic_memory(organization_id, ai_employee_id, user_id, question):
    """Use semantic memory search instead of just recent messages"""
    
    # Get memory using semantic search
    memory_context = get_semantic_memory_context(organization_id, ai_employee_id, user_id, question)
    
    # Build prompt with both recent and relevant memory
    memory_text = f"""
    Recent conversation:
    {format_memory(memory_context['recent_memory'])}
    
    Relevant past discussions:
    {format_memory(memory_context['relevant_memory'])}
    
    Topics previously discussed: {', '.join(memory_context['topics_discussed'])}
    """
    
    # Continue with normal generation using enhanced memory
    ...
```

4. UPDATE UI in index.html:

Show which memory was retrieved:
```javascript
// Display semantic memory retrieval
function displayMemoryRetrieval(relevantMemory) {
    const memoryDiv = document.createElement('div');
    memoryDiv.className = 'memory-context';
    memoryDiv.innerHTML = `
        <details>
            <summary>📚 Retrieved ${relevantMemory.length} relevant memories</summary>
            ${relevantMemory.map(m => `
                <div class="memory-item">
                    <p><strong>${m.summary}</strong></p>
                    <small>Topics: ${m.topics.join(', ')}</small>
                </div>
            `).join('')}
        </details>
    `;
    chatContainer.appendChild(memoryDiv);
}
```

═══════════════════════════════════════════════════════════════════════════════

FEATURE #4: BACKGROUND WORKER QUEUE

Process heavy tasks (embedding, tool execution) asynchronously.

1. INSTALL DEPENDENCIES:

Add to requirements.txt:
redis>=4.0.0
celery>=5.3.0

2. CREATE worker.py:
```python
from celery import Celery
from config import OPENAI_API_KEY
import os

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('supernal', broker=redis_url)

@celery_app.task(name='embed_document')
def embed_document_task(organization_id, document_id, text):
    """Embed a document in background"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        chunks = chunk_text(text)
        
        for chunk in chunks:
            embedding_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            )
            embedding = embedding_response.data[0].embedding
            
            # Save chunk
            save_organization_chunk(organization_id, chunk, embedding, document_id)
        
        return {"status": "success", "chunks_created": len(chunks)}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@celery_app.task(name='embed_conversation')
def embed_conversation_task(organization_id, ai_employee_id, user_id, conversation_id, text):
    """Embed conversation for semantic search in background"""
    try:
        from db import embed_conversation
        result = embed_conversation(organization_id, ai_employee_id, user_id, conversation_id, text)
        return {"status": "success", "embedding_id": str(result['id'])}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@celery_app.task(name='execute_tool_async')
def execute_tool_async(organization_id, ai_employee_id, user_id, tool_name, params):
    """Execute tool in background"""
    try:
        from agent import route_tool_call
        result = route_tool_call(organization_id, ai_employee_id, user_id, tool_name, params)
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
```

3. UPDATE main.py:
```python
from worker import embed_document_task, embed_conversation_task

@app.post("/api/upload-file")
async def upload_file(
    organization_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload file - embedding happens in background"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        contents = await file.read()
        
        # Parse file
        if file.filename.lower().endswith(".pdf"):
            text = extract_pdf_text(contents)
        elif file.filename.lower().endswith((".txt", ".md")):
            text = contents.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Save document metadata
        doc_id = save_organization_document(organization_id, file.filename)
        
        # Queue embedding task (don't wait)
        task = embed_document_task.delay(organization_id, doc_id, text)
        
        return {
            "status": "queued",
            "filename": file.filename,
            "doc_id": doc_id,
            "task_id": task.id,
            "message": "File uploaded. Embedding in progress."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upload-status/{task_id}")
async def get_upload_status(task_id: str):
    """Check status of background embedding task"""
    try:
        from celery.result import AsyncResult
        task = AsyncResult(task_id, app=celery_app)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

4. ENVIRONMENT CONFIG:

Add to .env:
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

═══════════════════════════════════════════════════════════════════════════════

FEATURE #5: OBSERVABILITY & MONITORING

Track all system metrics for production monitoring.

1. ADD OBSERVABILITY TABLES:
```sql
-- API call logs
CREATE TABLE api_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  endpoint TEXT,
  method TEXT,
  status_code INTEGER,
  latency_ms INTEGER,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- LLM call metrics
CREATE TABLE llm_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  ai_employee_id UUID NOT NULL,
  model TEXT,
  prompt_tokens INTEGER,
  completion_tokens INTEGER,
  total_tokens INTEGER,
  latency_ms INTEGER,
  cost_usd DECIMAL,
  created_at TIMESTAMP DEFAULT now()
);

-- Tool execution metrics
CREATE TABLE tool_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  tool_name TEXT,
  status TEXT,
  latency_ms INTEGER,
  error_count INTEGER,
  created_at TIMESTAMP DEFAULT now()
);

-- Error tracking
CREATE TABLE error_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  error_type TEXT,
  error_message TEXT,
  stack_trace TEXT,
  created_at TIMESTAMP DEFAULT now()
);
```

2. IMPLEMENT MONITORING IN main.py:
```python
import time
from datetime import datetime

# Middleware for tracking all requests
@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Track latency and log all API calls"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Log API call
        log_api_call(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            latency_ms=int(process_time)
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        log_error(str(e))
        raise

def log_api_call(endpoint, method, status_code, latency_ms):
    """Log API call to database"""
    try:
        supabase.table('api_logs').insert({
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'latency_ms': latency_ms,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
    except:
        pass  # Don't fail if logging fails

def log_llm_call(organization_id, ai_employee_id, model, tokens_used, latency_ms, cost):
    """Log LLM call metrics"""
    try:
        supabase.table('llm_metrics').insert({
            'organization_id': organization_id,
            'ai_employee_id': ai_employee_id,
            'model': model,
            'prompt_tokens': tokens_used['prompt'],
            'completion_tokens': tokens_used['completion'],
            'total_tokens': tokens_used['total'],
            'latency_ms': latency_ms,
            'cost_usd': cost,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
    except:
        pass

def log_error(error_message, error_type="general", stack_trace=None):
    """Log errors to database"""
    try:
        supabase.table('error_logs').insert({
            'error_type': error_type,
            'error_message': str(error_message),
            'stack_trace': stack_trace,
            'created_at': datetime.utcnow().isoformat()
        }).execute()
    except:
        pass
```

3. CREATE OBSERVABILITY ENDPOINTS:
```python
@app.get("/api/observability/metrics/{organization_id}")
async def get_metrics(organization_id: str):
    """Get observability metrics for an organization"""
    try:
        # Get API metrics
        api_logs = supabase.table('api_logs').select('*').eq('organization_id', organization_id).order('created_at', desc=True).limit(100).execute()
        
        # Get LLM metrics
        llm_metrics = supabase.table('llm_metrics').select('*').eq('organization_id', organization_id).order('created_at', desc=True).limit(100).execute()
        
        # Get error logs
        errors = supabase.table('error_logs').select('*').eq('organization_id', organization_id).order('created_at', desc=True).limit(100).execute()
        
        # Calculate aggregates
        total_requests = len(api_logs.data)
        avg_latency = sum([log['latency_ms'] for log in api_logs.data]) / total_requests if total_requests > 0 else 0
        total_llm_tokens = sum([m['total_tokens'] for m in llm_metrics.data])
        total_cost = sum([m['cost_usd'] for m in llm_metrics.data])
        error_count = len(errors.data)
        
        return {
            "organization_id": organization_id,
            "total_requests": total_requests,
            "avg_latency_ms": round(avg_latency, 2),
            "total_llm_calls": len(llm_metrics.data),
            "total_tokens_used": total_llm_tokens,
            "total_cost_usd": round(total_cost, 2),
            "error_count": error_count,
            "recent_errors": errors.data[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/observability/dashboard/{organization_id}")
async def get_dashboard(organization_id: str):
    """Get full observability dashboard"""
    metrics = get_metrics(organization_id)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
        "health_status": "healthy" if metrics["error_count"] < 10 else "warning",
        "recommendations": get_recommendations(metrics)
    }

def get_recommendations(metrics):
    """Generate recommendations based on metrics"""
    recommendations = []
    
    if metrics["avg_latency_ms"] > 2000:
        recommendations.append("High latency detected. Consider caching frequently accessed documents.")
    
    if metrics["error_count"] > 5:
        recommendations.append(f"High error rate ({metrics['error_count']} errors). Check error logs.")
    
    if metrics["total_cost_usd"] > 100:
        recommendations.append(f"High LLM costs (${metrics['total_cost_usd']}). Consider using cheaper models or longer memory windows.")
    
    return recommendations
```

4. UPDATE UI with Monitoring:

Add monitoring dashboard to index.html:
```html
<div id="monitoring-panel" style="display:none">
    <h3>📊 System Metrics</h3>
    <div class="metrics">
        <div class="metric">
            <label>Avg Latency:</label>
            <span id="avg-latency">--</span> ms
        </div>
        <div class="metric">
            <label>Total Tokens:</label>
            <span id="total-tokens">--</span>
        </div>
        <div class="metric">
            <label>Total Cost:</label>
            <span id="total-cost">$--</span>
        </div>
        <div class="metric">
            <label>Errors:</label>
            <span id="error-count">0</span>
        </div>
    </div>
</div>

<script>
async function updateMetrics() {
    const response = await fetch(`/api/observability/metrics/${organizationId}`);
    const data = await response.json();
    
    document.getElementById('avg-latency').textContent = data.avg_latency_ms.toFixed(0);
    document.getElementById('total-tokens').textContent = data.total_llm_tokens;
    document.getElementById('total-cost').textContent = data.total_cost_usd.toFixed(2);
    document.getElementById('error-count').textContent = data.error_count;
}

// Update metrics every 30 seconds
setInterval(updateMetrics, 30000);
</script>
```

═══════════════════════════════════════════════════════════════════════════════

INTEGRATION CHECKLIST:

After implementing all features, ensure:

☐ Tool calling works (test with send_email, create_ticket)
☐ Streaming responses work (tokens appear in real-time)
☐ Semantic memory retrieval works (relevant memories found)
☐ Background workers queue tasks correctly
☐ Observability dashboard shows metrics
☐ All database tables created with proper indexes
☐ Error handling graceful (fallback to text if streaming fails)
☐ Tool execution logged to database
☐ Memory embeddings generated correctly
☐ Redis/Celery running if using background workers

═══════════════════════════════════════════════════════════════════════════════

DEPLOYMENT NOTES:

For Railway deployment, add environment variables:

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
LANGSMITH_API_KEY=<your_key>

Make sure to:
- Install Redis on Railway
- Enable Celery worker dyno
- Add Redis add-on to Railway project

═══════════════════════════════════════════════════════════════════════════════

TESTING:

Test each feature:

1. Tool Calling:
curl -X POST http://localhost:8000/api/chat \
  -F "organization_id=amazon" \
  -F "ai_employee_id=sales_bot" \
  -F "user_id=ajay" \
  -F "question=Send an email to john@example.com about the proposal"

2. Streaming:
curl -X POST http://localhost:8000/api/chat/stream \
  -F "organization_id=amazon" \
  -F "ai_employee_id=sales_bot" \
  -F "user_id=ajay" \
  -F "question=What were our Q3 sales?"

3. Semantic Memory:
Upload doc → Ask question → Ask about past 3 weeks ago → Should retrieve relevant memory

4. Background Workers:
Upload large file → Should return immediately with task_id → Check /api/upload-status/{task_id}

5. Observability:
curl http://localhost:8000/api/observability/dashboard/amazon

═══════════════════════════════════════════════════════════════════════════════

This implementation transforms your system from a chatbot to a true multi-tenant AI employee platform competitive with enterprise solutions.

Build in this order:
1. Tool calling (most important)
2. Streaming responses (quick wins)
3. Semantic memory (important for intelligence)
4. Background workers (important for scale)
5. Observability (important for production)

All 5 features together = production-grade AI platform ready for Supernal.