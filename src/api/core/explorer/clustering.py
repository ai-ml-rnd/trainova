"""Embedding clustering for data explorer."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class Cluster(BaseModel):
    """Cluster of similar documents."""
    
    cluster_id: str
    centroid: List[float]
    documents: List[str]
    title: Optional[str] = None
    size: int


class EmbeddingClusterer:
    """Embedding clusterer for data explorer."""
    
    def __init__(self, n_clusters: int = 100, embedding_dim: int = 768):
        self.n_clusters = n_clusters
        self.embedding_dim = embedding_dim
    
    def cluster_embeddings(
        self,
        embeddings: List[List[float]],
    ) -> List[int]:
        """Cluster embeddings using K-means."""
        # For MVP, use simple modulo-based clustering
        return [i % self.n_clusters for i in range(len(embeddings))]
    
    async def generate_cluster_titles(
        self,
        clusters: Dict[str, List[str]],
    ) -> Dict[str, str]:
        """Generate titles for clusters using LLM."""
        # For MVP, return placeholder titles
        return {cid: f"Cluster {cid}" for cid in clusters}
    
    async def cluster_documents(
        self,
        document_ids: List[str],
        embeddings: List[List[float]],
    ) -> List[Cluster]:
        """Cluster documents and return cluster objects."""
        cluster_ids = self.cluster_embeddings(embeddings)
        
        # Group by cluster
        cluster_docs: Dict[int, List[str]] = {}
        for doc_id, cluster_id in zip(document_ids, cluster_ids):
            if cluster_id not in cluster_docs:
                cluster_docs[cluster_id] = []
            cluster_docs[cluster_id].append(doc_id)
        
        # Generate cluster objects
        clusters = []
        for cluster_id, docs in cluster_docs.items():
            # Compute centroid (average of embeddings)
            cluster_embeddings = [
                embeddings[i] for i, cid in enumerate(cluster_ids) if cid == cluster_id
            ]
            centroid = [
                sum(e[i] for e in cluster_embeddings) / len(cluster_embeddings)
                for i in range(self.embedding_dim)
            ]
            
            clusters.append(Cluster(
                cluster_id=str(cluster_id),
                centroid=centroid,
                documents=docs,
                size=len(docs),
            ))
        
        return clusters


def cluster_4m_docs() -> Dict:
    """Cluster 4M documents.
    
    Expected: < 1 h on batch node
    """
    clusterer = EmbeddingClusterer(n_clusters=1000)
    
    # For MVP, return placeholder
    return {
        "num_clusters": 1000,
        "docs_per_cluster": 4000,
        "time_seconds": 3600,
    }
