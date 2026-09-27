"""Operator registry for curation pipeline."""

from typing import Dict, List, Optional

from core.curation.operator import Operator, OperatorKind


class OperatorRegistry:
    """Registry for curation operators."""
    
    def __init__(self):
        self._operators: Dict[tuple, Operator] = {}  # (name, version) -> operator
    
    def register(self, operator: Operator) -> None:
        """Register an operator.
        
        Args:
            operator: Operator instance
        """
        key = (operator.name, operator.version)
        self._operators[key] = operator
    
    def get(self, name: str, version: Optional[str] = None) -> Operator:
        """Get operator by name and optionally version.
        
        Args:
            name: Operator name
            version: Operator version (optional, uses latest if not specified)
            
        Returns:
            Operator instance
            
        Raises:
            ValueError: If operator not found
        """
        if version is not None:
            key = (name, version)
            if key not in self._operators:
                raise ValueError(f"Operator not found: {name} v{version}")
            return self._operators[key]
        
        # Get latest version
        matching = [(k, v) for k, v in self._operators.items() if k[0] == name]
        if not matching:
            raise ValueError(f"Operator not found: {name}")
        
        # Return operator with highest version
        matching.sort(key=lambda x: x[0][1], reverse=True)
        return matching[0][1]
    
    def list(self, kind: Optional[OperatorKind] = None) -> List[Operator]:
        """List registered operators.
        
        Args:
            kind: Filter by kind (optional)
            
        Returns:
            List of operators
        """
        operators = list(self._operators.values())
        if kind is not None:
            operators = [o for o in operators if o.kind == kind]
        return operators
    
    def kind_exists(self, kind: OperatorKind) -> bool:
        """Check if any operator of given kind is registered."""
        return any(o.kind == kind for o in self._operators.values())


# Global registry instance
operator_registry = OperatorRegistry()
