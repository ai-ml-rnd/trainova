"""LangGraph steps for pipeline execution."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.outputs import ChatGeneration, Generation


class Step(ABC):
    """Base step class."""

    name: str
    config: Dict[str, Any]

    @abstractmethod
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the step."""
        pass


class Task(Step):
    """LLM task step."""

    def __init__(
        self,
        name: str,
        prompt_template: str,
        model_route: str = "gen-default",
        output_schema: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.prompt_template = prompt_template
        self.model_route = model_route
        self.output_schema = output_schema

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the task with LLM."""
        # TODO: Implement LLM call via LiteLLM
        # TODO: Use guided decoding for JSON schema

        # Create prompt
        prompt = ChatPromptTemplate.from_template(self.prompt_template)
        prompt_value = prompt.format(**state)

        # Call LLM (placeholder)
        response = {"output": f"Task {self.name} output"}

        # Validate against schema if provided
        if self.output_schema:
            response = self._validate_output(response, self.output_schema)

        return response

    def _validate_output(
        self, output: Dict[str, Any], schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate output against JSON schema."""
        # TODO: Implement JSON schema validation
        return output


class Combine(Step):
    """Combine step for merging multiple outputs."""

    def __init__(
        self,
        name: str,
        combine_type: str = "concat",
        field: str = "output",
    ):
        self.name = name
        self.combine_type = combine_type
        self.field = field

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple outputs."""
        outputs = state.get(self.field, [])

        if self.combine_type == "concat":
            combined = " ".join(str(o) for o in outputs)
        elif self.combine_type == "merge":
            combined = {f"item_{i}": o for i, o in enumerate(outputs)}
        else:
            combined = outputs

        return {self.field: combined}


class Validator(Step):
    """Validator step."""

    def __init__(
        self,
        name: str,
        validation_type: str = "python",
        code: Optional[str] = None,
    ):
        self.name = name
        self.validation_type = validation_type
        self.code = code

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the output."""
        output = state.get("output", "")

        if self.validation_type == "python":
            if self.code:
                # Execute validation code
                result = eval(self.code, {"output": output})
            else:
                result = output is not None and len(output) > 0
        else:
            result = True

        return {"validated": result, "output": output}
