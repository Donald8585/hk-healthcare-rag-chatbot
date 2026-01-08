import os
import logging
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HK Healthcare RAG Chatbot",
    description="Production RAG system for Hong Kong healthcare data",
    version="1.0.0"
)

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics storage
query_metrics = {
    "total_queries": 0,
    "total_latency": 0.0,
    "errors": 0,
    "start_time": datetime.now().isoformat()
}

# Load vector store
logger.info("Loading vector store...")
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
    logger.info("✅ Vector store loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load vector store: {e}")
    raise

# Initialize LLM
try:
    llm = Ollama(model="llama3.2:3b", temperature=0.3)
    logger.info("✅ LLM initialized successfully!")
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    raise

class Query(BaseModel):
    question: str

@app.post("/query")
async def query_documents(query: Query):
    start_time = time.time()
    query_metrics["total_queries"] += 1

    logger.info(f"Received query: {query.question[:100]}...")

    try:
        # Retrieve documents
        docs = vectorstore.similarity_search(query.question, k=4)
        logger.info(f"Retrieved {len(docs)} documents")

        # Build context
        context = "\n\n".join([doc.page_content for doc in docs])

        # Create prompt
        prompt = f"""You are a helpful AI assistant specializing in Hong Kong healthcare policy.
Use the following context to answer the question. If you don't know, say so.

Context:
{context}

Question: {query.question}

Answer:"""

        # Get LLM response
        answer = llm.invoke(prompt)

        # Calculate latency
        latency = time.time() - start_time
        query_metrics["total_latency"] += latency

        logger.info(f"Query completed in {latency:.2f}s")

        return {
            "answer": answer,
            "sources": [doc.metadata.get("source", "unknown") for doc in docs],
            "latency_seconds": round(latency, 2)
        }

    except Exception as e:
        query_metrics["errors"] += 1
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "HK Healthcare RAG API is running! 🏥",
        "docs": "/docs",
        "metrics": "/metrics"
    }

@app.get("/health")
async def health():
    try:
        doc_count = vectorstore._collection.count()
        return {
            "status": "healthy",
            "documents": doc_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def metrics():
    avg_latency = (
        query_metrics["total_latency"] / query_metrics["total_queries"] 
        if query_metrics["total_queries"] > 0 else 0
    )

    return {
        "total_queries": query_metrics["total_queries"],
        "total_errors": query_metrics["errors"],
        "average_latency_seconds": round(avg_latency, 2),
        "uptime_since": query_metrics["start_time"],
        "error_rate": (
            round(query_metrics["errors"] / query_metrics["total_queries"] * 100, 2)
            if query_metrics["total_queries"] > 0 else 0
        )
    }
