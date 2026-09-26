# LiteLLM Dockerfile for ARM64
FROM ghcr.io/berriai/litellm:latest@sha256:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Switch to non-root user
USER litellm

# Install additional dependencies
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    pydantic==2.9.0

# Set environment variables
ENV PORT=4000
ENV HOST=0.0.0.0
ENV DATABASE_URL=postgresql://litellm:password@postgres:5432/litellm
ENV MAX_LLM_REQUESTS=100
ENV MAX_TOKENS=32768
ENV TIMEOUT=60

# Copy configuration
COPY config.yaml /home/litellm/config.yaml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:4000/health || exit 1

# Expose port
EXPOSE 4000

# Run LiteLLM
CMD ["litellm", "--config", "/home/litellm/config.yaml"]
