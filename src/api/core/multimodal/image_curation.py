"""Image curation operators."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class ImageMetadata(BaseModel):
    """Image metadata."""
    
    width: int
    height: int
    aspect_ratio: float
    resolution: str
    clip_score: Optional[float] = None
    nsfw_score: Optional[float] = None


class ImageCurationOperator:
    """Base class for image curation operators."""
    
    def __init__(self, name: str):
        self.name = name
    
    def process(self, images: List[Dict]) -> List[Dict]:
        """Process a batch of images."""
        raise NotImplementedError


class ResolutionFilter(ImageCurationOperator):
    """Filter images by resolution."""
    
    def __init__(self, min_width: int = 100, min_height: int = 100):
        super().__init__("resolution_filter")
        self.min_width = min_width
        self.min_height = min_height
    
    def process(self, images: List[Dict]) -> List[Dict]:
        """Filter images by resolution."""
        result = []
        
        for img in images:
            metadata = img.get("metadata", {})
            width = metadata.get("width", 0)
            height = metadata.get("height", 0)
            
            if width >= self.min_width and height >= self.min_height:
                result.append(img)
            else:
                img["reject_reason"] = f"Resolution {width}x{height} < {self.min_width}x{self.min_height}"
                result.append(img)
        
        return result


class AspectRatioFilter(ImageCurationOperator):
    """Filter images by aspect ratio."""
    
    def __init__(self, min_ratio: float = 0.5, max_ratio: float = 2.0):
        super().__init__("aspect_ratio_filter")
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
    
    def process(self, images: List[Dict]) -> List[Dict]:
        """Filter images by aspect ratio."""
        result = []
        
        for img in images:
            metadata = img.get("metadata", {})
            aspect = metadata.get("aspect_ratio", 1.0)
            
            if self.min_ratio <= aspect <= self.max_ratio:
                result.append(img)
            else:
                img["reject_reason"] = f"Aspect ratio {aspect} not in [{self.min_ratio}, {self.max_ratio}]"
                result.append(img)
        
        return result


class NSFWFilter(ImageCurationOperator):
    """Filter NSFW images."""
    
    def __init__(self, threshold: float = 0.7):
        super().__init__("nsfw_filter")
        self.threshold = threshold
    
    def process(self, images: List[Dict]) -> List[Dict]:
        """Filter NSFW images."""
        result = []
        
        for img in images:
            metadata = img.get("metadata", {})
            nsfw_score = metadata.get("nsfw_score", 0.0)
            
            if nsfw_score < self.threshold:
                result.append(img)
            else:
                img["reject_reason"] = f"NSFW score {nsfw_score} >= {self.threshold}"
                result.append(img)
        
        return result


class CLIPScoreFilter(ImageCurationOperator):
    """Filter by CLIP score."""
    
    def __init__(self, min_score: float = 0.2):
        super().__init__("clip_score_filter")
        self.min_score = min_score
    
    def process(self, images: List[Dict]) -> List[Dict]:
        """Filter by CLIP score."""
        result = []
        
        for img in images:
            metadata = img.get("metadata", {})
            clip_score = metadata.get("clip_score", 0.0)
            
            if clip_score >= self.min_score:
                result.append(img)
            else:
                img["reject_reason"] = f"CLIP score {clip_score} < {self.min_score}"
                result.append(img)
        
        return result


def register_image_curation_operators(registry):
    """Register image curation operators."""
    registry.register(ResolutionFilter())
    registry.register(AspectRatioFilter())
    registry.register(NSFWFilter())
    registry.register(CLIPScoreFilter())
