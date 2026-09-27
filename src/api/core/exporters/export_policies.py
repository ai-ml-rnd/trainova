"""Export policies for dataset exports."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class ExportPolicy(BaseModel):
    """Export policy."""
    
    name: str
    license: Optional[str] = None
    pii_clean: bool = True
    judge_calibration: Optional[float] = None  # Minimum kappa threshold


class ExportPolicyEnforcer:
    """Enforce export policies."""
    
    def __init__(self):
        self._policies: Dict[str, ExportPolicy] = {}
    
    def register_policy(self, policy: ExportPolicy) -> None:
        """Register an export policy."""
        self._policies[policy.name] = policy
    
    def get_policy(self, name: str) -> Optional[ExportPolicy]:
        """Get export policy."""
        return self._policies.get(name)
    
    def enforce(
        self,
        records: List[Dict],
        policy_name: str,
    ) -> List[Dict]:
        """Enforce export policy on records."""
        policy = self._policies.get(policy_name)
        if not policy:
            return records
        
        result = records
        
        # PII cleanup
        if policy.pii_clean:
            result = [r for r in result if not r.get("has_pii", False)]
        
        # Judge calibration filter
        if policy.judge_calibration is not None:
            result = [
                r for r in result
                if r.get("judge_kappa", 0.0) >= policy.judge_calibration
            ]
        
        return result
    
    def check_policy(self, records: List[Dict], policy_name: str) -> Dict:
        """Check if records satisfy policy."""
        policy = self._policies.get(policy_name)
        if not policy:
            return {"satisfied": True}
        
        checks = {}
        
        if policy.pii_clean:
            has_pii = [r for r in records if r.get("has_pii", False)]
            checks["pii_clean"] = len(has_pii) == 0
        
        if policy.judge_calibration is not None:
            calibrated = [
                r for r in records
                if r.get("judge_kappa", 0.0) >= policy.judge_calibration
            ]
            checks["judge_calibration"] = len(calibrated) > 0
        
        return {
            "satisfied": all(checks.values()),
            "checks": checks,
        }


# Global policy enforcer
policy_enforcer = ExportPolicyEnforcer()
