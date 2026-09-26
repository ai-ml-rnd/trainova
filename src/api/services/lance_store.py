"""Lance record store service."""

import os
from typing import Any, Dict, List, Optional

import lance
import pyarrow as pa
from pydantic import BaseModel

from app.config import settings


class LanceStore:
    """Lance record store service."""

    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        self.bucket = settings.s3_bucket
        self.uri = f"s3://{self.bucket}/records/{dataset_id}"

    def _get_table_schema(self) -> pa.Schema:
        """Get Arrow schema for records."""
        return pa.schema([
            pa.field("record_id", pa.string()),
            pa.field("fields", pa.string()),  # JSON string
            pa.field("metadata", pa.string()),  # JSON string
            pa.field("provenance", pa.string()),  # JSON string
            pa.field("status", pa.string()),
            pa.field("created_at", pa.timestamp("us")),
        ])

    def create(self, data: list[dict]) -> None:
        """Create a new Lance dataset."""
        schema = self._get_table_schema()
        table = pa.Table.from_pylist(data, schema=schema)
        lance.write_dataset(table, self.uri, mode="create")

    def append(self, data: list[dict]) -> None:
        """Append records to existing dataset."""
        table = pa.Table.from_pylist(data, schema=self._get_table_schema())
        dataset = lance.dataset(self.uri)
        dataset.merge_insert("record_id") \
            .when_matched_update_all() \
            .when_not_matched_insert_all() \
            .execute(table)

    def search(self, query: dict, limit: int = 50, cursor: str | None = None) -> dict:
        """Search records using DSL query."""
        dataset = lance.dataset(self.uri)
        
        # Parse query DSL and build filter
        filter_expr = self._build_filter(query.get("filter", {}))
        
        # Execute search
        if cursor:
            results = dataset.scanner(filter=filter_expr, batch_size=limit, start_offset=int(cursor))
        else:
            results = dataset.scanner(filter=filter_expr, batch_size=limit)
        
        # Convert to list of dicts
        records = []
        for batch in results.to_batches():
            for row in batch.to_pylist():
                records.append({
                    "record_id": row["record_id"],
                    "fields": row["fields"],
                    "metadata": row["metadata"],
                    "provenance": row["provenance"],
                    "status": row["status"],
                })
        
        next_cursor = str(int(cursor or 0) + len(records)) if cursor else None
        
        return {
            "records": records,
            "next_cursor": next_cursor,
            "pagination": {
                "page": 1,
                "page_size": limit,
                "total": dataset.count_rows(),
            },
        }

    def get(self, record_id: str) -> dict | None:
        """Get record by ID."""
        dataset = lance.dataset(self.uri)
        results = dataset.scanner(filter=f"record_id = '{record_id}'").to_table()
        
        if len(results) == 0:
            return None
        
        row = results.to_pylist()[0]
        return {
            "record_id": row["record_id"],
            "fields": row["fields"],
            "metadata": row["metadata"],
            "provenance": row["provenance"],
            "status": row["status"],
        }

    def delete(self, record_id: str) -> None:
        """Delete record by ID."""
        dataset = lance.dataset(self.uri)
        dataset.delete(f"record_id = '{record_id}'")

    def _build_filter(self, filter_dict: dict) -> str:
        """Build filter expression from DSL."""
        if not filter_dict:
            return "1 = 1"
        
        conditions = []
        for key, value in filter_dict.items():
            if isinstance(value, dict):
                if "eq" in value:
                    conditions.append(f"{key} = '{value['eq']}'")
                elif "in" in value:
                    values = ",".join(f"'{v}'" for v in value["in"])
                    conditions.append(f"{key} IN ({values})")
                elif "like" in value:
                    conditions.append(f"{key} LIKE '{value['like']}'")
            else:
                conditions.append(f"{key} = '{value}'")
        
        return " AND ".join(conditions) if conditions else "1 = 1"


def get_lance_store(dataset_id: str) -> LanceStore:
    """Get Lance store instance."""
    return LanceStore(dataset_id)
