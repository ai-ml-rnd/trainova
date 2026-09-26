"""Application dependencies."""

from contextlib import contextmanager
from typing import Generator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Database
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def get_db() -> Generator:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_tenant(
    authorization: str = Header(None),
) -> str:
    """Extract tenant ID from token.

    In production, this would decode the JWT and extract the tenant_id claim.
    For now, returns the default tenant for local development.
    """
    if not authorization:
        return settings.default_tenant_id

    # In production, decode token and extract tenant
    # tenant_id = decode_token(authorization).get("tenant_id")
    # if not tenant_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token: missing tenant_id",
    #     )
    # return tenant_id

    return settings.default_tenant_id


def require_admin(
    tenant: str = Depends(get_current_tenant),
) -> str:
    """Require admin role for the current tenant."""
    # In production, check if user has admin role
    # if not has_admin_role(tenant):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin role required",
    #     )
    return tenant


# Dependency aliases
db = Depends(get_db)
current_tenant = Depends(get_current_tenant)
admin_required = Depends(require_admin)
