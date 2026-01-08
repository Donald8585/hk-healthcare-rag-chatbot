import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyBhmcNzb2C-mq8U7mhTNMStO4A848knnis"  # Paste new key
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

app = FastAPI(title="HK Healthcare RAG Chatbot")

# Load vector store
print("Loading vector store...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
print("✅ Vector store loaded!")

# Initialize LLM
llm = Ollama(model="llama3.2:3b", temperature=0.3)


class Query(BaseModel):
    question: str

@app.post("/query")
async def query_documents(query: Query):
    # Simple RAG: retrieve docs + format prompt manually
    docs = vectorstore.similarity_search(query.question, k=4)
    
    # Build context from retrieved docs
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

    
    return {
        "answer": answer,
        "sources": [doc.metadata.get("source", "unknown") for doc in docs]
    }

@app.get("/")
async def root():
    return {"message": "HK Healthcare RAG API is running! 🏥"}
