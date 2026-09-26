"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

# Configure Sentry if in production
if settings.is_production:
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=settings.environment,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request timing."""

    async def dispatch(self, request, call_next):
        import time

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    if settings.otel_enabled:
        FastAPIInstrumentor().instrument_app(app)

    yield

    # Shutdown
    if settings.otel_enabled:
        FastAPIInstrumentor().uninstrument()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Forge API - Unified Data Platform for LLM & VLM Training",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/health/db", tags=["health"])
async def database_health():
    """Database connectivity check."""
    try:
        from app.dependencies import get_db

        db = next(get_db())
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": str(e)},
        )


@app.get("/health/redis", tags=["health"])
async def redis_health():
    """Redis connectivity check."""
    try:
        import valkey

        r = valkey.from_url(settings.redis_url)
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "redis": str(e)},
        )


@app.get("/health/llm", tags=["health"])
async def llm_health():
    """LLM gateway connectivity check."""
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.litellm_url}/health",
                timeout=settings.litellm_timeout,
            )
            response.raise_for_status()
            return {"status": "healthy", "llm": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "llm": str(e)},
        )


# Import and include routers
from api.v1 import router as v1_router

app.include_router(v1_router, prefix="/v1", tags=["v1"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_debug,
    )
