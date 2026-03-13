-- Enable pgvector extension (required for VECTOR type)
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing tables if they have wrong schema (safe for fresh project)
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS users CASCADE;

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
  role TEXT NOT NULL,
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

-- Indexes for performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_chunks_user_id ON chunks(user_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
