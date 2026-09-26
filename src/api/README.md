# FastAPI API Skeleton

This directory contains the FastAPI application skeleton for the Forge platform.

## Structure

```
src/api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── dependencies.py      # Dependencies (auth, db, etc.)
│   ├── middleware.py        # Middleware (logging, CORS, etc.)
│   └── health.py            # Health check endpoints
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── endpoints/       # API endpoints
│   │   └── schemas.py       # Pydantic schemas
│   └── __init__.py
├── core/
│   ├── __init__.py
│   ├── exceptions.py        # Custom exceptions
│   ├── security.py          # Security utilities
│   └── utils.py             # Utility functions
├── models/
│   ├── __init__.py
│   ├── base.py              # Base model
│   └── *.py                 # SQLAlchemy models
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── Dockerfile               # API Dockerfile
└── docker-compose.yaml      # Local development
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest
```

## API Design Principles

1. **Intent-named endpoints** - No CRUD passthrough
2. **Tenant from token** - Never from path/body
3. **Versioned** - `/v1/...` routes
4. **Async-first** - All endpoints are async
5. **Typed** - OpenAPI schemas via Pydantic

## Health Endpoints

```python
GET /health          # Basic health check
GET /health/db       # Database connectivity
GET /health/redis    # Redis connectivity
GET /health/llm      # LLM gateway connectivity
```
