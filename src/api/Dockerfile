# Forge API Dockerfile
# Multi-arch build: docker buildx build --platform linux/amd64,linux/arm64 -t forge-api .

FROM python:3.12-slim@sha256:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY src/api/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production image
FROM python:3.12-slim@sha256:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Switch to non-root user
RUN groupadd -r forge && useradd -r -g forge forge

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/forge/.local

# Ensure scripts are available
ENV PATH=/home/forge/.local/bin:$PATH

# Copy application
COPY src/api/ /app/

# Create data directories
RUN mkdir -p /app/data && chown forge:forge /app/data

# Switch to non-root user
USER forge

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
