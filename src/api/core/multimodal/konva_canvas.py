"""Konva canvas for image annotation."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class BoundingBox(BaseModel):
    """Bounding box annotation."""
    
    x: float
    y: float
    width: float
    height: float
    label: str
    confidence: Optional[float] = None


class Polygon(BaseModel):
    """Polygon annotation."""
    
    points: List[tuple]  # List of (x, y) coordinates
    label: str


class Keypoint(BaseModel):
    """Keypoint annotation."""
    
    x: float
    y: float
    label: str
    visible: bool = True


class ImageAnnotation(BaseModel):
    """Image annotation with various shape types."""
    
    image_id: str
    bounding_boxes: List[BoundingBox] = []
    polygons: List[Polygon] = []
    keypoints: List[Keypoint] = []


class CanvasState(BaseModel):
    """Canvas state for VQA, caption, and pairwise tasks."""
    
    image_id: str
    vqa_questions: List[Dict] = []
    caption: Optional[str] = None
    pairwise_preference: Optional[str] = None  # "left", "right", "tie", "both-bad"
    pairwise_rationale: Optional[str] = None


class KonvaCanvas:
    """Konva canvas for image annotation."""
    
    def __init__(self, max_boxes: int = 500):
        self.max_boxes = max_boxes
    
    def add_bounding_box(self, annotation: ImageAnnotation, box: BoundingBox) -> bool:
        """Add bounding box to annotation."""
        if len(annotation.bounding_boxes) >= self.max_boxes:
            return False
        
        annotation.bounding_boxes.append(box)
        return True
    
    def add_polygon(self, annotation: ImageAnnotation, polygon: Polygon) -> bool:
        """Add polygon to annotation."""
        annotation.polygons.append(polygon)
        return True
    
    def add_keypoint(self, annotation: ImageAnnotation, keypoint: Keypoint) -> bool:
        """Add keypoint to annotation."""
        annotation.keypoints.append(keypoint)
        return True
    
    def to_coco_format(self, annotation: ImageAnnotation) -> Dict:
        """Convert annotation to COCO format."""
        coco = {
            "images": [{
                "id": annotation.image_id,
                "file_name": f"{annotation.image_id}.jpg",
            }],
            "annotations": [],
            "categories": [],
        }
        
        category_id_map = {}
        
        for box in annotation.bounding_boxes:
            if box.label not in category_id_map:
                category_id_map[box.label] = len(category_id_map) + 1
                coco["categories"].append({
                    "id": category_id_map[box.label],
                    "name": box.label,
                })
            
            coco["annotations"].append({
                "id": len(coco["annotations"]) + 1,
                "image_id": annotation.image_id,
                "category_id": category_id_map[box.label],
                "bbox": [box.x, box.y, box.width, box.height],
                "area": box.width * box.height,
                "iscrowd": 0,
            })
        
        return coco
    
    def to_llava_format(self, annotation: ImageAnnotation) -> List[Dict]:
        """Convert annotation to LLaVA conversation format."""
        conversations = []
        
        # Add caption
        conversations.append({
            "from": "human",
            "value": "<image>\nPlease describe this image.",
        })
        conversations.append({
            "from": "gpt",
            "value": "The image shows a scene with various objects.",
        })
        
        # Add bounding box details
        for box in annotation.bounding_boxes:
            conversations.append({
                "from": "human",
                "value": f"<image>\nWhere is the {box.label} in this image?",
            })
            conversations.append({
                "from": "gpt",
                "value": f"The {box.label} is at position [{box.x:.1f}, {box.y:.1f}, {box.width:.1f}, {box.height:.1f}].",
            })
        
        return conversations


def export_conversations(annotations: List[ImageAnnotation], output_path: str) -> None:
    """Export annotations to LLaVA conversation format."""
    conversations = []
    
    for ann in annotations:
        llava_conv = KonvaCanvas().to_llava_format(ann)
        for conv in llava_conv:
            conversations.append(conv)
    
    with open(output_path, "w") as f:
        import json
        json.dump(conversations, f, indent=2)
