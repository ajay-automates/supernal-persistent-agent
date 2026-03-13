# 🤖 Supernal Persistent Agent

**Multi-user persistent memory RAG agent with OpenAI integration**

A production-ready FastAPI backend that maintains persistent conversation memory across sessions, supports multiple concurrent users with complete data isolation, and uses vector search for document retrieval.

---

## ✨ Key Features

✅ **Persistent Memory** — Conversations survive server restarts and deployments  
✅ **Multi-User Support** — Complete data isolation per user  
✅ **Vector Search** — Fast semantic document retrieval using pgvector  
✅ **Context-Aware** — Agent references past conversations in responses  
✅ **Document Ingestion** — Support for PDF, TXT, and MD files  
✅ **LangSmith Integration** — Full observability of agent pipeline  
✅ **Production-Ready** — FastAPI async backend, Railway deployable  

---

## 🏗️ Architecture

```
User → FastAPI Server → Agent Pipeline
                           ├── Retrieve Documents (pgvector)
                           ├── Get Conversation Memory (Postgres)
                           └── Generate Answer (GPT-4o-mini)
                                 ↓
                        Supabase Database
                        (conversations, chunks, documents)
```

### Data Flow

1. User sends question with `user_id`
2. System retrieves user's documents using vector similarity
3. Agent fetches user's past conversations from memory
4. GPT-4o-mini generates answer using documents + memory + question
5. Response and new question are saved to persistent memory

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Supabase account (free tier works)
- OpenAI API key
- (Optional) LangSmith account for observability

### 1. Clone and Setup

```bash
git clone https://github.com/ajay-automates/supernal-persistent-agent.git
cd supernal-persistent-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Supabase

**Create a new Supabase project** (free tier is fine)

**Run these SQL commands in Supabase SQL Editor:**

```sql
-- Enable pgvector extension (required for VECTOR type)
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

-- Conversations table
CREATE TABLE conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id),
  role TEXT NOT NULL,  -- 'user' or 'assistant'
  content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT now()
);

-- Documents table
CREATE TABLE documents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id),
  filename TEXT NOT NULL,
  source TEXT,
  uploaded_at TIMESTAMP DEFAULT now()
);

-- Chunks table (with vector embeddings)
CREATE TABLE chunks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id),
  text TEXT NOT NULL,
  embedding VECTOR(1536),
  source TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

-- Vector search RPC function
CREATE OR REPLACE FUNCTION search_chunks(
  p_user_id TEXT,
  p_query_embedding VECTOR(1536),
  p_match_count INT
) RETURNS TABLE(
  id UUID,
  user_id TEXT,
  text TEXT,
  source TEXT,
  similarity FLOAT8
) AS $$
  SELECT
    chunks.id,
    chunks.user_id,
    chunks.text,
    chunks.source,
    1 - (chunks.embedding <=> p_query_embedding) as similarity
  FROM chunks
  WHERE chunks.user_id = p_user_id
  ORDER BY chunks.embedding <=> p_query_embedding
  LIMIT p_match_count;
$$ LANGUAGE SQL;

