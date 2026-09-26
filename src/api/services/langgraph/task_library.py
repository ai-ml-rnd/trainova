"""Task library for common LLM tasks."""

from typing import Dict, List, Optional

from services.langgraph.steps import Task


class TaskLibrary:
    """Library of pre-defined LLM tasks."""

    @staticmethod
    def get_task(task_type: str, config: Optional[Dict] = None) -> Task:
        """Get a task from the library."""
        config = config or {}

        if task_type == "self_instruct":
            return TaskLibrary._create_self_instruct_task(config)
        elif task_type == "evol_instruct":
            return TaskLibrary._create_evol_instruct_task(config)
        elif task_type == "multi_response":
            return TaskLibrary._create_multi_response_task(config)
        elif task_type == "qa_from_document":
            return TaskLibrary._create_qa_from_document_task(config)
        elif task_type == "chat_simulation":
            return TaskLibrary._create_chat_simulation_task(config)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    @staticmethod
    def list_tasks() -> List[str]:
        """List all available task types."""
        return [
            "self_instruct",
            "evol_instruct",
            "multi_response",
            "qa_from_document",
            "chat_simulation",
        ]

    @staticmethod
    def _create_self_instruct_task(config: Dict) -> Task:
        """Create self-instruct task."""
        return Task(
            name="self_instruct",
            prompt_template=config.get(
                "prompt_template",
                "Generate an instruction that could be completed by a human or AI assistant:\n\n{context}\n\nInstruction:",
            ),
            model_route=config.get("model_route", "gen-default"),
            output_schema=config.get("output_schema", {"type": "string"}),
        )

    @staticmethod
    def _create_evol_instruct_task(config: Dict) -> Task:
        """Create evolution-instruct task."""
        return Task(
            name="evol_instruct",
            prompt_template=config.get(
                "prompt_template",
                "Evolve the following instruction to make it more complex:\n\n{instruction}\n\nEvolved instruction:",
            ),
            model_route=config.get("model_route", "gen-default"),
            output_schema=config.get("output_schema", {"type": "string"}),
        )

    @staticmethod
    def _create_multi_response_task(config: Dict) -> Task:
        """Create multi-response task."""
        return Task(
            name="multi_response",
            prompt_template=config.get(
                "prompt_template",
                "Provide {num_responses} different responses to the following prompt:\n\n{prompt}\n\nResponses (numbered 1-{num_responses}):",
            ),
            model_route=config.get("model_route", "gen-default"),
            output_schema=config.get("output_schema", {"type": "array", "items": {"type": "string"}}),
        )

    @staticmethod
    def _create_qa_from_document_task(config: Dict) -> Task:
        """Create QA-from-document task."""
        return Task(
            name="qa_from_document",
            prompt_template=config.get(
                "prompt_template",
                "Based on the following document, generate a question and answer:\n\n{document}\n\nQuestion:",
            ),
            model_route=config.get("model_route", "gen-default"),
            output_schema=config.get(
                "output_schema",
                {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {"type": "string"},
                    },
                },
            ),
        )

    @staticmethod
    def _create_chat_simulation_task(config: Dict) -> Task:
        """Create chat simulation task."""
        return Task(
            name="chat_simulation",
            prompt_template=config.get(
                "prompt_template",
                "Simulate a conversation between two participants:\n\nContext: {context}\n\nParticipant A:",
            ),
            model_route=config.get("model_route", "gen-default"),
            output_schema=config.get(
                "output_schema",
                {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "enum": ["user", "assistant"]},
                            "content": {"type": "string"},
                        },
                    },
                },
            ),
        )


async def get_task(task_type: str, config: Optional[Dict] = None) -> Task:
    """Get a task from the library."""
    library = TaskLibrary()
    return library.get_task(task_type, config)


async def list_tasks() -> List[str]:
    """List all available task types."""
    return TaskLibrary.list_tasks()
