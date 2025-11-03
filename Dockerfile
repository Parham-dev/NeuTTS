FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (espeak-ng is the package name in Debian)
RUN apt-get update && apt-get install -y \
    espeak-ng \
    libsndfile1 \
    build-essential \
    cmake \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Verify espeak-ng is installed
RUN which espeak-ng && espeak-ng --version

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn python-multipart onnxruntime

# Install llama-cpp-python (needs build tools)
RUN pip install --no-cache-dir llama-cpp-python

# Copy application code
COPY . .

# Create directories
RUN mkdir -p output samples

# Expose port
EXPOSE 8001

# Run server
CMD ["python", "run_server.py"]
