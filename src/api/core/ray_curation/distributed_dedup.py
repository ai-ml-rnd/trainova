"""Distributed MinHash deduplication with Ray actors."""

from typing import List, Dict, Set
import hashlib


class MinHashActor:
    """Ray actor for MinHash computation."""
    
    def __init__(self, actor_id: int, n_bands: int = 14, n_rows: int = 8):
        self.actor_id = actor_id
        self.n_bands = n_bands
        self.n_rows = n_rows
        self._minhashes: Dict[str, List[int]] = {}
    
    def compute_minhash(self, text: str) -> List[int]:
        """Compute MinHash for text."""
        # For MVP, use simple hash-based MinHash
        signature = []
        for i in range(self.n_bands * self.n_rows):
            hash_val = hash((i, text))
            signature.append(hash_val % (2**32 - 1))
        return signature
    
    def add_document(self, doc_id: str, text: str) -> List[int]:
        """Add document and compute MinHash."""
        minhash = self.compute_minhash(text)
        self._minhashes[doc_id] = minhash
        return minhash
    
    def get_minhash(self, doc_id: str) -> Optional[List[int]]:
        """Get MinHash for document."""
        return self._minhashes.get(doc_id)
    
    def find_candidates(self, minhash: List[int], threshold: float = 0.8) -> List[str]:
        """Find candidate duplicates using LSH."""
        candidates = []
        
        for doc_id, other_minhash in self._minhashes.items():
            jaccard = self._jaccard_similarity(minhash, other_minhash)
            if jaccard >= threshold:
                candidates.append(doc_id)
        
        return candidates
    
    def _jaccard_similarity(self, a: List[int], b: List[int]) -> float:
        """Compute Jaccard similarity between two MinHashes."""
        if len(a) != len(b):
            return 0.0
        
        matches = sum(1 for x, y in zip(a, b) if x == y)
        return matches / len(a)


class UnionFind:
    """Union-Find data structure for clustering."""
    
    def __init__(self):
        self._parent: Dict[str, str] = {}
        self._rank: Dict[str, int] = {}
    
    def find(self, x: str) -> str:
        """Find root of set."""
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0
            return x
        
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        
        return self._parent[x]
    
    def union(self, x: str, y: str) -> None:
        """Union two sets."""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return
        
        if self._rank[root_x] < self._rank[root_y]:
            self._parent[root_x] = root_y
        elif self._rank[root_x] > self._rank[root_y]:
            self._parent[root_y] = root_x
        else:
            self._parent[root_y] = root_x
            self._rank[root_x] += 1
    
    def get_clusters(self) -> Dict[str, List[str]]:
        """Get clusters as dict of root -> members."""
        clusters: Dict[str, List[str]] = {}
        
        for doc_id in self._parent:
            root = self.find(doc_id)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(doc_id)
        
        return clusters


class DistributedMinHash:
    """Distributed MinHash deduplication."""
    
    def __init__(self, n_bands: int = 14, n_rows: int = 8, threshold: float = 0.8):
        self.n_bands = n_bands
        self.n_rows = n_rows
        self.threshold = threshold
        self._actors: List[MinHashActor] = []
        self._union_find = UnionFind()
    
    async def initialize_actors(self, num_actors: int) -> None:
        """Initialize Ray actors."""
        for i in range(num_actors):
            self._actors.append(MinHashActor(i, self.n_bands, self.n_rows))
    
    async def add_document(self, doc_id: str, text: str) -> str:
        """Add document for deduplication."""
        # Distribute to actors
        actor_idx = hash(doc_id) % len(self._actors)
        actor = self._actors[actor_idx]
        
        minhash = actor.add_document(doc_id, text)
        
        # Find candidates
        candidates = actor.find_candidates(minhash, self.threshold)
        
        # Union with candidates
        for candidate in candidates:
            self._union_find.union(doc_id, candidate)
        
        return self._union_find.find(doc_id)
    
    async def get_clusters(self) -> Dict[str, List[str]]:
        """Get deduplication clusters."""
        return self._union_find.get_clusters()
    
    async def close(self):
        """Cleanup resources."""
        self._actors.clear()
