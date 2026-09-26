# vLLM CUDA-13 Dockerfile for ARM64 (DGX GB10)
# Based on NGC vLLM 26.02-py3

FROM nvcr.io/nvidia/vllm:v26.02-py3

# Switch to non-root user
USER vllm

# Install additional dependencies
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn==0.32.0 \
    pydantic==2.9.0

# Set environment variables
ENV CUDA_VISIBLE_DEVICES=0
ENV VLLM_HOST_IP=0.0.0.0
ENV VLLM_PORT=8000
ENV VLLM_MODEL_PATH=/models
ENV VLLM_GPU_MEMORY_UTILIZATION=0.85
ENV VLLM_MAX_NUM_SEQS=256
ENV VLLM_PREFIX_CACHING_ENABLED=true

# Create models directory
RUN mkdir -p /models

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run vLLM
CMD ["vllm", "serve", "/models", "--port", "8000", "--host", "0.0.0.0"]
