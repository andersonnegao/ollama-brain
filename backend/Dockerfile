FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama (for standalone deployment)
RUN curl -fsSL https://ollama.ai/install.sh | sh || true

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start Ollama in background and FastAPI in foreground
CMD ["/bin/bash", "-c", "ollama serve &>/dev/null & sleep 5 && (ollama pull ${OLLAMA_MODEL:-mistral:latest} &>/dev/null &) && python -m uvicorn api:app --host 0.0.0.0 --port 8080"]
