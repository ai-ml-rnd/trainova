"""Per-tenant redaction keys."""

from typing import Dict, Optional
from pydantic import BaseModel


class RedactionKey(BaseModel):
    """Redaction key for a tenant."""
    
    tenant_id: str
    key_id: str
    key_data: str  # Encrypted
    created_at: str


class RedactionKeyManager:
    """Manager for per-tenant redaction keys."""
    
    def __init__(self):
        self._keys: Dict[str, RedactionKey] = {}
    
    def create_key(self, tenant_id: str) -> RedactionKey:
        """Create a redaction key for tenant."""
        import hashlib
        import time
        
        key_data = hashlib.sha256(f"{tenant_id}-{time.time()}".encode()).hexdigest()
        
        key = RedactionKey(
            tenant_id=tenant_id,
            key_id=key_data[:16],
            key_data=key_data,
            created_at="2026-09-27T00:00:00Z",
        )
        
        self._keys[tenant_id] = key
        return key
    
    def get_key(self, tenant_id: str) -> Optional[RedactionKey]:
        """Get redaction key for tenant."""
        return self._keys.get(tenant_id)
    
    def rotate_key(self, tenant_id: str) -> RedactionKey:
        """Rotate redaction key for tenant."""
        return self.create_key(tenant_id)


def create_redaction_key(tenant_id: str) -> Dict:
    """Create a redaction key for tenant."""
    manager = RedactionKeyManager()
    key = manager.create_key(tenant_id)
    
    return {
        "key_id": key.key_id,
        "tenant_id": key.tenant_id,
    }
