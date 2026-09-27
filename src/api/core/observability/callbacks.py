"""LangChain callbacks for tracing."""

from typing import Dict, Optional
from langchain_core.callbacks import BaseCallbackHandler
from pydantic import BaseModel


class LangfuseCallbackHandler(BaseCallbackHandler, BaseModel):
    """LangChain callback handler for Langfuse."""
    
    langfuse_client = None
    trace_id: Optional[str] = None
    
    def on_chain_start(
        self,
        serialized: Dict[str, str],
        inputs: Dict[str, str],
        **kwargs,
    ) -> None:
        """Called when a chain starts."""
        if self.langfuse_client:
            self.trace_id = self.langfuse_client.trace(
                name=serialized.get("name", "chain"),
                metadata=kwargs,
            )
    
    def on_chain_end(self, outputs: Dict[str, str], **kwargs) -> None:
        """Called when a chain ends."""
        if self.trace_id and self.langfuse_client:
            self.langfuse_client.span(
                trace_id=self.trace_id,
                name="chain_end",
                metadata=kwargs,
            )
    
    def on_llm_start(
        self,
        serialized: Dict[str, str],
        prompts: list,
        **kwargs,
    ) -> None:
        """Called when LLM starts generating."""
        if self.trace_id and self.langfuse_client:
            self.langfuse_client.span(
                trace_id=self.trace_id,
                name="llm_generate",
                metadata={"prompts": len(prompts)},
            )
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM finishes generating."""
        if self.trace_id and self.langfuse_client:
            self.langfuse_client.span(
                trace_id=self.trace_id,
                name="llm_end",
                metadata=kwargs,
            )
