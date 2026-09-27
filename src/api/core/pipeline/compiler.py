"""Pipeline compiler to LangGraph."""

from typing import Dict, List, Optional
from langgraph.graph import StateGraph, END

from core.pipeline.spec import PipelineSpec, PipelineStep


class PipelineCompiler:
    """Compile pipeline spec to LangGraph."""
    
    def __init__(self):
        self.graph = None
        self.nodes = {}
    
    def compile(self, spec: PipelineSpec) -> StateGraph:
        """Compile pipeline spec to LangGraph StateGraph.
        
        Args:
            spec: Pipeline specification
            
        Returns:
            Compiled StateGraph
        """
        # Create state schema
        state_schema = self._create_state_schema(spec)
        
        # Create graph
        self.graph = StateGraph(state_schema)
        
        # Add nodes for each step
        for step in spec.steps:
            self._add_node(step)
        
        # Add edges
        self._add_edges(spec.steps)
        
        # Set entry point
        self.graph.set_entry_point(spec.steps[0].name)
        
        return self.graph
    
    def _create_state_schema(self, spec: PipelineSpec) -> Dict:
        """Create state schema from pipeline spec."""
        # For MVP, simple state with records and metadata
        return {
            "records": List[Dict],
            "metadata": Dict,
            "errors": List[Dict],
        }
    
    def _add_node(self, step: PipelineStep) -> None:
        """Add a node for a pipeline step."""
        
        async def node_func(state):
            # Process step
            records = state.get("records", [])
            result = await self._process_step(step, records)
            state["records"] = result
            return state
        
        self.graph.add_node(step.name, node_func)
        self.nodes[step.name] = step
    
    def _add_edges(self, steps: List[PipelineStep]) -> None:
        """Add edges between steps."""
        for i in range(len(steps) - 1):
            self.graph.add_edge(steps[i].name, steps[i + 1].name)
        
        # Add final edge to END
        self.graph.add_edge(steps[-1].name, END)
    
    async def _process_step(self, step: PipelineStep, records: List[Dict]) -> List[Dict]:
        """Process a single step."""
        # For MVP, return records unchanged
        # In production, this would execute the step logic
        return records


def compile_pipeline(spec: PipelineSpec) -> StateGraph:
    """Compile a pipeline spec to LangGraph."""
    compiler = PipelineCompiler()
    return compiler.compile(spec)
