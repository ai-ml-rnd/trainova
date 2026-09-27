"""Pipeline specification schema."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class PipelineStep(BaseModel):
    """Pipeline step definition."""
    
    name: str
    type: str  # task, loader, combine, validator
    config: Dict[str, Any] = {}


class PipelineSpec(BaseModel):
    """Pipeline specification."""
    
    name: str
    version: str
    description: Optional[str] = None
    steps: List[PipelineStep]
    input_schema: Optional[Dict[str, str]] = None
    output_schema: Optional[Dict[str, str]] = None
