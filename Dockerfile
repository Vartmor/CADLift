# ================================================================
# CADLift Backend - Production Dockerfile
# ================================================================

FROM python:3.11-slim

# Install system dependencies for CAD processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    openscad \
    libglu1-mesa \
    libxrender1 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY backend/pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY backend/ ./

# Create storage directory
RUN mkdir -p /app/storage

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV STORAGE_PATH=/app/storage
ENV LOG_LEVEL=INFO

# Expose port
EXPOSE 8000

# Start server with Xvfb for headless OpenSCAD
CMD ["sh", "-c", "xvfb-run -a uvicorn app.main:app --host 0.0.0.0 --port 8000"]
