"""
User Entity - Domain Layer
Clean Architecture - User domain entity with business logic
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..value_objects.identity_number import IdentityNumber


class UserCv:
    """User CV value object."""
    
    def __init__(self, identity_number: IdentityNumber):
        """Initialize user CV with identity number."""
        self.identity_number = identity_number
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "identity_number": str(self.identity_number)
        }


class EducationHistory:
    """Education history entity."""
    
    def __init__(
        self,
        id: str,
        document_number: str,
        document_verified: Optional[bool] = None,
        verification_date: Optional[datetime] = None
    ):
        """Initialize education history."""
        if not id or not id.strip():
            raise ValueError("Education ID cannot be empty")
        if not document_number or not document_number.strip():
            raise ValueError("Document number cannot be empty")
        
        self.id = id.strip()
        self.document_number = document_number.strip()
        self.document_verified = document_verified
        self.verification_date = verification_date
    
    def mark_as_verified(self) -> None:
        """Mark education document as verified."""
        self.document_verified = True
        self.verification_date = datetime.now()
    
    def mark_as_failed(self) -> None:
        """Mark education document verification as failed."""
        self.document_verified = False
        self.verification_date = datetime.now()
    
    def is_verified(self) -> bool:
        """Check if document is verified."""
        return self.document_verified is True
    
    def requires_verification(self) -> bool:
        """Check if document requires verification."""
        return self.document_verified is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "document_number": self.document_number,
            "document_verified": self.document_verified,
            "verification_date": self.verification_date.isoformat() if self.verification_date else None
        }


class UserSecurity:
    """User security information entity."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize user security with arbitrary data."""
        self.data = data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.data.copy()


class User:
    """
    User Domain Entity.
    
    Represents a system user with education histories and security information.
    Contains business rules for user data management and verification.
    """
    
    def __init__(
        self,
        user_id: str,
        user_cv: UserCv,
        education_histories: Optional[List[EducationHistory]] = None,
        user_security: Optional[UserSecurity] = None
    ):
        """
        Initialize User entity.
        
        Args:
            user_id: Unique user identifier
            user_cv: User CV information
            education_histories: List of education histories
            user_security: User security information
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        self.user_id = user_id.strip()
        self.user_cv = user_cv
        self.education_histories = education_histories or []
        self.user_security = user_security
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_education_history(self, education: EducationHistory) -> None:
        """
        Add education history to user.
        
        Business Rule: Cannot add duplicate education IDs
        
        Args:
            education: Education history to add
        """
        if any(edu.id == education.id for edu in self.education_histories):
            raise ValueError(f"Education history with ID {education.id} already exists")
        
        self.education_histories.append(education)
        self.updated_at = datetime.now()
    
    def get_education_by_id(self, education_id: str) -> Optional[EducationHistory]:
        """
        Get education history by ID.
        
        Args:
            education_id: Education ID to find
            
        Returns:
            Education history if found, None otherwise
        """
        return next(
            (edu for edu in self.education_histories if edu.id == education_id),
            None
        )
    
    def get_unverified_educations(self) -> List[EducationHistory]:
        """
        Get list of unverified education histories.
        
        Business Rule: Unverified means document_verified is None
        
        Returns:
            List of unverified education histories
        """
        return [edu for edu in self.education_histories if edu.requires_verification()]
    
    def get_verified_educations(self) -> List[EducationHistory]:
        """
        Get list of verified education histories.
        
        Returns:
            List of verified education histories
        """
        return [edu for edu in self.education_histories if edu.is_verified()]
    
    def get_failed_educations(self) -> List[EducationHistory]:
        """
        Get list of failed education verifications.
        
        Returns:
            List of failed education histories
        """
        return [edu for edu in self.education_histories if edu.document_verified is False]
    
    def has_pending_verifications(self) -> bool:
        """
        Check if user has pending document verifications.
        
        Returns:
            True if there are unverified documents
        """
        return len(self.get_unverified_educations()) > 0
    
    def get_verification_summary(self) -> Dict[str, int]:
        """
        Get verification summary statistics.
        
        Returns:
            Dictionary with verification counts
        """
        return {
            "total": len(self.education_histories),
            "verified": len(self.get_verified_educations()),
            "failed": len(self.get_failed_educations()),
            "pending": len(self.get_unverified_educations())
        }
    
    def update_security_info(self, security_data: Dict[str, Any]) -> None:
        """
        Update user security information.
        
        Args:
            security_data: New security data
        """
        self.user_security = UserSecurity(security_data)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user to dictionary for serialization.
        
        Returns:
            Dictionary representation of user
        """
        return {
            "user_id": self.user_id,
            "user_cv": self.user_cv.to_dict(),
            "education_histories": [edu.to_dict() for edu in self.education_histories],
            "user_security": self.user_security.to_dict() if self.user_security else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "verification_summary": self.get_verification_summary()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create User from dictionary data.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            User entity
        """
        user_cv_data = data.get('userCv', {})
        identity_number = IdentityNumber(user_cv_data.get('identityNumber', ''))
        user_cv = UserCv(identity_number)
        
        education_histories = []
        for edu_data in data.get('educationHistories', []):
            education = EducationHistory(
                id=edu_data.get('id', ''),
                document_number=edu_data.get('documentNumber', ''),
                document_verified=edu_data.get('documentVerified')
            )
            education_histories.append(education)
        
        user_security = None
        if data.get('userSecurity'):
            user_security = UserSecurity(data['userSecurity'])
        
        user = cls(
            user_id=str(data.get('userId', '')),
            user_cv=user_cv,
            education_histories=education_histories,
            user_security=user_security
        )
        
        return user
    
    def __str__(self) -> str:
        """String representation of user."""
        return f"User({self.user_id}, {len(self.education_histories)} educations)"
    
    def __repr__(self) -> str:
        """Detailed string representation of user."""
        return (
            f"User(user_id='{self.user_id}', "
            f"identity_number='{self.user_cv.identity_number}', "
            f"education_count={len(self.education_histories)})"
        ) 