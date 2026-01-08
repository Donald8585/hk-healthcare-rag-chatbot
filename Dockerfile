FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY ingest_data.py .
COPY chroma_db ./chroma_db

# Expose port
EXPOSE 8080

# Set environment variables
ENV OLLAMA_HOST=0.0.0.0
ENV PORT=8080

# Start Ollama and pull model in background, then start FastAPI
CMD ollama serve & \
    sleep 5 && \
    ollama pull llama3.2:3b && \
    uvicorn app:app --host 0.0.0.0 --port $PORT
