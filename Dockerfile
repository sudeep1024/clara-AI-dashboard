FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for Whisper audio transcription, optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir groq flask

# Copy pipeline code
COPY scripts/ ./scripts/
COPY data/     ./data/

# Create output directories
RUN mkdir -p outputs/accounts changelog workflows

# Default: run the local (zero-cost) batch runner
CMD ["python", "scripts/local_runner.py"]
