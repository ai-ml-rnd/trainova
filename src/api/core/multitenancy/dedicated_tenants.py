"""Dedicated namespace/DB tenants."""

from typing import Dict, Optional
from pydantic import BaseModel


class Tenant(BaseModel):
    """Tenant configuration."""
    
    id: str
    namespace: str
    database: str
    tier: str  # "free", "basic", "pro", "enterprise"


class TenantManager:
    """Manager for dedicated tenants."""
    
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}
    
    def create_tenant(
        self,
        tenant_id: str,
        tier: str = "basic",
    ) -> Tenant:
        """Create a dedicated tenant."""
        tenant = Tenant(
            id=tenant_id,
            namespace=f"tenant-{tenant_id}",
            database=f"tenant_{tenant_id}_db",
            tier=tier,
        )
        
        self._tenants[tenant_id] = tenant
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self._tenants.get(tenant_id)
    
    def list_tenants(self) -> Dict[str, Tenant]:
        """List all tenants."""
        return self._tenants


def create_dedicated_tenant(tenant_id: str, tier: str = "basic") -> Dict:
    """Create a dedicated tenant.
    
    Expected: dedicated namespace and DB per tenant
    """
    manager = TenantManager()
    tenant = manager.create_tenant(tenant_id, tier)
    
    return {
        "namespace": tenant.namespace,
        "database": tenant.database,
        "tier": tenant.tier,
    }
