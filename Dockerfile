# ================================================================
# CADLift Backend - Production Dockerfile (Optimized)
# ================================================================

FROM python:3.11-slim

# Install system dependencies for CAD processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    openscad \
    libglu1-mesa \
    libxrender1 \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy backend code
COPY backend/ ./

# Install Python dependencies (no cache for smaller image)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e .

# Create storage directory
RUN mkdir -p /app/storage

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STORAGE_PATH=/app/storage
ENV LOG_LEVEL=INFO
ENV ENABLE_STABLE_DIFFUSION=false
ENV ENABLE_TRIPOSR=false

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start server with Xvfb for headless OpenSCAD
CMD ["sh", "-c", "xvfb-run -a uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
