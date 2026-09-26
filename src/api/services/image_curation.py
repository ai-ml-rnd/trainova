"""Image curation operations: CLIP-score, resolution/aspect, NSFW."""

from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from services.curation.operators import FilterOperator, MapperOperator, OpContext


class CLIPScoreFilter(FilterOperator):
    """Filter images by CLIP similarity score."""

    name = "clip_score_filter"
    version = "1.0"
    kind = "filter"

    def __init__(
        self,
        min_score: float = 0.2,
        reference_text: Optional[str] = None,
    ):
        self.min_score = min_score
        self.reference_text = reference_text
        self._model = None
        self._processor = None

    def _get_model(self):
        if self._model is None:
            self._model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self._processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self._model.eval()
        return self._model, self._processor

    def filter_batch(self, batch: Any, ctx: OpContext) -> Any:
        """Filter images by CLIP score."""
        model, processor = self._get_model()

        # Extract images from batch
        images = self._extract_images(batch)

        # Compute scores
        scores = []
        for img in images:
            if self.reference_text:
                inputs = processor(text=[self.reference_text], images=img, return_tensors="pt", padding=True)
                with torch.no_grad():
                    outputs = model(**inputs)
                    score = outputs.logits_per_image[0].item()
            else:
                # Use empty text for intrinsic quality score
                inputs = processor(text=[""], images=img, return_tensors="pt", padding=True)
                with torch.no_grad():
                    outputs = model(**inputs)
                    score = outputs.logits_per_image[0].item()

            scores.append(score >= self.min_score)

        # Filter batch
        return self._filter_batch_by_mask(batch, scores)

    def _extract_images(self, batch: Any) -> List[Image.Image]:
        """Extract PIL Images from batch."""
        # TODO: Implement extraction from various formats
        return []

    def _filter_batch_by_mask(self, batch: Any, mask: List[bool]) -> Any:
        """Filter batch by boolean mask."""
        # TODO: Implement batch filtering
        return batch


class ResolutionFilter(FilterOperator):
    """Filter images by resolution and aspect ratio."""

    name = "resolution_filter"
    version = "1.0"
    kind = "filter"

    def __init__(
        self,
        min_width: int = 64,
        min_height: int = 64,
        max_width: int = 4096,
        max_height: int = 4096,
        min_aspect: float = 0.5,
        max_aspect: float = 2.0,
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.min_aspect = min_aspect
        self.max_aspect = max_aspect

    def filter_batch(self, batch: Any, ctx: OpContext) -> Any:
        """Filter images by resolution."""
        images = self._extract_images(batch)
        valid = []

        for img in images:
            width, height = img.size
            aspect = width / height

            if (
                self.min_width <= width <= self.max_width
                and self.min_height <= height <= self.max_height
                and self.min_aspect <= aspect <= self.max_aspect
            ):
                valid.append(True)
            else:
                valid.append(False)

        return self._filter_batch_by_mask(batch, valid)

    def _extract_images(self, batch: Any) -> List[Image.Image]:
        """Extract PIL Images from batch."""
        # TODO: Implement extraction
        return []

    def _filter_batch_by_mask(self, batch: Any, mask: List[bool]) -> Any:
        """Filter batch by boolean mask."""
        # TODO: Implement filtering
        return batch


class NSFWClassifier(FilterOperator):
    """Filter NSFW (Not Safe For Work) images."""

    name = "nsfw_classifier"
    version = "1.0"
    kind = "filter"

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self._model = None

    def _get_model(self):
        if self._model is None:
            # Load NSFW classifier (e.g., from HuggingFace)
            # Placeholder: use a simple heuristic
            pass
        return self._model

    def filter_batch(self, batch: Any, ctx: OpContext) -> Any:
        """Filter NSFW images."""
        images = self._extract_images(batch)
        valid = []

        for img in images:
            # Placeholder: simple heuristic for NSFW detection
            # In production, use a trained NSFW classifier
            nsfw_score = self._compute_nsfw_score(img)

            valid.append(nsfw_score < self.threshold)

        return self._filter_batch_by_mask(batch, valid)

    def _compute_nsfw_score(self, img: Image.Image) -> float:
        """Compute NSFW score for an image."""
        # Placeholder: simple heuristic
        # In production, use a trained classifier
        return 0.1

    def _extract_images(self, batch: Any) -> List[Image.Image]:
        """Extract PIL Images from batch."""
        # TODO: Implement extraction
        return []

    def _filter_batch_by_mask(self, batch: Any, mask: List[bool]) -> Any:
        """Filter batch by boolean mask."""
        # TODO: Implement filtering
        return batch


class AspectRatioMapper(MapperOperator):
    """Mapper to add aspect ratio to image metadata."""

    name = "aspect_ratio"
    version = "1.0"
    kind = "mapper"

    def process_batch(self, batch: Any, ctx: OpContext) -> Any:
        """Add aspect ratio to batch."""
        images = self._extract_images(batch)
        aspect_ratios = []

        for img in images:
            width, height = img.size
            aspect_ratio = width / height
            aspect_ratios.append(aspect_ratio)

        # TODO: Add aspect ratio to batch
        return batch

    def _extract_images(self, batch: Any) -> List[Image.Image]:
        """Extract PIL Images from batch."""
        # TODO: Implement extraction
        return []


# Register operators
from services.curation.operators import register_operator

register_operator(CLIPScoreFilter)
register_operator(ResolutionFilter)
register_operator(NSFWClassifier)
register_operator(AspectRatioMapper)
