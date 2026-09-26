"""VLM (Vision Language Model) service for captioning, VQA, and image-grounded tasks."""

import io
import base64
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel

from app.config import settings
from services.litellm_client import get_litellm_client


class VLMTask(BaseModel):
    """VLM task configuration."""

    task_type: str  # "captioning", "vqa", "preference"
    image_url: str
    prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 512


class VLMResponse(BaseModel):
    """VLM response."""

    output: str
    tokens: int
    confidence: float
    metadata: Dict[str, Any]


class VLMService:
    """VLM service for multimodal tasks."""

    def __init__(self):
        self.client = get_litellm_client()
        self.model_route = "vlm-default"

    async def generate_caption(
        self,
        image_url: str,
        temperature: float = 0.7,
    ) -> VLMResponse:
        """Generate a caption for an image."""
        image_data = await self._load_image(image_url)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in a single sentence."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            }
        ]

        response = await self.client.create_completion(
            model=self.model_route,
            messages=messages,
            temperature=temperature,
            max_tokens=100,
        )

        return VLMResponse(
            output=response["choices"][0]["message"]["content"],
            tokens=response["usage"]["total_tokens"],
            confidence=0.9,
            metadata={
                "model_route": self.model_route,
                "prompt_tokens": response["usage"]["prompt_tokens"],
                "completion_tokens": response["usage"]["completion_tokens"],
            },
        )

    async def generate_vqa(
        self,
        image_url: str,
        question: str,
        temperature: float = 0.7,
    ) -> VLMResponse:
        """Generate an answer to a question about an image."""
        image_data = await self._load_image(image_url)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            }
        ]

        response = await self.client.create_completion(
            model=self.model_route,
            messages=messages,
            temperature=temperature,
            max_tokens=100,
        )

        return VLMResponse(
            output=response["choices"][0]["message"]["content"],
            tokens=response["usage"]["total_tokens"],
            confidence=0.9,
            metadata={
                "model_route": self.model_route,
                "prompt_tokens": response["usage"]["prompt_tokens"],
                "completion_tokens": response["usage"]["completion_tokens"],
            },
        )

    async def generate_preference(
        self,
        image_url: str,
        prompt: str,
        responses: List[str],
        temperature: float = 0.7,
    ) -> VLMResponse:
        """Select the best response for an image-grounded prompt."""
        image_data = await self._load_image(image_url)

        choices_text = "\n".join(f"{i+1}. {r}" for i, r in enumerate(responses))

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{prompt}\n\nChoose the best response:\n{choices_text}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            }
        ]

        response = await self.client.create_completion(
            model=self.model_route,
            messages=messages,
            temperature=temperature,
            max_tokens=10,
            response_format={"type": "json_schema", "schema": {
                "type": "object",
                "properties": {
                    "choice": {"type": "integer", "minimum": 1, "maximum": len(responses)},
                    "reason": {"type": "string"},
                },
                "required": ["choice", "reason"],
            }},
        )

        content = response["choices"][0]["message"]["content"]
        result = {"choice": 1, "reason": "Fallback"}  # default
        try:
            import json
            result = json.loads(content)
        except json.JSONDecodeError:
            pass

        return VLMResponse(
            output=responses[result["choice"] - 1],
            tokens=response["usage"]["total_tokens"],
            confidence=0.85,
            metadata={
                "model_route": self.model_route,
                "selected": result["choice"],
                "reason": result.get("reason", ""),
                "prompt_tokens": response["usage"]["prompt_tokens"],
                "completion_tokens": response["usage"]["completion_tokens"],
            },
        )

    async def _load_image(self, image_url: str) -> str:
        """Load image from URL and return base64-encoded JPEG."""
        if image_url.startswith("data:"):
            # Already base64
            return image_url.split(",")[1] if "," in image_url else image_url.split("base64,")[1]

        # Download image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        # Convert to JPEG
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(response.content))
        if img.mode != "RGB":
            img = img.convert("RGB")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode()

    async def preview_task(
        self,
        task: VLMTask,
        max_rows: int = 5,
    ) -> Dict[str, Any]:
        """Preview VLM task on a small batch."""
        # TODO: Implement batch preview
        return {
            "task_type": task.task_type,
            "image_count": min(max_rows, 5),
            "est_time_seconds": max_rows * 2,
            "est_cost_tokens": max_rows * 200,
        }


# Global instance
_vlm_service: Optional[VLMService] = None


def get_vlm_service() -> VLMService:
    """Get the global VLM service."""
    global _vlm_service
    if _vlm_service is None:
        _vlm_service = VLMService()
    return _vlm_service
