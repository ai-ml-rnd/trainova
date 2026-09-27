"""Deep Agent dataset builder service."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class FilesystemPermission(BaseModel):
    """Filesystem permission with deny-by-default."""
    
    tenant_id: str
    session_id: str
    path: str
    can_read: bool = False
    can_write: bool = False


class TypedTool(BaseModel):
    """Typed tool definition."""
    
    name: str
    description: str
    input_schema: Dict
    output_schema: Dict


class AgentSession(BaseModel):
    """Deep Agent session."""
    
    session_id: str
    tenant_id: str
    budget: float
    spent: float = 0.0
    tools: List[TypedTool]
    permissions: List[FilesystemPermission]


class DeepAgentService:
    """Deep Agent dataset builder service."""
    
    def __init__(self):
        self._sessions: Dict[str, AgentSession] = {}
        self._allow_listed_tools = {"read_file", "write_file", "search_web"}
    
    async def create_session(
        self,
        tenant_id: str,
        session_id: str,
        budget: float,
    ) -> AgentSession:
        """Create a new agent session."""
        session = AgentSession(
            session_id=session_id,
            tenant_id=tenant_id,
            budget=budget,
            tools=self._get_default_tools(),
            permissions=self._get_default_permissions(tenant_id, session_id),
        )
        
        self._sessions[session_id] = session
        return session
    
    async def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    async def execute_tool(
        self,
        session_id: str,
        tool_name: str,
        tool_args: Dict,
    ) -> Dict:
        """Execute a tool with permission and budget checks."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Check budget
        if session.spent >= session.budget:
            raise ValueError("Budget exhausted")
        
        # Check tool is allow-listed
        if tool_name not in self._allow_listed_tools:
            raise ValueError(f"Tool not allowed: {tool_name}")
        
        # Check permissions
        if not self._has_permission(session, tool_name, tool_args):
            raise ValueError("Permission denied")
        
        # Execute tool (placeholder)
        result = {"status": "success"}
        
        # Update budget (placeholder cost)
        session.spent += 0.001
        
        return result
    
    def _get_default_tools(self) -> List[TypedTool]:
        """Get default tools for agents."""
        return [
            TypedTool(
                name="read_file",
                description="Read a file from the filesystem",
                input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                output_schema={"type": "string"},
            ),
            TypedTool(
                name="write_file",
                description="Write content to a file",
                input_schema={"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}},
                output_schema={"type": "object"},
            ),
            TypedTool(
                name="search_web",
                description="Search the web for information",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                output_schema={"type": "array"},
            ),
        ]
    
    def _get_default_permissions(self, tenant_id: str, session_id: str) -> List[FilesystemPermission]:
        """Get default permissions for a session."""
        return [
            FilesystemPermission(
                tenant_id=tenant_id,
                session_id=session_id,
                path=f"/data/{tenant_id}/{session_id}",
                can_read=True,
                can_write=True,
            ),
        ]
    
    def _has_permission(self, session: AgentSession, tool_name: str, tool_args: Dict) -> bool:
        """Check if tool execution is permitted."""
        # For MVP, allow all allow-listed tools
        return True
    
    async def close(self):
        """Cleanup resources."""
        self._sessions.clear()


# Global service instance
deep_agent_service = DeepAgentService()
