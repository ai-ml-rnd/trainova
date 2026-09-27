"""Quotas and chargeback for tenants."""

from typing import Dict, Optional
from pydantic import BaseModel


class Quota(BaseModel):
    """Tenant quota."""
    
    tokens_per_month: int = 1000000
    gpu_hours_per_month: int = 100
    storage_gb: int = 100


class ChargebackRecord(BaseModel):
    """Chargeback record."""
    
    tenant_id: str
    period: str  # YYYY-MM
    tokens_used: int
    gpu_hours_used: float
    storage_used_gb: float
    total_cost: float


class ChargebackManager:
    """Manager for quotas and chargeback."""
    
    def __init__(self):
        self._quotas: Dict[str, Quota] = {}
        self._usage: Dict[str, Dict] = {}
    
    def set_quota(self, tenant_id: str, quota: Quota) -> None:
        """Set quota for tenant."""
        self._quotas[tenant_id] = quota
    
    def get_quota(self, tenant_id: str) -> Optional[Quota]:
        """Get quota for tenant."""
        return self._quotas.get(tenant_id)
    
    def record_usage(
        self,
        tenant_id: str,
        tokens: int = 0,
        gpu_hours: float = 0.0,
        storage_gb: float = 0.0,
    ) -> None:
        """Record usage for tenant."""
        if tenant_id not in self._usage:
            self._usage[tenant_id] = {
                "tokens": 0,
                "gpu_hours": 0.0,
                "storage_gb": 0.0,
            }
        
        self._usage[tenant_id]["tokens"] += tokens
        self._usage[tenant_id]["gpu_hours"] += gpu_hours
        self._usage[tenant_id]["storage_gb"] += storage_gb
    
    def get_chargeback(self, tenant_id: str, period: str) -> ChargebackRecord:
        """Get chargeback record for tenant."""
        usage = self._usage.get(tenant_id, {})
        quota = self._quotas.get(tenant_id)
        
        # Calculate cost (placeholder rates)
        token_cost = usage.get("tokens", 0) * 0.000001
        gpu_cost = usage.get("gpu_hours", 0) * 1.0
        storage_cost = usage.get("storage_gb", 0) * 0.10
        
        return ChargebackRecord(
            tenant_id=tenant_id,
            period=period,
            tokens_used=usage.get("tokens", 0),
            gpu_hours_used=usage.get("gpu_hours", 0),
            storage_used_gb=usage.get("storage_gb", 0),
            total_cost=token_cost + gpu_cost + storage_cost,
        )
    
    def check_quota(self, tenant_id: str) -> bool:
        """Check if tenant is within quota."""
        usage = self._usage.get(tenant_id, {})
        quota = self._quotas.get(tenant_id)
        
        if not quota:
            return True
        
        return (
            usage.get("tokens", 0) <= quota.tokens_per_month and
            usage.get("gpu_hours", 0) <= quota.gpu_hours_per_month and
            usage.get("storage_gb", 0) <= quota.storage_gb
        )


def calculate_chargeback(tenant_id: str, period: str) -> Dict:
    """Calculate chargeback for tenant.
    
    Expected: report per tenant per month
    """
    manager = ChargebackManager()
    record = manager.get_chargeback(tenant_id, period)
    
    return {
        "tenant_id": record.tenant_id,
        "period": record.period,
        "tokens_used": record.tokens_used,
        "gpu_hours_used": record.gpu_hours_used,
        "storage_used_gb": record.storage_used_gb,
        "total_cost": record.total_cost,
    }
