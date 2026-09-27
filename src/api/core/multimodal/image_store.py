"""Content-addressed image storage."""

import hashlib
from typing import Optional, Tuple
from PIL import Image
import io


class ImageStore:
    """Content-addressed image storage."""
    
    def __init__(self, base_path: str = "/data/images"):
        self.base_path = base_path
    
    def compute_phash(self, image_data: bytes) -> str:
        """Compute perceptual hash for image deduplication."""
        # For MVP, use SHA-256 as placeholder
        return hashlib.sha256(image_data).hexdigest()[:16]
    
    def compute_fingerprint(self, image_data: bytes) -> str:
        """Compute unique fingerprint for image."""
        return hashlib.sha256(image_data).hexdigest()
    
    async def upload_image(
        self,
        image_data: bytes,
        tenant_id: str,
        filename: Optional[str] = None,
    ) -> dict:
        """
        Upload an image with content-addressed storage.
        
        Args:
            image_data: Image bytes
            tenant_id: Tenant identifier
            filename: Original filename (optional)
            
        Returns:
            Image metadata with path, hash, dimensions
        """
        # Compute fingerprint for deduplication
        fingerprint = self.compute_fingerprint(image_data)
        phash = self.compute_phash(image_data)
        
        # Check for duplicate
        existing = await self._get_by_fingerprint(fingerprint)
        if existing:
            return existing
        
        # Generate storage path
        path = f"{self.base_path}/{tenant_id}/{fingerprint[:2]}/{fingerprint[2:4]}/{fingerprint}"
        
        # Create thumbnails
        thumbnails = await self._generate_thumbnails(image_data)
        
        # Store image
        await self._store_image(image_data, path)
        
        # Store metadata
        metadata = {
            "fingerprint": fingerprint,
            "phash": phash,
            "path": path,
            "filename": filename,
            "tenant_id": tenant_id,
            "thumbnails": thumbnails,
            "created_at": "2026-09-27T00:00:00Z",
        }
        
        await self._store_metadata(metadata)
        
        return metadata
    
    async def _get_by_fingerprint(self, fingerprint: str) -> Optional[dict]:
        """Get image by fingerprint (for dedup)."""
        # Placeholder - in production, query metadata store
        return None
    
    async def _store_image(self, image_data: bytes, path: str) -> None:
        """Store image bytes."""
        # Placeholder - in production, store to S3/GCS
        pass
    
    async def _store_metadata(self, metadata: dict) -> None:
        """Store image metadata."""
        # Placeholder - in production, store to Postgres
        pass
    
    async def _generate_thumbnails(self, image_data: bytes) -> dict:
        """Generate thumbnails at various sizes."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            thumbnails = {}
            for size in [(128, 128), (256, 256), (512, 512)]:
                img_copy = image.copy()
                img_copy.thumbnail(size, Image.LANCZOS)
                
                buf = io.BytesIO()
                img_copy.save(buf, format="JPEG", quality=85)
                thumbnails[f"{size[0]}x{size[1]}"] = buf.getvalue()
            
            return thumbnails
        except Exception:
            return {}


def strip_exif(image_data: bytes) -> bytes:
    """Strip EXIF data from image."""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Get image data without EXIF
        data = list(image.getdata())
        clean_image = Image.new(image.mode, image.size)
        clean_image.putdata(data)
        
        buf = io.BytesIO()
        clean_image.save(buf, format=image.format)
        
        return buf.getvalue()
    except Exception:
        return image_data
