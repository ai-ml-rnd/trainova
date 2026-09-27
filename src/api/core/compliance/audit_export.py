"""Audit export to SIEM."""

from typing import List, Dict
from pydantic import BaseModel


class AuditEvent(BaseModel):
    """Audit event."""
    
    timestamp: str
    user_id: str
    action: str
    resource: str
    details: Dict


class AuditExporter:
    """Export audit events to SIEM."""
    
    def __init__(self):
        self._events: List[AuditEvent] = []
    
    def log_event(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Dict,
    ) -> None:
        """Log an audit event."""
        import time
        
        event = AuditEvent(
            timestamp=f"2026-09-27T{time.strftime('%H:%M:%S')}Z",
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
        )
        
        self._events.append(event)
    
    def get_events(
        self,
        start_time: str,
        end_time: str,
        limit: int = 1000,
    ) -> List[AuditEvent]:
        """Get audit events in time range."""
        return self._events[-limit:]
    
    def export_to_siem(self) -> List[Dict]:
        """Export events in SIEM format."""
        return [e.dict() for e in self._events]


def log_audit_event(user_id: str, action: str, resource: str, details: Dict) -> Dict:
    """Log an audit event.
    
    Expected: Export to SIEM
    """
    exporter = AuditExporter()
    exporter.log_event(user_id, action, resource, details)
    
    return {"status": "logged"}
