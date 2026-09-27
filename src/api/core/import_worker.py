"""Import job worker."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.dataset import Dataset
from models.import_job import ImportJob, ImportJobStatus, SourceType
from core.record_store import Record, PostgresRecordStore
from core.connector.base import SourceConnector
from core.connector.jsonl import JSONLConnector


class ImportWorker:
    """Worker for processing import jobs."""
    
    BATCH_SIZE = 1000
    CHECKPOINT_EVERY = 10000  # Save checkpoint every N records
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.connector: Optional[SourceConnector] = None
    
    async def run(self, job_id: str) -> None:
        """Run an import job.
        
        Args:
            job_id: Import job ID
        """
        # Load job
        stmt = select(ImportJob).where(ImportJob.id == uuid.UUID(job_id))
        result = await self.session.execute(stmt)
        job = result.scalar_one_or_none()
        
        if job is None:
            raise ValueError(f"Import job not found: {job_id}")
        
        # Update status to running
        job.status = ImportJobStatus.RUNNING
        job.started_at = datetime.utcnow()
        await self.session.flush()
        
        try:
            # Initialize connector
            self.connector = self._get_connector(job.source_type)
            
            # Restore from checkpoint if exists
            if job.checkpoint:
                self.connector.restore_from_checkpoint(job.checkpoint)
            
            # Connect to source
            await self.connector.connect(job.source_path)
            
            # Get total count if available
            job.total_rows = await self.connector.get_total_count()
            await self.session.flush()
            
            # Process in batches
            records_processed = job.rows_imported or 0
            
            while True:
                batch = await self.connector.read_batch(self.BATCH_SIZE)
                
                if not batch:
                    break
                
                # Add records to dataset
                record_store = PostgresRecordStore(self.session)
                added = await record_store.bulk_add(str(job.dataset_id), batch)
                
                records_processed += added
                
                # Update progress
                job.rows_imported = records_processed
                if job.total_rows:
                    job.progress = records_processed / job.total_rows
                else:
                    job.progress = 0.0
                
                # Save checkpoint periodically
                if records_processed % self.CHECKPOINT_EVERY == 0:
                    job.checkpoint = self.connector.get_checkpoint()
                
                await self.session.flush()
            
            # Mark as succeeded
            job.status = ImportJobStatus.SUCCEEDED
            job.finished_at = datetime.utcnow()
            job.progress = 1.0
            await self.session.flush()
            
        except Exception as e:
            job.status = ImportJobStatus.FAILED
            job.error = str(e)
            job.finished_at = datetime.utcnow()
            await self.session.flush()
            raise
        
        finally:
            if self.connector:
                await self.connector.close()
    
    def _get_connector(self, source_type: SourceType) -> SourceConnector:
        """Get connector for source type."""
        if source_type == SourceType.JSONL:
            return JSONLConnector()
        elif source_type == SourceType.PARQUET:
            raise NotImplementedError("Parquet connector not yet implemented")
        elif source_type == SourceType.CSV:
            raise NotImplementedError("CSV connector not yet implemented")
        elif source_type == SourceType.S3:
            raise NotImplementedError("S3 connector not yet implemented")
        elif source_type == SourceType.HF:
            raise NotImplementedError("Hugging Face connector not yet implemented")
        else:
            raise ValueError(f"Unknown source type: {source_type}")
