"""Deduplication operators."""

import hashlib
from typing import List, Dict, Set, Optional
import dataclasses

from core.curation.operator import DedupOperator, OperatorKind, OpContext
import pyarrow as pa


@dataclasses.dataclass
class DedupResult:
    """Result of deduplication."""
    
    cluster_id: str
    duplicate_ids: List[str]
    primary_id: str


class ExactDedupOperator(DedupOperator):
    """Exact deduplication using SHA-256."""
    
    name: str = "exact_dedup"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.DEDUP
    
    def __init__(self, text_field: str = "text"):
        self.text_field = text_field
        self._hash_to_ids: Dict[str, List[str]] = {}
    
    def identify_duplicates(self, batch: pa.RecordBatch) -> List[str]:
        """Identify duplicates using SHA-256 hash."""
        if self.text_field not in batch.column_names:
            return []
        
        hashes = []
        dup_ids = []
        
        for i in range(len(batch)):
            text = batch.column(self.text_field)[i].as_py()
            if not text:
                continue
            
            hash_val = hashlib.sha256(text.encode()).hexdigest()
            if hash_val in self._hash_to_ids:
                dup_ids.append(str(i))
                self._hash_to_ids[hash_val].append(str(i))
            else:
                self._hash_to_ids[hash_val] = [str(i)]
                hashes.append(hash_val)
        
        return dup_ids
    
    def process_batch(self, batch: pa.RecordBatch, ctx: OpContext) -> pa.RecordBatch:
        """Process batch and add cluster_id column."""
        dup_ids = self.identify_duplicates(batch)
        
        cluster_ids = [None] * len(batch)
        
        for i in range(len(batch)):
            if str(i) in dup_ids:
                cluster_ids[i] = "duplicate"
            else:
                text = batch.column(self.text_field)[i].as_py()
                if text:
                    hash_val = hashlib.sha256(text.encode()).hexdigest()
                    cluster_ids[i] = f"cluster_{hash_val[:16]}"
                else:
                    cluster_ids[i] = "empty"
        
        return batch.append_column("dup_cluster_id", pa.array(cluster_ids))


class MinHashOperator(DedupOperator):
    """MinHash-LSH deduplication."""
    
    name: str = "minhash_dedup"
    version: str = "1.0"
    kind: OperatorKind = OperatorKind.DEDUP
    
    def __init__(
        self,
        n_bands: int = 14,
        n_rows_per_band: int = 8,
        ngram_size: int = 5,
        jaccard_threshold: float = 0.8,
    ):
        self.n_bands = n_bands
        self.n_rows_per_band = n_rows_per_band
        self.ngram_size = ngram_size
        self.jaccard_threshold = jaccard_threshold
        self._minhashes: Dict[str, List[int]] = {}
        self._union_find: Dict[str, str] = {}
    
    def _shingle(self, text: str) -> Set[str]:
        """Generate shingles from text."""
        if len(text) < self.ngram_size:
            return set()
        
        shingles = set()
        for i in range(len(text) - self.ngram_size + 1):
            shingles.add(text[i:i + self.ngram_size])
        return shingles
    
    def _minhash(self, shingles: Set[str], seed: int) -> int:
        """Compute minhash for shingles."""
        if not shingles:
            return 0
        
        min_val = float('inf')
        for shingle in shingles:
            hash_val = hash((seed, shingle))
            if hash_val < min_val:
                min_val = hash_val
        return min_val
    
    def compute_minhash(self, text: str) -> List[int]:
        """Compute MinHash signature for text."""
        shingles = self._shingle(text)
        num_hashes = self.n_bands * self.n_rows_per_band
        return [self._minhash(shingles, i) for i in range(num_hashes)]
    
    def _find_similar(self, minhash: List[int]) -> Optional[str]:
        """Find similar items using LSH."""
        bands = []
        for i in range(self.n_bands):
            band = minhash[i * self.n_rows_per_band:(i + 1) * self.n_rows_per_band]
            bands.append(tuple(band))
        
        # Check for matches in each band
        for band in bands:
            # In production, use a hash table for LSH buckets
            # For MVP, just return None (will be implemented later)
            pass
        
        return None
    
    def identify_duplicates(self, batch: pa.RecordBatch) -> List[str]:
        """Identify duplicates using MinHash."""
        if "text" not in batch.column_names:
            return []
        
        dup_ids = []
        
        for i in range(len(batch)):
            text = batch.column("text")[i].as_py()
            if not text:
                continue
            
            minhash = self.compute_minhash(text)
            similar_id = self._find_similar(minhash)
            
            if similar_id is not None:
                dup_ids.append(str(i))
                self._union_find[str(i)] = similar_id
        
        return dup_ids
    
    def process_batch(self, batch: pa.RecordBatch, ctx: OpContext) -> pa.RecordBatch:
        """Process batch and add cluster_id column."""
        dup_ids = self.identify_duplicates(batch)
        
        cluster_ids = []
        cluster_counter = 0
        
        for i in range(len(batch)):
            if str(i) in dup_ids:
                cluster_ids.append(f"minhash_cluster_{cluster_counter}")
            else:
                cluster_ids.append(f"minhash_cluster_{cluster_counter}")
                cluster_counter += 1
        
        return batch.append_column("dup_cluster_id", pa.array(cluster_ids))


def register_dedup_operators(registry):
    """Register dedup operators."""
    registry.register(ExactDedupOperator())
    registry.register(MinHashOperator())
