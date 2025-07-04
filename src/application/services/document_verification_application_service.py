"""
Document Verification Application Service - Application Layer
Clean Architecture - Orchestrates document verification use cases
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..use_cases.process_document_use_case import ProcessDocumentUseCase, ValidationResult
from ..use_cases.receive_event_use_case import ReceiveEventUseCase
from domain.entities.event import Event
from domain.entities.user import User, EducationHistory
from domain.repositories.event_repository import IEventRepository


class DocumentVerificationStats:
    """Statistics for document verification operations."""
    
    def __init__(self):
        self.total_processed = 0
        self.successful_verifications = 0
        self.failed_verifications = 0
        self.skipped_documents = 0
        self.backend_updates = 0
        self.failed_backend_updates = 0
    
    def add_successful_verification(self) -> None:
        """Record successful verification."""
        self.successful_verifications += 1
        self.total_processed += 1
    
    def add_failed_verification(self) -> None:
        """Record failed verification."""
        self.failed_verifications += 1
        self.total_processed += 1
    
    def add_skipped_document(self) -> None:
        """Record skipped document."""
        self.skipped_documents += 1
    
    def add_backend_update(self, success: bool) -> None:
        """Record backend update attempt."""
        if success:
            self.backend_updates += 1
        else:
            self.failed_backend_updates += 1
    
    def get_success_rate(self) -> float:
        """Get verification success rate."""
        if self.total_processed == 0:
            return 0.0
        return (self.successful_verifications / self.total_processed) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_processed": self.total_processed,
            "successful_verifications": self.successful_verifications,
            "failed_verifications": self.failed_verifications,
            "skipped_documents": self.skipped_documents,
            "backend_updates": self.backend_updates,
            "failed_backend_updates": self.failed_backend_updates,
            "success_rate": f"{self.get_success_rate():.1f}%"
        }


class DocumentVerificationApplicationService:
    """
    Document Verification Application Service.
    
    Single Responsibility: Coordinates document verification workflow
    Open/Closed: Can be extended with new verification strategies
    Dependency Inversion: Depends on use cases and repositories
    """
    
    def __init__(
        self,
        event_repository: IEventRepository,
        receive_event_use_case: ReceiveEventUseCase,
        process_document_use_case: ProcessDocumentUseCase
    ):
        """Initialize with dependencies."""
        self._event_repository = event_repository
        self._receive_event_use_case = receive_event_use_case
        self._process_document_use_case = process_document_use_case
        self.logger = logging.getLogger(__name__)
    
    def process_verification_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single verification event.
        
        Converts raw event data to event and processes it.
        
        Args:
            event_data: Raw event data
            
        Returns:
            Processing result dictionary
        """
        try:
            self.logger.info(f"🎯 Processing verification event")
            
            # Validate event data
            validation_error = self._validate_event_data(event_data)
            if validation_error:
                return {
                    "success": False,
                    "message": f"Event validation failed: {validation_error}",
                    "error_code": "VALIDATION_ERROR"
                }
            
            # Create event from data
            receive_result = self._receive_event_use_case.execute(event_data)
            if not receive_result.success:
                return {
                    "success": False,
                    "message": receive_result.error_message,
                    "error_code": receive_result.error_code
                }
            
            # Get the created event
            event = self._event_repository.find_by_id(receive_result.event_id)
            if not event:
                return {
                    "success": False,
                    "message": "Event not found after creation",
                    "error_code": "EVENT_NOT_FOUND"
                }
            
            # Process the document
            validation_result = self._process_document_use_case.execute(event)
            
            return {
                "success": True,
                "event_id": event.id,
                "verification_result": {
                    "success": validation_result.success,
                    "message": validation_result.message,
                    "files": validation_result.files
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Verification event processing error: {str(e)}"
            self.logger.error(f"💥 {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "error_code": "PROCESSING_ERROR"
            }
    
    def process_user_documents(self, user: User) -> DocumentVerificationStats:
        """
        Process all unverified documents for a user.
        
        Args:
            user: User with education histories to process
            
        Returns:
            Processing statistics
        """
        stats = DocumentVerificationStats()
        
        try:
            self.logger.info(f"👤 Processing documents for user: {user.user_id}")
            
            unverified_educations = user.get_unverified_educations()
            
            if not unverified_educations:
                self.logger.info(f"📭 No unverified documents for user: {user.user_id}")
                return stats
            
            for education in unverified_educations:
                try:
                    self._process_education_document(user, education, stats)
                except Exception as e:
                    self.logger.error(f"💥 Error processing education {education.id}: {str(e)}")
                    stats.add_failed_verification()
            
            self.logger.info(f"📊 User processing completed: {stats.to_dict()}")
            return stats
            
        except Exception as e:
            self.logger.error(f"💥 User document processing error: {str(e)}")
            return stats
    
    def process_batch_events(self, batch_size: int = 10) -> Dict[str, Any]:
        """
        Process a batch of pending events.
        
        Args:
            batch_size: Maximum number of events to process
            
        Returns:
            Batch processing result
        """
        try:
            self.logger.info(f"🚀 Processing event batch (size: {batch_size})")
            
            pending_events = self._event_repository.find_pending_events(limit=batch_size)
            
            if not pending_events:
                return {
                    "success": True,
                    "message": "No pending events found",
                    "processed_count": 0,
                    "successful_count": 0,
                    "failed_count": 0
                }
            
            processed_count = 0
            successful_count = 0
            failed_count = 0
            
            for event in pending_events:
                try:
                    result = self._process_document_use_case.execute(event)
                    processed_count += 1
                    
                    if result.success:
                        successful_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    self.logger.error(f"💥 Error processing event {event.id}: {str(e)}")
                    failed_count += 1
                    processed_count += 1
            
            return {
                "success": True,
                "message": f"Batch processing completed",
                "processed_count": processed_count,
                "successful_count": successful_count,
                "failed_count": failed_count,
                "success_rate": f"{(successful_count / processed_count * 100) if processed_count > 0 else 0:.1f}%",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Batch processing error: {str(e)}"
            self.logger.error(f"💥 {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "error_code": "BATCH_PROCESSING_ERROR"
            }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        try:
            return self._event_repository.get_statistics()
        except Exception as e:
            self.logger.error(f"💥 Error getting statistics: {str(e)}")
            return {}
    
    def _process_education_document(
        self, 
        user: User, 
        education: EducationHistory, 
        stats: DocumentVerificationStats
    ) -> None:
        """Process a single education document."""
        try:
            # Skip if already verified
            if education.is_verified():
                stats.add_skipped_document()
                return
            
            # Validate document data
            if not education.document_number or len(education.document_number) < 3:
                self.logger.warning(f"⚠️ Invalid document number for education {education.id}")
                stats.add_skipped_document()
                return
            
            self.logger.info(f"🔍 Processing education document: {education.id}")
            
            # Create event data
            event_data = {
                "userId": user.user_id,
                "identityNumber": str(user.user_cv.identity_number),
                "eventType": "UserEducationCreated",
                "eventData": {
                    "id": education.id,
                    "documentNumber": education.document_number
                }
            }
            
            # Process the event
            result = self.process_verification_event(event_data)
            
            if result["success"]:
                verification_result = result["verification_result"]
                if verification_result["success"]:
                    education.mark_as_verified()
                    stats.add_successful_verification()
                else:
                    education.mark_as_failed()
                    stats.add_failed_verification()
            else:
                education.mark_as_failed()
                stats.add_failed_verification()
                
        except Exception as e:
            self.logger.error(f"💥 Education document processing error: {str(e)}")
            education.mark_as_failed()
            stats.add_failed_verification()
    
    def _validate_event_data(self, event_data: Dict[str, Any]) -> str:
        """
        Validate event data structure.
        
        Args:
            event_data: Event data to validate
            
        Returns:
            Error message if validation fails, None if successful
        """
        required_fields = ["userId", "identityNumber", "eventType", "eventData"]
        
        for field in required_fields:
            if field not in event_data:
                return f"Missing required field: {field}"
            
            if not event_data[field]:
                return f"Empty value for field: {field}"
        
        # Validate identity number
        identity_number = event_data["identityNumber"]
        if len(identity_number) != 11:
            return f"Invalid identity number length: {len(identity_number)}"
        
        # Validate event data structure
        event_data_obj = event_data["eventData"]
        if "documentNumber" not in event_data_obj:
            return "Missing documentNumber in eventData"
        
        document_number = event_data_obj["documentNumber"]
        if len(document_number) < 3:
            return f"Invalid document number: too short"
        
        return None 