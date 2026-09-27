"""HITL (Human-in-the-Loop) UI for Deep Agents."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class ApprovalRecord(BaseModel):
    """Approval record for HITL."""
    
    id: str
    session_id: str
    tool_call_id: str
    tool_name: str
    tool_args: Dict
    approval_status: str  # "pending", "approved", "rejected"
    approved_by: Optional[str] = None
    timestamp: str


class PlanView(BaseModel):
    """Plan view for agent execution."""
    
    plan_id: str
    session_id: str
    steps: List[Dict]
    status: str  # "planning", "executing", "completed", "interrupted"


class SpecDiff(BaseModel):
    """Specification diff."""
    
    before: Dict
    after: Dict
    changes: List[Dict]


class HITLUI:
    """HITL UI service for Deep Agents."""
    
    def __init__(self):
        self._approvals: Dict[str, ApprovalRecord] = {}
        self._plans: Dict[str, PlanView] = {}
    
    async def record_approval(
        self,
        session_id: str,
        tool_call_id: str,
        tool_name: str,
        tool_args: Dict,
    ) -> ApprovalRecord:
        """Record an approval request."""
        approval = ApprovalRecord(
            id=f"{session_id}-{tool_call_id}",
            session_id=session_id,
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            tool_args=tool_args,
            approval_status="pending",
            timestamp="2026-09-27T00:00:00Z",
        )
        
        self._approvals[approval.id] = approval
        return approval
    
    async def approve(self, approval_id: str, approved_by: str) -> bool:
        """Approve a tool call."""
        if approval_id not in self._approvals:
            return False
        
        approval = self._approvals[approval_id]
        approval.approval_status = "approved"
        approval.approved_by = approved_by
        return True
    
    async def reject(self, approval_id: str, approved_by: str) -> bool:
        """Reject a tool call."""
        if approval_id not in self._approvals:
            return False
        
        approval = self._approvals[approval_id]
        approval.approval_status = "rejected"
        approval.approved_by = approved_by
        return True
    
    async def create_plan(self, session_id: str, plan: Dict) -> PlanView:
        """Create a plan view."""
        plan_view = PlanView(
            plan_id=f"{session_id}-plan-{len(self._plans)}",
            session_id=session_id,
            steps=plan.get("steps", []),
            status="planning",
        )
        
        self._plans[plan_view.plan_id] = plan_view
        return plan_view
    
    async def get_approval(self, approval_id: str) -> Optional[ApprovalRecord]:
        """Get approval record."""
        return self._approvals.get(approval_id)
    
    async def get_plan(self, plan_id: str) -> Optional[PlanView]:
        """Get plan view."""
        return self._plans.get(plan_id)


# Global HITL UI instance
hitl_ui = HITLUI()
