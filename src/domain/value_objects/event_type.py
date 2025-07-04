"""
EventType Value Object - Domain Layer
"""
from enum import Enum
from dataclasses import dataclass


class EventTypeEnum(Enum):
    """Event type enumeration."""
    USER_EDUCATION_CREATED = "UserEducationCreated"
    USER_SECURITY_CREATED = "UserSecurityCreated"
    USER_CV_CREATED = "UserCvCreated"


@dataclass(frozen=True)
class EventType:
    """
    Event Type Value Object.
    
    Domain Rules:
    - Event type must be from supported types
    - Value is immutable (frozen dataclass)
    - Provides business logic for document type mapping
    """
    value: str
    
    def __post_init__(self):
        """Validate event type on creation."""
        if not self._is_valid_event_type():
            raise ValueError(f"Invalid event type: {self.value}")
    
    @classmethod
    def from_string(cls, event_type_str: str) -> 'EventType':
        """Factory method to create from string."""
        return cls(event_type_str)
    
    @classmethod
    def education(cls) -> 'EventType':
        """Factory method for education event."""
        return cls(EventTypeEnum.USER_EDUCATION_CREATED.value)
    
    @classmethod
    def security(cls) -> 'EventType':
        """Factory method for security event."""
        return cls(EventTypeEnum.USER_SECURITY_CREATED.value)
    
    @classmethod
    def cv(cls) -> 'EventType':
        """Factory method for CV event."""
        return cls(EventTypeEnum.USER_CV_CREATED.value)
    
    def _is_valid_event_type(self) -> bool:
        """Check if event type is valid."""
        valid_types = [e.value for e in EventTypeEnum]
        return self.value in valid_types
    
    def get_document_type(self) -> str:
        """Get document type based on event type."""
        if "Education" in self.value:
            return "education"
        elif "Security" in self.value:
            return "security"
        elif "Cv" in self.value:
            return "cv"
        else:
            raise ValueError(f"Unknown document type for event: {self.value}")
    
    def is_education_event(self) -> bool:
        """Check if this is an education event."""
        return self.value == EventTypeEnum.USER_EDUCATION_CREATED.value
    
    def is_security_event(self) -> bool:
        """Check if this is a security event."""
        return self.value == EventTypeEnum.USER_SECURITY_CREATED.value
    
    def is_cv_event(self) -> bool:
        """Check if this is a CV event."""
        return self.value == EventTypeEnum.USER_CV_CREATED.value 