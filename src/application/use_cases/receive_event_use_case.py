"""
Receive Event Use Case - Application Layer
Clean Architecture - Business logic for event reception
"""
import logging
from datetime import datetime
from typing import Dict, Any

from domain.entities.event import Event
from domain.value_objects.event_type import EventType
from domain.value_objects.document_number import DocumentNumber
from domain.value_objects.identity_number import IdentityNumber
from domain.repositories.event_repository import IEventRepository


class EventReceivedResult:
    """Result of event reception operation."""
    
    def __init__(
        self,
        success: bool,
        event_id: int = None,
        error_message: str = None,
        error_code: str = None,
        timestamp: datetime = None,
        queue_stats: Dict[str, Any] = None
    ):
        self.success = success
        self.event_id = event_id
        self.error_message = error_message
        self.error_code = error_code
        self.timestamp = timestamp or datetime.now()
        self.queue_stats = queue_stats or {}
    
    @classmethod
    def success_result(cls, event_id: int, queue_stats: Dict[str, Any]):
        """Create successful result."""
        return cls(success=True, event_id=event_id, queue_stats=queue_stats)
    
    @classmethod
    def failure_result(cls, error_message: str, error_code: str = "UNKNOWN_ERROR"):
        """Create failure result."""
        return cls(success=False, error_message=error_message, error_code=error_code)


class ReceiveEventUseCase:
    """
    Use Case for receiving and queuing events.
    
    Single Responsibility: Only handles event reception business logic
    Dependency Inversion: Depends on repository abstraction, not concrete implementation
    """
    
    def __init__(self, event_repository: IEventRepository):
        """Initialize with repository dependency."""
        self._event_repository = event_repository
        self.logger = logging.getLogger(__name__)
    
    def execute(self, event_data: Dict[str, Any]) -> EventReceivedResult:
        """
        Execute event reception use case.
        
        Business Rules:
        1. Validate event data structure
        2. Create domain entities with validation
        3. Save event to repository
        4. Return result with queue statistics
        
        Args:
            event_data: Raw event data from external source
            
        Returns:
            EventReceivedResult with operation outcome
        """
        try:
            self.logger.info(f"🎯 Executing receive event use case")
            
            # Business Rule: Validate required fields
            validation_result = self._validate_event_data(event_data)
            if not validation_result.success:
                return validation_result
            
            # Business Rule: Create domain entities
            event = self._create_event_entity(event_data)
            
            # Business Rule: Persist event
            saved_event = self._event_repository.save(event)
            
            # Get updated queue statistics
            queue_stats = self._event_repository.get_statistics()
            
            self.logger.info(f"✅ Event saved with ID: {saved_event.id}")
            
            return EventReceivedResult.success_result(
                event_id=saved_event.id,
                queue_stats=queue_stats
            )
            
        except ValueError as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.warning(f"⚠️ {error_msg}")
            return EventReceivedResult.failure_result(error_msg, "VALIDATION_ERROR")
            
        except Exception as e:
            error_msg = f"Unexpected error in event reception: {str(e)}"
            self.logger.error(f"💥 {error_msg}")
            return EventReceivedResult.failure_result(error_msg, "INTERNAL_ERROR")
    
    def _validate_event_data(self, event_data: Dict[str, Any]) -> EventReceivedResult:
        """Validate event data structure."""
        required_fields = ['userId', 'identityNumber', 'eventType', 'eventData']
        
        for field in required_fields:
            if field not in event_data:
                error_msg = f"Missing required field: {field}"
                return EventReceivedResult.failure_result(error_msg, "MISSING_REQUIRED_FIELD")
        
        # Validate eventData structure
        event_data_obj = event_data.get('eventData', {})
        if 'documentNumber' not in event_data_obj:
            error_msg = "Missing documentNumber in eventData"
            return EventReceivedResult.failure_result(error_msg, "MISSING_DOCUMENT_NUMBER")
        
        return EventReceivedResult.success_result(event_id=None, queue_stats={})
    
    def _create_event_entity(self, event_data: Dict[str, Any]) -> Event:
        """Create Event domain entity from raw data."""
        # Create value objects with validation
        event_type = EventType(event_data['eventType'])
        identity_number = IdentityNumber(event_data['identityNumber'])
        document_number = DocumentNumber(event_data['eventData']['documentNumber'])
        
        # Create event entity
        event = Event(
            user_id=event_data['userId'],
            identity_number=identity_number,
            event_type=event_type,
            event_data=event_data['eventData'],
            document_number=document_number
        )
        
        return event 