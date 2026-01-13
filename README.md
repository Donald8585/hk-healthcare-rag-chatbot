---
title: HK Healthcare RAG Chatbot
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: false
license: mit
short_description: Hong Kong Healthcare RAG chatbot powered by Cohere AI
---
# HK Healthcare RAG Chatbot 🏥

A **production-ready** Retrieval-Augmented Generation (RAG) chatbot built with LangChain, Chroma vector database, and Ollama LLM. Provides intelligent Q&A over Hong Kong healthcare policy documents, statistics, and facility information.

![Architecture](https://img.shields.io/badge/Architecture-RAG-blue) ![Status](https://img.shields.io/badge/Status-Production-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Features

- ✅ **Semantic Search**: Vector-based retrieval using HuggingFace embeddings
- ✅ **Local LLM**: Powered by Ollama (llama3.2:3b) - no API costs
- ✅ **Multi-modal Data**: Processes PDFs, CSVs, and JSON facility data
- ✅ **REST API**: FastAPI backend with interactive Swagger docs
- ✅ **Chat UI**: Streamlit frontend with conversation history
- ✅ **Monitoring**: Built-in metrics, logging, and health checks
- ✅ **Containerized**: Docker support for easy deployment
- ✅ **Cloud-Ready**: GCP Cloud Run deployment scripts included
- ✅ **Source Attribution**: Cites documents used for each answer
- ✅ **Production-Ready**: 616 documents indexed, 1785 semantic chunks

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐
│  Streamlit  │─────▶│   FastAPI    │─────▶│  Chroma VectorDB │
│     UI      │      │   Backend    │      │  (1785 chunks)  │
└─────────────┘      └──────────────┘      └───────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │Ollama LLaMA3.2│
                     │   (3B model) │
                     └──────────────┘
```

**Tech Stack:**
- **Framework**: LangChain 0.3.13
- **Vector DB**: Chroma 0.5.23 (local persistence)
- **Embeddings**: HuggingFace all-MiniLM-L6-v2
- **LLM**: Ollama llama3.2:3b (local)
- **API**: FastAPI 0.115.6
- **Frontend**: Streamlit
- **Deployment**: Docker + GCP Cloud Run
- **Data**: Hospital Authority Reports, HK Gov Open Data

## 📊 Dataset

- **Hospital Authority Annual Report 2023-24** (498KB, 447 pages)
- **Steering Committee Review Report** (351KB)
- **Healthcare Statistics** (doctors, nurses, hospital beds 2015-2024)
- **Facility Data**: 167 hospitals, clinics, and specialist centers
- **Total**: 616 documents → 1785 semantic chunks

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/download) installed
- (Optional) Docker for containerization
- (Optional) GCP account for cloud deployment

### Local Installation

```bash
# 1. Clone repository
git clone https://github.com/Donald8585/hk-healthcare-rag-chatbot.git
cd hk-healthcare-rag-chatbot

# 2. Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# or: source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull Ollama model
ollama pull llama3.2:3b

# 5. Ingest data (first time only - takes ~2 mins)
python ingest_data.py

# 6. Start backend API
uvicorn app:app --port 8000

# 7. Start frontend UI (new terminal)
streamlit run frontend.py
```

**Access the app:**
- Frontend UI: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

### Docker Deployment

```bash
# Build image
docker build -t hk-healthcare-rag .

# Run container
docker run -p 8080:8080 hk-healthcare-rag

# Test
curl http://localhost:8080/health
```

### GCP Cloud Run Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Cloud Run deployment guide.

**Quick deploy:**
```bash
gcloud builds submit --config cloudbuild.yaml
```

**Estimated cost**: ~$13/month for 1000 queries/day (scales to $0 when idle!)

## 📝 Usage Examples

### Web UI (Streamlit)
1. Open http://localhost:8501
2. Type your question in the chat input
3. View answer with source citations

### API (FastAPI)

```bash
# Query endpoint
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many doctors per 1000 population in Hong Kong in 2024?"}'

# Response
{
  "answer": "According to the latest data from Table 1, in 2024 there were 2.2 registered doctors per 1,000 population in Hong Kong...",
  "sources": ["data/healthstat_table1.csv"],
  "latency_seconds": 3.45
}

# Health check
curl http://localhost:8000/health

# Metrics dashboard
curl http://localhost:8000/metrics
```

### Python SDK

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What is the life expectancy in Hong Kong?"}
)

data = response.json()
print(data["answer"])
print("Sources:", data["sources"])
```

## 🎓 Example Questions

- "How many doctors per 1000 population in Hong Kong?"
- "What are the life expectancy rates for males and females?"
- "List all hospitals in Kowloon district"
- "Explain Hospital Authority's governance structure"
- "What is the total fertility rate trend from 2015-2024?"
- "How many registered nurses work in Hong Kong?"

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| **Ingestion Time** | ~2 minutes (1785 chunks) |
| **Query Latency** | 3-5 seconds (retrieval + generation) |
| **Memory Usage** | ~4GB RAM (vector store + LLM) |
| **Cost** | $0 (fully local) or ~$13/month (Cloud Run) |
| **Accuracy** | High (retrieves 4 most relevant chunks) |
| **Documents** | 616 source documents indexed |

## 🔧 Configuration

### Adjust Retrieval Settings

In `app.py`, modify:
```python
docs = vectorstore.similarity_search(query.question, k=4)  # Change k for more/fewer docs
```

### Change LLM Model

```python
llm = Ollama(model="llama3.2:3b", temperature=0.3)  # Try: llama3.1:8b, mistral:7b
```

### Adjust Chunking

In `ingest_data.py`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Increase for more context
    chunk_overlap=200  # Increase for better coherence
)
```

## 🛠️ Project Structure

```
hk-healthcare-rag-chatbot/
├── app.py                  # FastAPI backend with monitoring
├── frontend.py             # Streamlit chat UI
├── ingest_data.py          # Data ingestion script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── cloudbuild.yaml         # GCP Cloud Build config
├── DEPLOYMENT.md           # Cloud deployment guide
├── README.md               # This file
├── data/                   # Source documents
│   ├── en_full_report.pdf
│   ├── HA_Annual_Report_2023-24_en.pdf
│   ├── healthstat_table1.csv
│   ├── healthstat_table2.csv
│   ├── facility-hosp.json
│   ├── facility-fmc.json
│   └── facility-sop.json
└── chroma_db/              # Vector database (generated)
```

## 🔍 Key Learnings

- **RAG Pipeline**: Document ingestion → chunking → embedding → retrieval → generation
- **Vector Search**: Semantic similarity beats keyword matching for complex queries
- **Local-First Architecture**: Zero cloud dependencies, unlimited queries, no API costs
- **Production Patterns**: Error handling, source attribution, monitoring, logging
- **MLOps**: Docker containerization, cloud deployment, auto-scaling

## 🚧 Future Enhancements

- [ ] Multi-language support (Chinese/English bilingual)
- [ ] Hybrid search (vector + keyword BM25)
- [ ] Query caching for common questions
- [ ] A/B testing different LLMs
- [ ] User feedback collection
- [ ] Advanced analytics dashboard
- [ ] API rate limiting
- [ ] Authentication/authorization

## 🐛 Troubleshooting

**Issue**: Ollama not found
```bash
# Install Ollama: https://ollama.com/download
ollama pull llama3.2:3b
```

**Issue**: Port 8000 already in use
```bash
uvicorn app:app --port 8001  # Use different port
```

**Issue**: Out of memory
```bash
# Use smaller model
ollama pull llama3.2:1b
```

**Issue**: Slow responses
- Reduce retrieval count: `k=2` instead of `k=4`
- Use faster model: `llama3.2:3b` instead of larger models
- Add SSD for faster vector DB access

## 📄 License

MIT License - See LICENSE file

## 🏆 Built With

This project demonstrates:
- ✅ End-to-end MLOps pipeline
- ✅ Production RAG architecture
- ✅ Hong Kong healthcare domain expertise
- ✅ API design best practices
- ✅ Cloud-native deployment
- ✅ Real-world data engineering

---

**Author**: Alfred So  
**LinkedIn**: [linkedin.com/in/alfred-so](https://www.linkedin.com/in/alfred-so/)  
**GitHub**: [github.com/Donald8585](https://github.com/Donald8585/)  
**Email**: fiverrkroft@gmail.com

**Date**: January 8, 2026

**Certifications**:
- Google Cloud Machine Learning Engineer (Jan 2026)
- Databricks Certified Machine Learning Professional (Jan 2026)
- AWS Certified Machine Learning – Specialty
- Microsoft Certified: Azure AI Engineer Associate
- Google Data Analytics Professional
- IBM Data Science Professional
- DeepLearning.AI TensorFlow Developer

---

⭐ **Star this repo** if you find it useful!  
🐛 **Report issues** at [GitHub Issues](https://github.com/Donald8585/hk-healthcare-rag-chatbot/issues)  
🤝 **Contribute** via Pull Requests
