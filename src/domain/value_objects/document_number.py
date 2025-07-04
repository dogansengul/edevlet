"""
DocumentNumber Value Object - Domain Layer
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentNumber:
    """
    Document Number Value Object.
    
    Domain Rules:
    - Document number cannot be empty
    - Must contain only alphanumeric characters and allowed special chars
    - Length must be between 5 and 50 characters
    - Value is immutable
    """
    value: str
    
    def __post_init__(self):
        """Validate document number on creation."""
        if not self._is_valid():
            raise ValueError(f"Invalid document number: {self.value}")
    
    def _is_valid(self) -> bool:
        """Validate document number format."""
        if not self.value or not self.value.strip():
            return False
        
        # Length check
        if len(self.value) < 5 or len(self.value) > 50:
            return False
        
        # Allow alphanumeric, underscores, hyphens
        pattern = r'^[A-Za-z0-9_-]+$'
        return bool(re.match(pattern, self.value))
    
    @classmethod
    def create(cls, value: str) -> 'DocumentNumber':
        """Factory method to create DocumentNumber."""
        return cls(value.strip() if value else "")
    
    def __str__(self) -> str:
        return self.value 