"""LangGraph pipeline runner."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from langgraph.checkpointer import PostgresSaver
from langgraph.graph import StateGraph

from app.config import settings
from services.langgraph.compiler import PipelineCompiler
from services.langgraph.steps import Task


class PipelineRunner:
    """Runner for LangGraph pipelines."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.graph: Optional[StateGraph] = None
        self.checkpointer: Optional[PostgresSaver] = None

    async def initialize(self, spec: Dict[str, Any]) -> None:
        """Initialize runner with pipeline spec."""
        # Compile spec to graph
        compiler = PipelineCompiler()
        self.graph = compiler.compile(spec)

        # Set up checkpointer
        self.checkpointer = PostgresSaver.from_conn_string(settings.database_url)

    async def preview(self, input: Dict[str, Any], max_rows: int = 50) -> Dict[str, Any]:
        """Preview pipeline execution on a small batch."""
        if self.graph is None:
            raise ValueError("Runner not initialized")

        # TODO: Get subset of data
        input_batch = {**input, "batch_size": min(len(input.get("records", [])), max_rows)}

        # Run graph
        config = {"configurable": {"thread_id": self.run_id}}
        final_state = await self.graph.astream_events(input_batch, version="v1", config=config)

        return {"state": final_state, "max_rows": max_rows}

    async def run(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Run the full pipeline."""
        if self.graph is None:
            raise ValueError("Runner not initialized")

        # Run graph with checkpointer
        config = {"configurable": {"thread_id": self.run_id}}

        async for event in self.graph.astream_events(input, version="v1", config=config):
            # Stream events
            yield event

        # Return final state
        async with self.checkpointer.get_connection() as conn:
            final_state = await self.checkpointer.get_tuple(conn, self.run_id)
            return {"state": final_state[2] if final_state else {}}


async def preview_pipeline(
    spec: Dict[str, Any], input: Dict[str, Any], max_rows: int = 50
) -> Dict[str, Any]:
    """Preview a pipeline on a small batch."""
    runner = PipelineRunner(run_id="preview")
    await runner.initialize(spec)
    return await runner.preview(input, max_rows)


async def run_pipeline(
    spec: Dict[str, Any], input: Dict[str, Any], run_id: str
) -> Dict[str, Any]:
    """Run a pipeline."""
    runner = PipelineRunner(run_id=run_id)
    await runner.initialize(spec)

    final_state = None
    async for event in runner.run(input):
        # Process event
        pass

    return {"status": "completed", "run_id": run_id}