-- Create indexes for performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_chunks_user_id ON chunks(user_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
```

### 3. Environment Setup

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required environment variables:**

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=optional_langsmith_key  # For observability
PORT=8000
```

### 4. Run Locally

```bash
python main.py
```

Visit: http://localhost:8000

API will be available at: http://localhost:8000

Health check: http://localhost:8000/health

---

## 📡 API Endpoints

### Chat (with persistent memory)
```bash
POST /api/chat
Form data: user_id, question

curl -X POST http://localhost:8000/api/chat \
  -F "user_id=user_123" \
  -F "question=What was I asking about before?"
```

**Response:**
```json
{
  "user_id": "user_123",
  "question": "What was I asking about before?",
  "answer": "You previously asked about...",
  "sources": ["document.pdf"],
  "memory_used": true
}
```

### Upload Text
```bash
POST /api/upload-text
Form data: user_id, text

curl -X POST http://localhost:8000/api/upload-text \
  -F "user_id=user_123" \
  -F "text=Your document content here"
```

### Upload File
```bash
POST /api/upload-file
Form data: user_id, file (PDF/TXT/MD)

curl -X POST http://localhost:8000/api/upload-file \
  -F "user_id=user_123" \
  -F "file=@document.pdf"
```

### Get Conversation Memory
```bash
GET /api/memory?user_id=user_123

curl http://localhost:8000/api/memory?user_id=user_123
```

**Response:**
```json
{
  "memory": [
    {"role": "user", "content": "...", "timestamp": "2026-03-13T..."},
    {"role": "assistant", "content": "...", "timestamp": "2026-03-13T..."}
  ],
  "count": 4
}
```

### Clear Memory
```bash
DELETE /api/memory?user_id=user_123
```

### List Documents
```bash
GET /api/documents?user_id=user_123
```

### Get Statistics
```bash
GET /api/stats?user_id=user_123

curl http://localhost:8000/api/stats?user_id=user_123
```

**Response:**
```json
{
  "conversation_turns": 5,
  "total_messages": 10,
  "documents": 3,
  "chunks": 42
}
```

### Health Check
```bash
GET /health

curl http://localhost:8000/health
```

---

## 🚢 Deploy to Railway

### 1. Push to GitHub
```bash
git add .
git commit -m "Initial commit: persistent agent"
git push origin main
```

### 2. Connect to Railway

1. Go to [Railway.app](https://railway.app)
2. Create new project
3. Connect GitHub repository
4. Railway auto-detects Python
5. Set environment variables in Railway dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `OPENAI_API_KEY`
   - `LANGSMITH_API_KEY` (optional)

### 3. Deploy
Railway automatically deploys on `git push`

---

## 💡 How Persistent Memory Works

### Example: User Returns After a Week

**Day 1, User asks:**
```
Q: "What are the best practices for prompt engineering?"
A: "Based on your document, here are the best practices..."
```
✅ Stored in database

**Day 8, User asks:**
```
Q: "What was I asking about last week?"
A: "Last week you asked about prompt engineering. Here's what we discussed..."
```
✅ Agent retrieves past conversation from Postgres  
✅ Uses context to answer new question

---

## 🔒 Data Isolation

Each user is completely isolated:

- User A's documents → Only searchable by User A
- User A's conversations → Only visible to User A
- User B's documents → Completely separate storage
- Database queries filter by `user_id` automatically

All database operations include `WHERE user_id = ?` to ensure isolation.

---

## 🎯 Design Decisions

| Component | Choice | Why |
|-----------|--------|-----|
| **Framework** | FastAPI | Async, fast, production-ready |
| **Database** | Supabase (PostgreSQL) | Managed, free tier, pgvector support |
| **Embeddings** | OpenAI text-embedding-3-small | Fast, cheap, good quality |
| **LLM** | GPT-4o-mini | Cost-effective, good for RAG |
| **Deployment** | Railway | Simple, free tier, auto-deploys |

---

## 📊 Observability

### With LangSmith (Optional)

If you provide `LANGSMITH_API_KEY`, all agent calls are automatically traced:

1. Each question retrieval
2. Document search
3. Answer generation
4. Memory operations

Visit LangSmith dashboard to see full trace of each request.

---

## 🧪 Testing

### Create Test User with Memory

```bash
# Upload document
curl -X POST http://localhost:8000/api/upload-text \
  -F "user_id=test_user" \
  -F "text=Python is a programming language created in 1991."

# Ask first question
curl -X POST http://localhost:8000/api/chat \
  -F "user_id=test_user" \
  -F "question=When was Python created?"

# Ask question about past
curl -X POST http://localhost:8000/api/chat \
  -F "user_id=test_user" \
  -F "question=What was I asking about before?"

# Check memory
curl http://localhost:8000/api/memory?user_id=test_user
```

### Multi-User Test

```bash
# User A uploads document
curl -X POST http://localhost:8000/api/upload-text \
  -F "user_id=user_a" \
  -F "text=User A's secret document"

# User B tries to access (should not work)
curl http://localhost:8000/api/documents?user_id=user_b
# Returns: [] (empty)

# User A can access
curl http://localhost:8000/api/documents?user_id=user_a
# Returns: [user_a_document]
```

---

## 🐛 Troubleshooting

### "SUPABASE_URL and SUPABASE_KEY required"
- Check `.env` file has correct values
- Don't use quotes: `SUPABASE_URL=https://...` not `SUPABASE_URL="https://..."`

### Vector search returning empty results
- Make sure documents are uploaded
- Check chunks were created: `GET /api/stats?user_id=your_user`
- Verify pgvector extension installed in Supabase

### LangSmith traces not appearing
- Verify `LANGSMITH_API_KEY` is set
- Check LangSmith dashboard project name matches `LANGSMITH_PROJECT`

### OpenAI API errors
- Verify `OPENAI_API_KEY` is valid
- Check you have API credits

---

## 📈 Production Considerations

### Scaling
- Database queries are indexed by `user_id`
- Vector search uses pgvector (efficient)
- Each request is independent (horizontal scaling works)

### Cost
- Supabase free tier: ~1M tokens/month for embeddings
- OpenAI: ~$0.01 per request (gpt-4o-mini)
- Railway: free tier for small projects

### Security
- All data filtered by `user_id`
- No credentials in code (use environment variables)
- Use Railway/Supabase security features

---

## 🤝 Contributing

This project is built for the Supernal AI interview. Feel free to extend:

- Add voice input/output
- Implement conversation summarization
- Add feedback loop for answer quality
- Create UI dashboard

---

## 📄 License

MIT

---

## 🔗 Related Projects

- [AI Voice Agent](https://github.com/ajay-automates/ai-voice-agent) — Real-time voice conversations
- [Agentic RAG Pipeline](https://github.com/ajay-automates/agentic-rag-pipeline) — Retrieval + reasoning
- [Job Application Automator](https://github.com/ajay-automates/job-application-automator) — MCP-based automation

---

**Built for Supernal AI - Persistent multi-user agent infrastructure** 🚀
