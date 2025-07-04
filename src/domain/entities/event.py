"""
Event Entity - Domain Layer
Clean Architecture - Core business entity with rich domain logic
"""
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

from ..value_objects.event_type import EventType
from ..value_objects.document_number import DocumentNumber
from ..value_objects.identity_number import IdentityNumber


class EventStatus(Enum):
    """Event processing status enumeration."""
    NEW = "new"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRYING = "retrying"


class Event:
    """
    Event Domain Entity.
    
    Represents a document verification event with complete business logic.
    Encapsulates all business rules related to event processing lifecycle.
    """
    
    def __init__(
        self,
        user_id: str,
        identity_number: IdentityNumber,
        event_type: EventType,
        event_data: Dict[str, Any],
        document_number: Optional[DocumentNumber] = None
    ):
        """
        Initialize Event entity.
        
        Args:
            user_id: User identifier
            identity_number: TC Identity number value object
            event_type: Event type value object
            event_data: Raw event data
            document_number: Document number value object
        """
        # Validate required fields
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        # Core fields
        self.id: Optional[int] = None
        self.user_id = user_id.strip()
        self.identity_number = identity_number
        self.event_type = event_type
        self.event_data = event_data or {}
        self.document_number = document_number
        
        # State fields
        self.status = EventStatus.NEW
        self.retry_count = 0
        self.error_message: Optional[str] = None
        
        # Timestamps
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.processed_at: Optional[datetime] = None
    
    def start_processing(self) -> None:
        """
        Mark event as being processed.
        
        Business Rule: Event must be in NEW or RETRYING status to start processing
        """
        if self.status not in [EventStatus.NEW, EventStatus.RETRYING]:
            raise ValueError(f"Cannot start processing event in {self.status.value} status")
        
        self.status = EventStatus.PROCESSING
        self.updated_at = datetime.now()
    
    def mark_as_processed(self) -> None:
        """
        Mark event as successfully processed.
        
        Business Rule: Event must be in PROCESSING status to be marked as processed
        """
        if self.status != EventStatus.PROCESSING:
            raise ValueError(f"Cannot mark event as processed from {self.status.value} status")
        
        self.status = EventStatus.PROCESSED
        self.processed_at = datetime.now()
        self.updated_at = datetime.now()
        self.error_message = None
    
    def mark_as_failed(self, error_message: str) -> None:
        """
        Mark event as failed.
        
        Business Rule: Can only fail from PROCESSING or RETRYING status
        
        Args:
            error_message: Description of the failure
        """
        if self.status not in [EventStatus.PROCESSING, EventStatus.RETRYING]:
            raise ValueError(f"Cannot mark event as failed from {self.status.value} status")
        
        if not error_message or not error_message.strip():
            raise ValueError("Error message cannot be empty")
        
        self.status = EventStatus.FAILED
        self.error_message = error_message.strip()
        self.updated_at = datetime.now()
    
    def mark_for_retry(self) -> None:
        """
        Mark event for retry.
        
        Business Rule: Only failed events can be retried, max 3 retries
        """
        if self.status != EventStatus.FAILED:
            raise ValueError(f"Cannot retry event in {self.status.value} status")
        
        if self.retry_count >= 3:
            raise ValueError("Maximum retry count (3) exceeded")
        
        self.status = EventStatus.RETRYING
        self.retry_count += 1
        self.updated_at = datetime.now()
        self.error_message = None
    
    def can_be_processed(self) -> bool:
        """
        Check if event can be processed.
        
        Business Rule: Event must be in NEW or RETRYING status to be processable
        
        Returns:
            True if event can be processed
        """
        return self.status in [EventStatus.NEW, EventStatus.RETRYING]
    
    def can_be_retried(self) -> bool:
        """
        Check if event can be retried.
        
        Business Rule: Event must be FAILED and retry count < 3
        
        Returns:
            True if event can be retried
        """
        return self.status == EventStatus.FAILED and self.retry_count < 3
    
    def is_terminal_state(self) -> bool:
        """
        Check if event is in a terminal state.
        
        Terminal states: PROCESSED or FAILED with max retries exceeded
        
        Returns:
            True if event is in terminal state
        """
        return (
            self.status == EventStatus.PROCESSED or
            (self.status == EventStatus.FAILED and self.retry_count >= 3)
        )
    
    def get_processing_duration(self) -> Optional[float]:
        """
        Get processing duration in seconds.
        
        Returns:
            Duration in seconds if processed, None otherwise
        """
        if self.processed_at:
            return (self.processed_at - self.created_at).total_seconds()
        return None
    
    def get_document_type_display(self) -> str:
        """
        Get human-readable document type.
        
        Returns:
            Display name for document type
        """
        if "Education" in str(self.event_type):
            return "Eğitim Belgesi"
        elif "Security" in str(self.event_type):
            return "Güvenlik Belgesi"
        else:
            return "Bilinmeyen Belge Tipi"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for serialization.
        
        Returns:
            Dictionary representation of event
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "identity_number": str(self.identity_number),
            "event_type": str(self.event_type),
            "document_number": str(self.document_number) if self.document_number else None,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "error_message": self.error_message,
            "event_data": self.event_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
    
    def __str__(self) -> str:
        """String representation of event."""
        return f"Event({self.id}, {self.user_id}, {self.event_type}, {self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of event."""
        return (
            f"Event(id={self.id}, user_id='{self.user_id}', "
            f"event_type={self.event_type}, status={self.status.value}, "
            f"retry_count={self.retry_count})"
        )


class DocumentVerificationEvent(Event):
    """
    Specialized Event for document verification.
    
    Domain-specific event with additional verification business rules.
    """
    
    def __init__(
        self,
        user_id: str,
        identity_number: IdentityNumber,
        event_type: EventType,
        event_data: Dict[str, Any],
        document_number: DocumentNumber
    ):
        """Initialize document verification event."""
        super().__init__(user_id, identity_number, event_type, event_data, document_number)
        
        # Verify document number is present for verification events
        if not document_number:
            raise ValueError("Document number is required for verification events")
    
    def get_verification_key(self) -> str:
        """
        Get unique verification key for this event.
        
        Business Rule: Verification key combines identity number and document number
        
        Returns:
            Unique verification key
        """
        return f"{self.identity_number}_{self.document_number}"
    
    def requires_manual_verification(self) -> bool:
        """
        Check if manual verification is required.
        
        Business Rule: Manual verification required after 2 failed attempts
        
        Returns:
            True if manual verification is required
        """
        return self.retry_count >= 2 and self.status == EventStatus.FAILED 