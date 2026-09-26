"""Deduplication service."""

import hashlib
from typing import List, Optional

import pyarrow as pa
import ray

from services.curation.operators import DedupOperator, OpContext


@ray.remote
class MinHashActor:
    """Ray actor for MinHash computation."""

    def __init__(self, num_bands: int = 14, rows_per_band: int = 8):
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.hash_functions = self._create_hash_functions()

    def _create_hash_functions(self) -> list:
        """Create hash functions for MinHash."""
        import mmh3

        return [
            lambda x, seed=i: mmh3.hash(str(x), seed) for i in range(num_bands * rows_per_band)
        ]

    def compute_minhash(self, shingles: list) -> list:
        """Compute MinHash for a set of shingles."""
        minhashes = [float("inf")] * (self.num_bands * self.rows_per_band)

        for shingle in shingles:
            for i, hash_func in enumerate(self.hash_functions):
                h = hash_func(shingle)
                minhashes[i] = min(minhashes[i], h)

        return minhashes

    def get_band_signatures(self, minhashes: list) -> list:
        """Get band signatures for LSH."""
        signatures = []
        for band in range(self.num_bands):
            start = band * self.rows_per_band
            end = start + self.rows_per_band
            signatures.append(tuple(minhashes[start:end]))
        return signatures


@ray.remote
class UnionFindActor:
    """Ray actor for union-find clustering."""

    def __init__(self):
        self.parent: dict = {}
        self.rank: dict = {}

    def find(self, x: str) -> str:
        """Find root with path compression."""
        if self.parent.get(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent.get(x, x)

    def union(self, x: str, y: str) -> None:
        """Union two elements."""
        px, py = self.find(x), self.find(y)
        if px == py:
            return

        if self.rank.get(px, 0) < self.rank.get(py, 0):
            px, py = py, px
        self.parent[py] = px
        self.rank[px] = self.rank.get(px, 0) + 1


class ExactDedup:
    """Exact deduplication using SHA-256 hashes."""

    @staticmethod
    def compute_hash(text: str) -> str:
        """Compute SHA-256 hash of text."""
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def deduplicate(records: list[dict]) -> tuple[list[dict], list[str]]:
        """Deduplicate records and return unique records + duplicates."""
        seen = set()
        unique = []
        duplicates = []

        for record in records:
            text = record.get("text", "")
            hash_val = ExactDedup.compute_hash(text)

            if hash_val not in seen:
                seen.add(hash_val)
                record["dedup_hash"] = hash_val
                record["dup_cluster_id"] = hash_val
                unique.append(record)
            else:
                record["dedup_hash"] = hash_val
                record["dup_cluster_id"] = hash_val
                duplicates.append(record)

        return unique, duplicates


class FuzzyDedup:
    """Fuzzy deduplication using MinHash-LSH."""

    def __init__(
        self,
        n_gram_size: int = 5,
        num_bands: int = 14,
        rows_per_band: int = 8,
        threshold: float = 0.8,
    ):
        self.n_gram_size = n_gram_size
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        self.threshold = threshold
        self.actors: list = []
        self.uf_actor: Optional[ray.actor.ActorHandle] = None

    def _shingle(self, text: str) -> set:
        """Create shingles from text."""
        words = text.lower().split()
        return {
            " ".join(words[i : i + self.n_gram_size])
            for i in range(len(words) - self.n_gram_size + 1)
        }

    async def initialize(self):
        """Initialize Ray actors."""
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)

        self.actors = [
            MinHashActor.remote(self.num_bands, self.rows_per_band)
            for _ in range(10)  # 10 parallel actors
        ]
        self.uf_actor = UnionFindActor.remote()

    async def deduplicate(
        self, records: list[dict]
    ) -> tuple[list[dict], dict[str, list[str]]]:
        """Deduplicate records using MinHash-LSH."""
        await self.initialize()

        # Compute MinHashes in parallel
        futures = []
        for record in records:
            shingles = self._shingle(record.get("text", ""))
            actor = self.actors[hash(record["record_id"]) % len(self.actors)]
            futures.append(
                actor.compute_minhash.remote(list(shingles)).then(
                    lambda mh, rid=record["record_id"]: (rid, mh)
                )
            )

        results = await ray.get(futures)

        # Build LSH index
        lsh_index: dict[str, list[str]] = {}
        for record_id, minhash in results:
            signatures = self.actors[
                hash(record_id) % len(self.actors)
            ].get_band_signatures.remote(minhash)
            for sig in await ray.get(signatures):
                if sig not in lsh_index:
                    lsh_index[sig] = []
                lsh_index[sig].append(record_id)

        # Cluster similar records
        uf = UnionFindActor.remote()
        for sig, record_ids in lsh_index.items():
            if len(record_ids) > 1:
                for i in range(1, len(record_ids)):
                    await uf.union.remote(record_ids[0], record_ids[i])

        # Get clusters
        clusters: dict[str, list[str]] = {}
        for record_id in lsh_index.keys():
            root = await uf.find.remote(record_id)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(record_id)

        # Filter clusters above threshold
        unique = []
        duplicate_clusters = {}
        for cluster_id, members in clusters.items():
            if len(members) == 1:
                unique.append({"record_id": members[0], "dup_cluster_id": members[0]})
            else:
                duplicate_clusters[cluster_id] = members

        return unique, duplicate_clusters


async def run_dedup(
    dataset_id: str, method: str = "exact"
) -> dict:
    """Run deduplication on a dataset."""
    if method == "exact":
        dedup = ExactDedup()
    else:
        dedup = FuzzyDedup()

    # TODO: Load records from Lance
    # records = ...

    if method == "exact":
        unique, duplicates = dedup.deduplicate([])
    else:
        unique, clusters = await dedup.deduplicate([])

    return {
        "dataset_id": dataset_id,
        "method": method,
        "records_before": 0,
        "records_after": len(unique),
        "duplicates_removed": 0,
        "cluster_info": clusters if method == "fuzzy" else None,
    }
