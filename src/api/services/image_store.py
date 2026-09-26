"""Image store with content-addressed upload, thumbnails, EXIF stripping, pHash dedup."""

import hashlib
import io
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import PIL.Image
from pydantic import BaseModel

from app.config import settings


class ImageMetadata(BaseModel):
    """Image metadata."""

    id: str
    tenant_id: str
    dataset_id: str
    original_filename: str
    content_type: str
    size_bytes: int
    width: int
    height: int
    phash: Optional[str] = None
    thumbnail_url: Optional[str] = None
    exif_stripped: bool
    created_at: datetime


class ImageStore:
    """Content-addressed image store with deduplication."""

    def __init__(self):
        self.metadata_store: Dict[str, ImageMetadata] = {}

    def _compute_phash(self, image: PIL.Image.Image, hash_size: int = 8) -> str:
        """Compute perceptual hash."""
        # Resize to 8x8 grayscale
        gray = image.resize((hash_size, hash_size), PIL.Image.LANCZOS).convert("L")

        # Compute DCT
        dct = np.fft.dct(np.array(gray, dtype=np.float32))

        # Keep top-left 8x8 coefficients
        dct_low = dct[:8, :8]

        # Median threshold
        median = np.median(dct_low)
        phash_bits = (dct_low > median).flatten()

        # Convert to hex
        phash_int = int("".join(str(b) for b in phash_bits), 2)
        return f"{phash_int:016x}"

    def _strip_exif(self, image: PIL.Image.Image) -> PIL.Image.Image:
        """Strip EXIF data from image."""
        data = list(image.getdata())
        stripped = PIL.Image.new(image.mode, image.size)
        stripped.putdata(data)
        return stripped

    async def upload_image(
        self,
        tenant_id: str,
        dataset_id: str,
        file_data: bytes,
        filename: str,
        content_type: str,
    ) -> ImageMetadata:
        """Upload an image with content-addressed storage."""
        # Parse image
        image = PIL.Image.open(io.BytesIO(file_data))

        # Strip EXIF
        stripped_image = self._strip_exif(image)

        # Compute content hash (SHA-256 of PNG bytes)
        png_buffer = io.BytesIO()
        stripped_image.save(png_buffer, format="PNG")
        content_hash = hashlib.sha256(png_buffer.getvalue()).hexdigest()

        # Check for duplicate
        existing = await self._find_by_phash(content_hash)
        if existing:
            return existing

        # Compute pHash
        phash = self._compute_phash(stripped_image)

        # Generate ID
        image_id = f"img-{uuid.uuid4().hex[:12]}"

        # Store in S3
        await self._upload_to_s3(image_id, png_buffer.getvalue(), content_type)

        # Create thumbnail
        thumbnail_url = await self._generate_thumbnail(image_id, stripped_image)

        # Save metadata
        metadata = ImageMetadata(
            id=image_id,
            tenant_id=tenant_id,
            dataset_id=dataset_id,
            original_filename=filename,
            content_type=content_type,
            size_bytes=len(file_data),
            width=stripped_image.width,
            height=stripped_image.height,
            phash=phash,
            thumbnail_url=thumbnail_url,
            exif_stripped=True,
            created_at=datetime.utcnow(),
        )

        self.metadata_store[image_id] = metadata

        return metadata

    async def _find_by_phash(self, content_hash: str) -> Optional[ImageMetadata]:
        """Find image by content hash (dedup check)."""
        for metadata in self.metadata_store.values():
            if metadata.id == content_hash:
                return metadata
        return None

    async def _upload_to_s3(
        self,
        image_id: str,
        file_data: bytes,
        content_type: str,
    ) -> None:
        """Upload image to S3."""
        # TODO: Implement S3 upload via SeaweedFS/S3-compatible store
        pass

    async def _generate_thumbnail(
        self,
        image_id: str,
        image: PIL.Image.Image,
        size: tuple[int, int] = (256, 256),
    ) -> str:
        """Generate thumbnail URL."""
        # TODO: Generate thumbnail and return URL
        return f"/images/{image_id}/thumbnail"

    async def get_image(self, image_id: str) -> Optional[ImageMetadata]:
        """Get image metadata by ID."""
        return self.metadata_store.get(image_id)

    async def search_similar(
        self,
        image_id: str,
        max_results: int = 10,
        threshold: float = 0.9,
    ) -> List[ImageMetadata]:
        """Find similar images by pHash."""
        target = self.metadata_store.get(image_id)
        if not target:
            return []

        similar = []
        target_phash = int(target.phash, 16) if target.phash else 0

        for metadata in self.metadata_store.values():
            if metadata.id == image_id:
                continue

            if not metadata.phash:
                continue

            metadata_phash = int(metadata.phash, 16)
            hamming_dist = bin(target_phash ^ metadata_phash).count("1")
            similarity = 1 - (hamming_dist / 64)

            if similarity >= threshold:
                similar.append(metadata)

        similar.sort(key=lambda x: 1 - (bin(target_phash ^ int(x.phash, 16)).count("1") / 64))

        return similar[:max_results]


# Global instance
_image_store: Optional[ImageStore] = None


def get_image_store() -> ImageStore:
    """Get the global image store."""
    global _image_store
    if _image_store is None:
        _image_store = ImageStore()
    return _image_store
