"""
Data models for the eDevlet automation system.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class DocumentType(Enum):
    """Document type enumeration."""
    EDUCATION = "education"
    SECURITY = "security"


class VerificationStatus(Enum):
    """Document verification status enumeration."""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class EventType(Enum):
    """Event type enumeration for document verification."""
    USER_EDUCATION_CREATED = "UserEducationCreated"
    USER_SECURITY_CREATED = "UserSecurityCreated"


@dataclass
class EventData:
    """Event data model for document verification events."""
    id: str
    document_number: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventData':
        return cls(
            id=data.get('id', ''),
            document_number=data.get('documentNumber', '')
        )


@dataclass 
class VerificationEvent:
    """Verification event model."""
    user_id: str
    identity_number: str
    event_type: str
    event_data: EventData
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationEvent':
        event_info = data.get('event', {})
        return cls(
            user_id=event_info.get('userId', ''),
            identity_number=event_info.get('identityNumber', ''),
            event_type=event_info.get('eventType', ''),
            event_data=EventData.from_dict(event_info.get('eventData', {}))
        )
    
    def get_document_type(self) -> DocumentType:
        """Determine document type based on event type."""
        if "Education" in self.event_type:
            return DocumentType.EDUCATION
        elif "Security" in self.event_type:
            return DocumentType.SECURITY
        else:
            raise ValueError(f"Unknown event type: {self.event_type}")


@dataclass
class UserCv:
    """User CV information model."""
    identity_number: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserCv':
        return cls(
            identity_number=data.get('identityNumber', '')
        )


@dataclass
class EducationHistory:
    """Education history document model."""
    id: int
    document_number: str
    document_verified: Optional[bool]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EducationHistory':
        return cls(
            id=data.get('id'),
            document_number=data.get('documentNumber', ''),
            document_verified=data.get('documentVerified')
        )


@dataclass
class UserSecurity:
    """User security document model."""
    # This can be expanded based on actual structure
    data: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSecurity':
        return cls(data=data or {})


@dataclass
class User:
    """User model containing all user information."""
    user_id: int
    user_cv: UserCv
    education_histories: List[EducationHistory]
    user_security: Optional[UserSecurity] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            user_id=data.get('userId'),
            user_cv=UserCv.from_dict(data.get('userCv', {})),
            education_histories=[
                EducationHistory.from_dict(edu) 
                for edu in data.get('educationHistories', [])
            ],
            user_security=UserSecurity.from_dict(data.get('userSecurity')) 
            if data.get('userSecurity') else None
        )


@dataclass
class ValidationError:
    """Validation error model."""
    error_type: str
    message: str


@dataclass
class ValidationResult:
    """Document validation result model."""
    success: bool
    files: List[str]
    message: Optional[str] = None
    error: Optional[ValidationError] = None
    
    @classmethod
    def success_result(cls, files: List[str], message: str = None) -> 'ValidationResult':
        return cls(
            success=True,
            files=files,
            message=message
        )
    
    @classmethod
    def error_result(cls, error_type: str, message: str, files: List[str] = None) -> 'ValidationResult':
        return cls(
            success=False,
            files=files or [],
            error=ValidationError(error_type=error_type, message=message)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for logging and API calls."""
        result = {
            'success': self.success,
            'files': self.files
        }
        
        if self.message:
            result['message'] = self.message
            
        if self.error:
            result['error'] = {
                'error_type': self.error.error_type,
                'message': self.error.message
            }
            
        return result


@dataclass
class ProcessingStats:
    """Processing statistics model."""
    total_users: int = 0
    processed_users: int = 0
    successful_verifications: int = 0
    failed_verifications: int = 0
    skipped_documents: int = 0
    
    def add_successful_verification(self):
        self.successful_verifications += 1
    
    def add_failed_verification(self):
        self.failed_verifications += 1
    
    def add_skipped_document(self):
        self.skipped_documents += 1
    
    def increment_processed_users(self):
        self.processed_users += 1
    
    def get_summary(self) -> str:
        return (
            f"İşlem Özeti: {self.processed_users}/{self.total_users} kullanıcı işlendi, "
            f"{self.successful_verifications} başarılı, "
            f"{self.failed_verifications} başarısız doğrulama, "
            f"{self.skipped_documents} belge atlandı"
        )
