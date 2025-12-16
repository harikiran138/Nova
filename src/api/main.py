from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.api.rag import ingest_text, get_qa_chain

from contextlib import asynccontextmanager
from src.agent_core.config import Config
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load config to ensure env vars are set if needed
    Config.from_env()
    # Force tinyllama / all-minilm if not set, for consistency with local tests
    if not os.getenv("OLLAMA_MODEL"):
        os.environ["OLLAMA_MODEL"] = "tinyllama"
    if not os.getenv("OLLAMA_EMBEDDING_MODEL"):
        os.environ["OLLAMA_EMBEDDING_MODEL"] = "all-minilm"
    yield

app = FastAPI(title="Nova Agent RAG API", version="1.0.0", lifespan=lifespan)

class IngestRequest(BaseModel):
    text: str
    source: str = "api_upload"

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest_document(request: IngestRequest):
    try:
        ingest_text(request.text, request.source)
        return {"status": "success", "message": "Document ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_knowledge_base(request: QueryRequest):
    try:
        chain = get_qa_chain()
        result = chain.invoke({"query": request.query})
        
        # Format response
        response = {
            "answer": result["result"],
            "sources": [doc.metadata.get("source", "unknown") for doc in result.get("source_documents", [])]
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
