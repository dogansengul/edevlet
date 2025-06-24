"""
Document processing service for handling document verification workflow.
"""
import json
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any

from ..models.entities import User, EducationHistory, ValidationResult, ProcessingStats
from ..services.document_verification_service import DocumentVerificationService
from ..services.backend_integration_service import BackendIntegrationService
from ..utils.logging import LogManager
from ..constants import SUCCESS_MESSAGES, ERROR_MESSAGES
from ..config.config import Config


class DocumentProcessingService:
    """Service for processing documents through the complete workflow."""
    
    def __init__(
        self, 
        verification_service: DocumentVerificationService,
        backend_service: BackendIntegrationService,
        log_manager: LogManager
    ):
        """
        Initialize the service.
        
        Args:
            verification_service: Document verification service
            backend_service: Backend integration service
            log_manager: Log manager for operations
        """
        self.verification_service = verification_service
        self.backend_service = backend_service
        self.log_manager = log_manager
        
        # Failed updates queue configuration
        self.failed_updates_file = "failed_updates.json"
    
    def process_verification_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a single verification event directly.
        
        This method provides a streamlined approach for event-driven processing,
        bypassing the User object creation overhead.
        
        Args:
            event_data: Dictionary containing verification data:
                {
                    "identityNumber": "12345678901",
                    "documentNumber": "BARCODE12345", 
                    "userId": "guid-here",
                    "educationId": "cv-guid-here",  # For education events
                    "securityId": "security-guid-here",  # For security events  
                    "eventType": "UserEducationCreated" # or "UserSecurityCreated"
                }
                
        Returns:
            bool: True if verification and backend update were successful, False otherwise
        """
        try:
            # Validate required fields
            validation_error = self._validate_event_data(event_data)
            if validation_error:
                print(f"❌ Event validation error: {validation_error}")
                self.log_manager.log_processing_cycle(f"Event validation failed: {validation_error}", "ERROR")
                return False
            
            identity_number = event_data["identityNumber"]
            document_number = event_data["documentNumber"]
            user_id = event_data["userId"]
            event_type = event_data.get("eventType", "")
            
            # Determine document ID based on event type
            if "Education" in event_type:
                document_id = event_data.get("educationId", user_id)  # Fallback to userId
                document_type_display = "Eğitim"
            elif "Security" in event_type:
                document_id = event_data.get("securityId", user_id)  # Fallback to userId
                document_type_display = "Güvenlik"
            else:
                print(f"❌ Bilinmeyen event tipi: {event_type}")
                self.log_manager.log_processing_cycle(f"Unknown event type: {event_type}", "ERROR")
                return False
            
            print(f"\n🎯 Event işleme başlatılıyor:")
            print(f"   👤 User ID: {user_id}")
            print(f"   🆔 TC Kimlik: {identity_number}")
            print(f"   📄 Belge No: {document_number}")
            print(f"   📋 {document_type_display} Belge ID: {document_id}")
            print(f"   🏷️ Event Tipi: {event_type}")
            
            # Perform eDevlet verification
            print(f"   🔍 E-Devlet doğrulaması başlatılıyor...")
            result = self.verification_service.verify_document(
                barcode=document_number,
                tc_kimlik_no=identity_number
            )
            
            # Log the operation
            self.log_manager.log_operation(identity_number, document_number, result)
            
            # Prepare description based on result
            if result.success:
                description = SUCCESS_MESSAGES["verification"]
                status_emoji = "✅"
                status_text = "Başarılı"
            else:
                description = result.error.message if result.error else ERROR_MESSAGES["verification_failed"]
                status_emoji = "❌"
                status_text = "Başarısız"
            
            print(f"   {status_emoji} Doğrulama sonucu: {status_text}")
            print(f"   📤 Backend'e {document_type_display.lower()} belgesi sonucu gönderiliyor...")
            
            # Update backend with result using new event-driven method
            update_success = self.backend_service.update_document_by_event_type(
                event_type=event_type,
                document_id=document_id,
                user_id=user_id,
                document_number=document_number,
                is_verified=result.success,
                description=description
            )
            
            if update_success:
                print(f"   ✅ {SUCCESS_MESSAGES['update']}")
                self.log_manager.log_processing_cycle(f"Event başarıyla işlendi: {user_id} - {document_number} ({event_type})")
                return True
            else:
                print(f"   ❌ {ERROR_MESSAGES['backend_update_failed']}")
                self.log_manager.log_processing_cycle(f"Backend güncelleme başarısız: {user_id} - {document_number} ({event_type})", "ERROR")
                
                # Add to failed updates queue for retry
                failed_update_data = {
                    **event_data,
                    "verificationResult": {
                        "success": result.success,
                        "description": description,
                        "files": result.files,
                        "verifiedAt": datetime.now().isoformat()
                    },
                    "failedAt": datetime.now().isoformat(),
                    "retryCount": 0
                }
                
                self._add_to_failed_updates_queue(failed_update_data)
                print(f"   🔄 Update failed updates queue'ya eklendi")
                
                # Return True because verification was successful, only backend update failed
                return True
                
        except Exception as e:
            error_msg = f"Event processing error: {str(e)}"
            print(f"   ❌ HATA: {error_msg}")
            self.log_manager.log_error(e, f"Event processing failed for {event_data.get('userId', 'unknown')}")
            return False
    
    def _validate_event_data(self, event_data: Dict[str, Any]) -> str:
        """
        Validate event data dictionary.
        
        Args:
            event_data: Event data to validate
            
        Returns:
            Error message if validation fails, None if successful
        """
        required_fields = ["identityNumber", "documentNumber", "userId", "eventType"]
        
        for field in required_fields:
            if field not in event_data:
                return f"Missing required field: {field}"
            
            if not event_data[field]:
                return f"Empty value for required field: {field}"
        
        # Additional validation
        identity_number = event_data["identityNumber"]
        if len(identity_number) != 11:
            return f"Invalid identity number length: {len(identity_number)} (expected 11)"
        
        document_number = event_data["documentNumber"]
        if len(document_number) < 3:
            return f"Invalid document number length: {len(document_number)} (too short)"
        
        # Validate event type and required document ID field
        event_type = event_data["eventType"]
        if "Education" in event_type:
            if "educationId" not in event_data or not event_data["educationId"]:
                return "Missing or empty educationId for education event"
        elif "Security" in event_type:
            if "securityId" not in event_data or not event_data["securityId"]:
                return "Missing or empty securityId for security event"
        else:
            return f"Unknown event type: {event_type}"
        
        return None
    
    def _add_to_failed_updates_queue(self, failed_update_data: Dict[str, Any]):
        """Add failed update to the retry queue."""
        try:
            # Read existing failed updates
            failed_updates = []
            if os.path.exists(self.failed_updates_file):
                try:
                    with open(self.failed_updates_file, 'r', encoding='utf-8') as f:
                        failed_updates = json.load(f)
                except json.JSONDecodeError:
                    self.log_manager.log_processing_cycle("⚠️ Failed updates dosyası bozuk, yeni başlatılıyor.", "WARNING")
                    failed_updates = []
            
            # Add new failed update
            failed_updates.append(failed_update_data)
            
            # Write back to file
            with open(self.failed_updates_file, 'w', encoding='utf-8') as f:
                json.dump(failed_updates, f, indent=2, ensure_ascii=False)
            
            self.log_manager.log_processing_cycle(f"Failed update queue'ya eklendi: {failed_update_data.get('userId', 'unknown')}")
            
        except Exception as e:
            self.log_manager.log_error(e, "Failed update queue'ya ekleme hatası")
    
    def get_failed_updates(self) -> List[Dict[str, Any]]:
        """Get all failed updates from the queue."""
        try:
            if not os.path.exists(self.failed_updates_file):
                return []
            
            with open(self.failed_updates_file, 'r', encoding='utf-8') as f:
                failed_updates = json.load(f)
            
            return failed_updates
            
        except Exception as e:
            self.log_manager.log_error(e, "Failed updates okuma hatası")
            return []
    
    def retry_failed_update(self, failed_update_data: Dict[str, Any]) -> bool:
        """Retry a single failed update."""
        try:
            # Extract verification result
            verification_result = failed_update_data.get("verificationResult", {})
            
            # Extract event data
            event_data = {
                "identityNumber": failed_update_data.get("identityNumber"),
                "documentNumber": failed_update_data.get("documentNumber"),
                "userId": failed_update_data.get("userId"),
                "educationId": failed_update_data.get("educationId")
            }
            
            print(f"\n🔄 Failed update retry başlatılıyor:")
            print(f"   👤 User ID: {event_data['userId']}")
            print(f"   📄 Belge No: {event_data['documentNumber']}")
            print(f"   🔁 Retry Count: {failed_update_data.get('retryCount', 0) + 1}")
            
            # Attempt backend update
            update_success = self.backend_service.update_education_document_status(
                education_id=event_data["educationId"],
                user_id=event_data["userId"],
                document_number=event_data["documentNumber"],
                is_verified=verification_result.get("success", False),
                description=verification_result.get("description", "Retry attempt")
            )
            
            if update_success:
                print(f"   ✅ Failed update retry başarılı!")
                self.log_manager.log_processing_cycle(f"Failed update retry başarılı: {event_data['userId']} - {event_data['documentNumber']}")
                return True
            else:
                print(f"   ❌ Failed update retry başarısız")
                self.log_manager.log_processing_cycle(f"Failed update retry başarısız: {event_data['userId']} - {event_data['documentNumber']}", "ERROR")
                return False
                
        except Exception as e:
            self.log_manager.log_error(e, f"Failed update retry hatası: {failed_update_data.get('userId', 'unknown')}")
            return False
    
    def remove_failed_update(self, failed_update_data: Dict[str, Any]):
        """Remove a failed update from the queue after successful retry."""
        try:
            # Read all failed updates
            failed_updates = self.get_failed_updates()
            
            # Find and remove the specific update
            updated_failed_updates = []
            for update in failed_updates:
                # Match by userId and documentNumber and failedAt timestamp
                if not (update.get("userId") == failed_update_data.get("userId") and 
                       update.get("documentNumber") == failed_update_data.get("documentNumber") and
                       update.get("failedAt") == failed_update_data.get("failedAt")):
                    updated_failed_updates.append(update)
            
            # Write back the updated list
            with open(self.failed_updates_file, 'w', encoding='utf-8') as f:
                json.dump(updated_failed_updates, f, indent=2, ensure_ascii=False)
            
            self.log_manager.log_processing_cycle(f"Failed update kaldırıldı: {failed_update_data.get('userId', 'unknown')}")
            
        except Exception as e:
            self.log_manager.log_error(e, "Failed update kaldırma hatası")
    
    def process_user(self, user: User) -> ProcessingStats:
        """
        Process all pending documents for a user.
        
        Args:
            user: User object containing documents to process
            
        Returns:
            ProcessingStats: Statistics for this user's processing
        """
        stats = ProcessingStats()
        
        try:
            print(f"Kullanıcı ID: {user.user_id}, TC Kimlik No: {user.user_cv.identity_number}")
            
            # Process education documents
            if user.education_histories:
                print(f"{len(user.education_histories)} eğitim belgesi bulundu.")
                self._process_education_documents(user, stats)
            else:
                print("Eğitim belgesi bulunamadı.")
            
            # Process security documents (if structure is known)
            if user.user_security:
                print("Güvenlik belgeleri bulundu ancak henüz işlenmiyor (yapı belirsiz).")
                # TODO: Implement security document processing when structure is clear
            
            stats.increment_processed_users()
            
        except Exception as e:
            self.log_manager.log_error(e, f"User processing error for user {user.user_id}")
            print(f"HATA: Kullanıcı işleme hatası: {str(e)}")
        
        return stats
    
    def _process_education_documents(self, user: User, stats: ProcessingStats):
        """Process education documents for a user."""
        for edu_index, edu_doc in enumerate(user.education_histories, 1):
            try:
                print(f"\n  Eğitim belgesi {edu_index}/{len(user.education_histories)} kontrol ediliyor...")
                
                # Check if document verification is needed
                if self._should_verify_document(edu_doc):
                    success = self._process_single_education_document(user, edu_doc, stats)
                    if success:
                        stats.add_successful_verification()
                    else:
                        stats.add_failed_verification()
                else:
                    print(f"  {ERROR_MESSAGES['already_verified']}")
                    stats.add_skipped_document()
                    
            except Exception as e:
                self.log_manager.log_error(e, f"Education document processing error for document {edu_doc.id}")
                print(f"  HATA: Eğitim belgesi işleme hatası: {str(e)}")
                stats.add_failed_verification()
    
    def _should_verify_document(self, edu_doc: EducationHistory) -> bool:
        """
        Check if document needs verification based on configuration.
        
        Uses Config.PROCESS_DOCUMENTS_CONFIG to determine which documents to process:
        - null/None: Unverified documents
        - false: Failed/invalid documents  
        - true: Already verified documents (for re-verification)
        
        Returns:
            True if document needs verification, False otherwise
        """
        config = Config.PROCESS_DOCUMENTS_CONFIG
        
        if edu_doc.document_verified is None:
            should_process = config.get("process_null_documents", True)
            status_text = "null (doğrulanmamış)"
        elif edu_doc.document_verified is True:
            should_process = config.get("process_true_documents", False)
            status_text = "true (zaten doğrulanmış)"
        else:  # document_verified is False
            should_process = config.get("process_false_documents", False)
            status_text = "false (başarısız/geçersiz)"
        
        action_text = "işlenecek" if should_process else "atlanacak"
        print(f"  Belge doğrulama durumu: {status_text} - {action_text}")
        
        return should_process
    
    def _process_single_education_document(
        self, 
        user: User, 
        edu_doc: EducationHistory, 
        stats: ProcessingStats
    ) -> bool:
        """
        Process a single education document.
        
        This method now uses the new event-driven approach for consistency.
        
        Returns:
            True if processing was successful, False otherwise
        """
        # Validate required data
        validation_error = self._validate_education_document_data(edu_doc)
        if validation_error:
            print(f"  HATA: {validation_error}")
            return False
        
        print(f"  Eğitim ID: {edu_doc.id}, Barkod: {edu_doc.document_number}")
        
        # Convert to event data format and use the new method
        event_data = {
            "identityNumber": user.user_cv.identity_number,
            "documentNumber": edu_doc.document_number,
            "userId": str(user.user_id),
            "educationId": str(edu_doc.id)
        }
        
        # Use the new streamlined processing method
        return self.process_verification_event(event_data)
    
    def _validate_education_document_data(self, edu_doc: EducationHistory) -> str:
        """
        Validate education document data.
        
        Returns:
            Error message if validation fails, None if successful
        """
        if not edu_doc.id:
            return ERROR_MESSAGES["no_education_id"]
        
        if not edu_doc.document_number:
            return ERROR_MESSAGES["no_barcode"]
        
        return None

