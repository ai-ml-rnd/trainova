"""Health check endpoints."""

from fastapi import APIRouter

from api.v1.schemas import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health():
    """Basic health check."""
    return HealthResponse(status="healthy", version="0.1.0")


@router.get("/ready", response_model=HealthResponse)
async def ready():
    """Readiness check."""
    return HealthResponse(status="ready", version="0.1.0")
