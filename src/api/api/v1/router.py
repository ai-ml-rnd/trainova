"""API v1 router."""

from fastapi import APIRouter

from api.v1.endpoints import health, tenants, datasets, records, import_jobs

router = APIRouter()

# Include sub-routers
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
router.include_router(datasets.router, prefix="/v1/datasets", tags=["datasets"])
router.include_router(records.router, prefix="/v1/records", tags=["records"])
router.include_router(import_jobs.router, prefix="/v1/import-jobs", tags=["import-jobs"])
