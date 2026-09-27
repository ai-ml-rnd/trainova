"""Facets for data explorer."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class FacetValue(BaseModel):
    """Facet value with count."""
    
    value: str
    count: int


class Facet(BaseModel):
    """Facet definition."""
    
    name: str
    values: List[FacetValue]
    total: int


class FacetCalculator:
    """Calculate facets over datasets."""
    
    def __init__(self):
        self._facets: Dict[str, Dict[str, int]] = {}
    
    def add_document(self, doc_id: str, doc: Dict) -> None:
        """Add document for facet calculation."""
        for key, value in doc.items():
            if key not in self._facets:
                self._facets[key] = {}
            str_value = str(value)
            self._facets[key][str_value] = self._facets[key].get(str_value, 0) + 1
    
    def calculate_facets(self, docs: List[Dict]) -> Dict[str, Facet]:
        """Calculate facets over documents."""
        facets = {}
        
        for doc in docs:
            self.add_document(doc.get("id", ""), doc)
        
        for key, values in self._facets.items():
            facet_values = [
                FacetValue(value=v, count=c)
                for v, c in values.items()
            ]
            facets[key] = Facet(
                name=key,
                values=facet_values,
                total=sum(values.values()),
            )
        
        return facets
    
    def filter_facets(
        self,
        facets: Dict[str, Facet],
        accepted_only: bool = False,
        rejected_only: bool = False,
    ) -> Dict[str, Facet]:
        """Filter facets by acceptance status."""
        if not accepted_only and not rejected_only:
            return facets
        
        filtered = {}
        for key, facet in facets.items():
            filtered_values = [
                v for v in facet.values
                if (accepted_only and v.value == "accepted") or
                   (rejected_only and v.value == "rejected") or
                   (not accepted_only and not rejected_only)
            ]
            filtered[key] = Facet(
                name=key,
                values=filtered_values,
                total=sum(v.count for v in filtered_values),
            )
        
        return filtered
