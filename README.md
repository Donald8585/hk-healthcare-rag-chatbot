# HK Healthcare RAG Chatbot 🏥

A production-ready Retrieval-Augmented Generation (RAG) chatbot built with LangChain, Chroma vector database, and Ollama LLM. Provides intelligent Q&A over Hong Kong healthcare policy documents, statistics, and facility information.

## 🎯 Features

- **Semantic Search**: Vector-based retrieval using HuggingFace embeddings
- **Local LLM**: Powered by Ollama (llama3.2:3b) - no API costs
- **Multi-modal Data**: Processes PDFs, CSVs, and JSON facility data
- **REST API**: FastAPI backend with interactive Swagger docs
- **Source Attribution**: Cites documents used for each answer
- **Production-Ready**: 616 documents indexed, 1785 semantic chunks

## 🏗️ Architecture

```
User Query → FastAPI Endpoint → Vector Store (Chroma) → LLM (Ollama) → Response
```

**Tech Stack:**
- **Framework**: LangChain
- **Vector DB**: Chroma (local persistence)
- **Embeddings**: HuggingFace all-MiniLM-L6-v2
- **LLM**: Ollama llama3.2:3b
- **API**: FastAPI
- **Data**: Hospital Authority Reports, HK Gov Open Data

## 📊 Dataset

- **Hospital Authority Annual Report 2023-24** (498KB, 447 pages)
- **Steering Committee Review Report** (351KB)
- **Healthcare Statistics** (doctors, nurses, hospital beds 2015-2024)
- **Facility Data**: 167 hospitals, clinics, and specialist centers

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/download) installed

### Installation

1. Clone repository:
```bash
git clone https://github.com/Donald8585/hk-healthcare-rag-chatbot.git
cd hk-healthcare-rag-chatbot
```

2. Install dependencies:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
```

3. Pull Ollama model:
```bash
ollama pull llama3.2:3b
```

4. Ingest data (first time only):
```bash
python ingest_data.py
```

5. Start API server:
```bash
uvicorn app:app --port 8000
```

6. Access interactive docs: http://localhost:8000/docs

## 📝 Usage

**API Example:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many doctors per 1000 population in Hong Kong?"}'
```

**Response:**
```json
{
  "answer": "According to the data, in 2024 there were 2.2 registered doctors per 1,000 population in Hong Kong...",
  "sources": ["data/healthstat_table1.csv", "data/HA_Annual_Report_2023-24_en.pdf"]
}
```

## 🎓 Key Learnings

- **RAG Pipeline**: Document ingestion → chunking → embedding → retrieval → generation
- **Vector Search**: Semantic similarity vs keyword matching
- **Local-First**: Zero cloud dependencies, unlimited queries
- **Production Patterns**: Error handling, source attribution, API design

## 🛠️ Future Enhancements

- [ ] Streamlit chat UI
- [ ] Docker containerization
- [ ] GCP Cloud Run deployment
- [ ] Query logging and analytics
- [ ] Multi-language support (Chinese/English)
- [ ] A/B testing different LLMs

## 📈 Performance

- **Ingestion**: 1785 chunks in ~2 minutes
- **Query Latency**: ~3-5 seconds (includes retrieval + generation)
- **Memory**: ~4GB RAM (vector store + LLM)
- **Cost**: $0 (fully local)

## 🏆 Built With

This project demonstrates:
- End-to-end MLOps pipeline
- Production RAG architecture
- Hong Kong healthcare domain knowledge
- API design best practices

---

**Author**: Alfred So ([LinkedIn](https://www.linkedin.com/in/alfred-so/) | [GitHub](https://github.com/Donald8585/))

**Date**: January 8, 2026

**Certifications**: Google Cloud ML Engineer, AWS ML Specialty, Azure AI Engineer, Databricks ML Professional
