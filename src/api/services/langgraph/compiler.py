"""LangGraph pipeline compiler."""

from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END

from services.langgraph.steps import Step, Task, Combine, Validator


class PipelineCompiler:
    """Compile pipeline spec to LangGraph StateGraph."""

    def __init__(self):
        self.graph = None
        self.nodes: Dict[str, Step] = {}
        self.edges: List[tuple] = []

    def compile(self, spec: Dict[str, Any]) -> StateGraph:
        """Compile pipeline spec to LangGraph."""
        # Validate spec
        self._validate_spec(spec)

        # Create graph
        self.graph = StateGraph(dict)

        # Add nodes
        for node_id, node_spec in spec.get("nodes", {}).items():
            step = self._create_step(node_spec)
            self.nodes[node_id] = step
            self.graph.add_node(node_id, step.run)

        # Add edges
        for edge_spec in spec.get("edges", []):
            self._add_edge(edge_spec)

        # Set entry point
        entry_point = spec.get("entry_point", list(self.nodes.keys())[0])
        self.graph.set_entry_point(entry_point)

        return self.graph

    def _validate_spec(self, spec: Dict[str, Any]) -> None:
        """Validate pipeline spec."""
        if "nodes" not in spec:
            raise ValueError("Pipeline spec must have 'nodes'")

        if not spec["nodes"]:
            raise ValueError("Pipeline spec must have at least one node")

        # Check for cycles
        self._check_cycles(spec)

    def _check_cycles(self, spec: Dict[str, Any]) -> None:
        """Check for cycles in pipeline graph."""
        # TODO: Implement cycle detection
        pass

    def _create_step(self, node_spec: Dict[str, Any]) -> Step:
        """Create a step from node spec."""
        node_type = node_spec.get("type", "task")

        if node_type == "task":
            return Task(**node_spec.get("config", {}))
        elif node_type == "combine":
            return Combine(**node_spec.get("config", {}))
        elif node_type == "validator":
            return Validator(**node_spec.get("config", {}))
        else:
            raise ValueError(f"Unknown node type: {node_type}")

    def _add_edge(self, edge_spec: Dict[str, Any]) -> None:
        """Add an edge to the graph."""
        source = edge_spec.get("source")
        target = edge_spec.get("target")

        if source and target:
            self.graph.add_edge(source, target)


async def compile_pipeline(spec: Dict[str, Any]) -> StateGraph:
    """Compile a pipeline spec to LangGraph."""
    compiler = PipelineCompiler()
    return compiler.compile(spec)


async def validate_pipeline_spec(spec: Dict[str, Any]) -> bool:
    """Validate a pipeline spec."""
    compiler = PipelineCompiler()
    try:
        compiler._validate_spec(spec)
        return True
    except ValueError:
        return False
