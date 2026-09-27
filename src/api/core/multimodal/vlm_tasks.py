"""VLM task definitions."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class VLMTaskType(str, Enum):
    """VLM task types."""
    
    CAPTIONING = "captioning"
    VQA = "vqa"
    PREFERENCE = "preference"
    DETECTION = "detection"


class VLMTask(BaseModel):
    """VLM task specification."""
    
    task_type: VLMTaskType
    image_path: str
    prompt: Optional[str] = None
    regions: Optional[List[Dict]] = None  # For region-grounded tasks


class VLMResponse(BaseModel):
    """VLM response."""
    
    task_id: str
    output: str
    confidence: float
    regions: Optional[List[Dict]] = None


class VLMTaskManager:
    """Manager for VLM tasks."""
    
    def __init__(self, route: str = "vlm-default"):
        self.route = route
        self._client = None
    
    async def _get_client(self):
        """Get LLM client."""
        if self._client is None:
            from core.llm.litellm_client import LiteLLMClient
            self._client = LiteLLMClient()
        return self._client
    
    async def run_task(self, task: VLMTask) -> VLMResponse:
        """Run a VLM task."""
        client = await self._get_client()
        
        # Construct prompt based on task type
        prompt = self._build_prompt(task)
        
        # Call VLM
        messages = [
            {"role": "user", "content": prompt},
        ]
        
        response = await client.chat_completion(
            messages=messages,
            model=self.route,
            response_format={"type": "json_object"},
        )
        
        # Parse response
        output = response["choices"][0]["message"]["content"]
        
        return VLMResponse(
            task_id=task.image_path,
            output=output,
            confidence=0.95,  # Placeholder
            regions=task.regions,
        )
    
    def _build_prompt(self, task: VLMTask) -> str:
        """Build prompt for task."""
        if task.task_type == VLMTaskType.CAPTIONING:
            return "Describe this image in detail."
        
        elif task.task_type == VLMTaskType.VQA:
            return f"Answer this question about the image: {task.prompt}"
        
        elif task.task_type == VLMTaskType.PREFERENCE:
            return "Compare these two images and describe which you prefer and why."
        
        elif task.task_type == VLMTaskType.DETECTION:
            return "Detect objects in this image and provide bounding boxes in COCO format."
        
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
    
    async def close(self):
        """Close client."""
        if self._client:
            await self._client.close()
            self._client = None


class VLMJudge(VLMTaskManager):
    """VLM for judgment tasks."""
    
    def __init__(self):
        super().__init__(route="vlm-judge")
    
    async def judge_preference(
        self,
        image1_path: str,
        image2_path: str,
    ) -> Dict:
        """Judge preference between two images."""
        task = VLMTask(
            task_type=VLMTaskType.PREFERENCE,
            image_path=f"{image1_path}|{image2_path}",
        )
        
        response = await self.run_task(task)
        
        return {
            "preferred": "image1" if "image1" in response.output.lower() else "image2",
            "rationale": response.output,
            "confidence": response.confidence,
        }
