"""Document parsing with Unstructured and pdfium."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class Document(BaseModel):
    """Parsed document."""
    
    id: str
    content: str
    metadata: Dict
    pages: List[Dict] = []


class DocumentParser:
    """Document parser."""
    
    def __init__(self, analytics_off: bool = True):
        self.analytics_off = analytics_off
    
    async def parse_pdf(
        self,
        file_path: str,
    ) -> Document:
        """Parse PDF using pdfium."""
        # For MVP, return placeholder
        return Document(
            id=file_path,
            content="PDF content placeholder",
            metadata={"source": file_path, "pages": 1},
        )
    
    async def parse_unstructured(
        self,
        file_path: str,
    ) -> Document:
        """Parse using Unstructured OSS."""
        # For MVP, return placeholder
        return Document(
            id=file_path,
            content="Unstructured content placeholder",
            metadata={"source": file_path},
        )
    
    async def parse_vlm_ocr(
        self,
        image_path: str,
    ) -> Document:
        """Run VLM OCR on scanned image."""
        # For MVP, return placeholder
        return Document(
            id=image_path,
            content="OCR content placeholder",
            metadata={"source": image_path},
        )
    
    async def parse(self, file_path: str) -> Document:
        """Parse document automatically."""
        if file_path.endswith(".pdf"):
            return await self.parse_pdf(file_path)
        elif file_path.endswith((".jpg", ".png", ".jpeg")):
            return await self.parse_vlm_ocr(file_path)
        else:
            return await self.parse_unstructured(file_path)
