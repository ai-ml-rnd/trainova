"""PostgreSQL-backed record store implementation."""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from models.dataset import Record as DBRecord, Dataset
from core.record_store import Record, RecordStore, ScanResult, QualityMetrics, ProvenanceEntry


class PostgresRecordStore(RecordStore):
    """PostgreSQL-backed record store implementation for MVP."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
    
    async def bulk_add(self, dataset_id: str, records: List[Record]) -> int:
        """Add multiple records to a dataset."""
        db_records = []
        for record in records:
            db_record = DBRecord(
                dataset_id=uuid.UUID(dataset_id),
                record_id=record.record_id,
                fields=record.fields,
                metadata=record.metadata,
                provenance=[p.model_dump() for p in record.provenance],
                quality=record.quality.model_dump(),
                status=record.status,
                reject_reason=record.reject_reason,
                embedding=record.embedding,
                created_at=datetime.utcnow(),
            )
            db_records.append(db_record)
        
        self.session.add_all(db_records)
        await self.session.flush()
        
        return len(db_records)
    
    async def get_by_id(self, dataset_id: str, record_id: str) -> Optional[Record]:
        """Get a record by its ID."""
        stmt = (
            select(DBRecord)
            .where(DBRecord.dataset_id == uuid.UUID(dataset_id))
            .where(DBRecord.record_id == record_id)
        )
        result = await self.session.execute(stmt)
        db_record = result.scalar_one_or_none()
        
        if db_record is None:
            return None
        
        return Record(
            record_id=db_record.record_id,
            fields=db_record.fields,
            metadata=db_record.metadata or {},
            provenance=[ProvenanceEntry(**p) for p in db_record.provenance or []],
            quality=QualityMetrics(**db_record.quality or {}),
            status=db_record.status,
            reject_reason=db_record.reject_reason,
            embedding=db_record.embedding,
        )
    
    async def scan(
        self,
        dataset_id: str,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> ScanResult:
        """Scan records in a dataset."""
        stmt = (
            select(DBRecord)
            .where(DBRecord.dataset_id == uuid.UUID(dataset_id))
            .order_by(DBRecord.id)
            .limit(limit)
        )
        
        if cursor:
            # Parse cursor (simplified: just use ID offset)
            try:
                cursor_id = int(cursor)
                stmt = stmt.where(DBRecord.id > cursor_id)
            except ValueError:
                pass
        
        result = await self.session.execute(stmt)
        db_records = result.scalars().all()
        
        records = []
        next_cursor = None
        for db_record in db_records:
            records.append(
                Record(
                    record_id=db_record.record_id,
                    fields=db_record.fields,
                    metadata=db_record.metadata or {},
                    provenance=[ProvenanceEntry(**p) for p in db_record.provenance or []],
                    quality=QualityMetrics(**db_record.quality or {}),
                    status=db_record.status,
                    reject_reason=db_record.reject_reason,
                    embedding=db_record.embedding,
                )
            )
            next_cursor = str(db_record.id)
        
        return ScanResult(
            records=records,
            next_cursor=next_cursor if len(records) == limit else None,
        )
    
    async def filter(
        self,
        dataset_id: str,
        filter_expr: Dict[str, Any],
        limit: int = 100
    ) -> List[Record]:
        """Filter records in a dataset using DSL."""
        # Parse filter expression
        where_clause = self._parse_filter(filter_expr)
        
        stmt = (
            select(DBRecord)
            .where(DBRecord.dataset_id == uuid.UUID(dataset_id))
            .where(where_clause)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        db_records = result.scalars().all()
        
        return [
            Record(
                record_id=db_record.record_id,
                fields=db_record.fields,
                metadata=db_record.metadata or {},
                provenance=[ProvenanceEntry(**p) for p in db_record.provenance or []],
                quality=QualityMetrics(**db_record.quality or {}),
                status=db_record.status,
                reject_reason=db_record.reject_reason,
                embedding=db_record.embedding,
            )
            for db_record in db_records
        ]
    
    async def semantic_search(
        self,
        dataset_id: str,
        vector: List[float],
        k: int = 10
    ) -> List[Record]:
        """Semantic search for similar records (placeholder for pgvector)."""
        # For MVP, use simple cosine similarity in Python
        # In production, use pgvector cosine similarity
        
        stmt = (
            select(DBRecord)
            .where(DBRecord.dataset_id == uuid.UUID(dataset_id))
            .where(DBRecord.embedding.isnot(None))
            .limit(k * 10)  # Get more candidates
        )
        
        result = await self.session.execute(stmt)
        db_records = result.scalars().all()
        
        # Calculate cosine similarity
        def cosine_similarity(v1: List[float], v2: List[float]) -> float:
            if not v1 or not v2:
                return 0.0
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = sum(a * a for a in v1) ** 0.5
            norm2 = sum(b * b for b in v2) ** 0.5
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)
        
        scored_records = []
        for db_record in db_records:
            similarity = cosine_similarity(vector, db_record.embedding or [])
            scored_records.append((similarity, db_record))
        
        scored_records.sort(key=lambda x: x[0], reverse=True)
        
        return [
            Record(
                record_id=db_record.record_id,
                fields=db_record.fields,
                metadata=db_record.metadata or {},
                provenance=[ProvenanceEntry(**p) for p in db_record.provenance or []],
                quality=QualityMetrics(**db_record.quality or {}),
                status=db_record.status,
                reject_reason=db_record.reject_reason,
                embedding=db_record.embedding,
            )
            for _, db_record in scored_records[:k]
        ]
    
    def _parse_filter(self, filter_expr: Dict[str, Any]) -> Any:
        """Parse filter expression into SQLAlchemy clause."""
        field = filter_expr.get("field")
        op = filter_expr.get("op")
        value = filter_expr.get("value")
        
        if field == "status":
            column = DBRecord.status
        elif field == "quality.lang":
            column = DBRecord.quality["lang"]
        elif field == "quality.quality_score":
            column = DBRecord.quality["quality_score"]
        else:
            # Generic field access
            column = DBRecord.fields[field] if field in DBRecord.fields else DBRecord.metadata[field]
        
        if op == "==":
            return column == value
        elif op == "!=":
            return column != value
        elif op == ">":
            return column > value
        elif op == "<":
            return column < value
        elif op == ">=":
            return column >= value
        elif op == "<=":
            return column <= value
        elif op == "contains":
            return column.contains(value)
        elif op == "in":
            return column.in_(value)
        else:
            raise ValueError(f"Unknown operator: {op}")
