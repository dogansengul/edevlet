"""
Process Document Use Case - Application Layer
Clean Architecture - Business logic for document processing
"""
import logging
from datetime import datetime
from typing import Protocol, List
from abc import ABC, abstractmethod

from domain.entities.event import Event, EventStatus
from domain.repositories.event_repository import IEventRepository


class ValidationResult:
    """Result of document validation operation."""
    
    def __init__(
        self,
        success: bool,
        message: str = None,
        files: List[str] = None,
        error_code: str = None
    ):
        self.success = success
        self.message = message
        self.files = files or []
        self.error_code = error_code
    
    @classmethod
    def success_result(cls, message: str, files: List[str] = None):
        """Create successful validation result."""
        return cls(success=True, message=message, files=files or [])
    
    @classmethod
    def failure_result(cls, message: str, error_code: str = "VALIDATION_FAILED"):
        """Create failed validation result."""
        return cls(success=False, message=message, error_code=error_code)


class IDocumentValidator(Protocol):
    """
    Document Validator Interface.
    
    Interface Segregation Principle: Small, focused interface
    Dependency Inversion: High-level modules depend on this abstraction
    """
    
    @abstractmethod
    def validate_document(self, document_number: str, identity_number: str) -> ValidationResult:
        """Validate document and return result."""
        pass


class IBackendNotifier(Protocol):
    """
    Backend Notifier Interface.
    
    Interface Segregation Principle: Small, focused interface
    Dependency Inversion: High-level modules depend on this abstraction
    """
    
    @abstractmethod
    def notify_verification_result(self, event: Event, result: ValidationResult) -> bool:
        """Notify backend about verification result."""
        pass


class ProcessDocumentUseCase:
    """
    Use Case for processing document verification.
    
    Single Responsibility: Only handles document processing business logic
    Open/Closed: Can be extended with new validation strategies
    Dependency Inversion: Depends on abstractions (interfaces)
    """
    
    def __init__(
        self,
        event_repository: IEventRepository,
        document_validator: IDocumentValidator,
        backend_notifier: IBackendNotifier
    ):
        """Initialize with dependencies."""
        self._event_repository = event_repository
        self._document_validator = document_validator
        self._backend_notifier = backend_notifier
        self.logger = logging.getLogger(__name__)
    
    def execute(self, event: Event) -> ValidationResult:
        """
        Execute document processing use case.
        
        Business Rules:
        1. Mark event as processing
        2. Validate document through external service
        3. Update event status based on validation result
        4. Notify backend about the result
        5. Return processing result
        
        Args:
            event: Event to process
            
        Returns:
            ValidationResult with processing outcome
        """
        try:
            self.logger.info(f"⚙️ Processing event: {event.id}")
            
            # Business Rule: Mark event as processing
            event.start_processing()
            self._event_repository.update_status(event)
            
            # Business Rule: Validate document
            validation_result = self._document_validator.validate_document(
                document_number=str(event.document_number),
                identity_number=str(event.identity_number)
            )
            
            # Business Rule: Update event status based on validation
            if validation_result.success:
                event.mark_as_processed()
                self.logger.info(f"✅ Document validation successful for event: {event.id}")
            else:
                event.mark_as_failed(validation_result.message)
                self.logger.warning(f"❌ Document validation failed for event: {event.id}")
            
            self._event_repository.update_status(event)
            
            # Business Rule: Notify backend
            try:
                notification_success = self._backend_notifier.notify_verification_result(
                    event, validation_result
                )
                if notification_success:
                    self.logger.info(f"📡 Backend notified successfully for event: {event.id}")
                else:
                    self.logger.warning(f"⚠️ Backend notification failed for event: {event.id}")
            except Exception as e:
                self.logger.error(f"💥 Backend notification error for event {event.id}: {str(e)}")
            
            return validation_result
            
        except Exception as e:
            error_msg = f"Error processing event {event.id}: {str(e)}"
            self.logger.error(f"💥 {error_msg}")
            
            # Mark event as failed
            try:
                event.mark_as_failed(error_msg)
                self._event_repository.update_status(event)
            except Exception as save_error:
                self.logger.error(f"💥 Failed to save error state: {str(save_error)}")
            
            return ValidationResult.failure_result(
                message=error_msg,
                error_code="PROCESSING_ERROR"
            )
    
    def can_process_event(self, event: Event) -> bool:
        """
        Check if event can be processed.
        
        Args:
            event: Event to check
            
        Returns:
            True if event can be processed
        """
        return event.can_be_processed() 