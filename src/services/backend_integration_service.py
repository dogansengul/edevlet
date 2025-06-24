"""
Backend integration service for API operations.
"""
from typing import List, Optional

from ..core.backend_service import BackendAPIClient
from ..models.entities import User
from ..exceptions import BackendAPIError, AuthenticationError
from ..constants import ErrorType


class BackendIntegrationService:
    """Service for handling backend API integration."""
    
    def __init__(self, base_url: str, email: str, password: str):
        """
        Initialize the service.
        
        Args:
            base_url: Backend API base URL
            email: Authentication email
            password: Authentication password
        """
        self.client = BackendAPIClient(base_url, email, password)
    
    def fetch_users_for_verification(self) -> Optional[List[User]]:
        """
        Fetch users that have documents pending verification.
        
        Returns:
            List of User objects or None if failed
        """
        try:
            items = self.client.fetch_documents_for_verification()
            
            if items is None:
                return None
            
            users = []
            for item in items:
                try:
                    user = User.from_dict(item)
                    users.append(user)
                except Exception as e:
                    print(f"Error parsing user data: {str(e)}")
                    continue
            
            return users
            
        except Exception as e:
            print(f"Error fetching users for verification: {str(e)}")
            return None
    
    def update_education_document_status(
        self, 
        education_id: int, 
        user_id: int, 
        document_number: str,
        is_verified: bool, 
        description: str
    ) -> bool:
        """
        Update education document verification status.
        
        Args:
            education_id: Education document ID
            user_id: User ID
            document_number: Document number (barcode)
            is_verified: Whether document is verified
            description: Human readable description
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            return self.client.update_education_history(
                education_id=education_id,
                user_id=user_id,
                document_number=document_number,
                document_verified_status=is_verified,
                hr_description=description
            )
        except Exception as e:
            print(f"Error updating education document status: {str(e)}")
            return False
    
    def update_security_document_status(
        self, 
        security_id: str,
        user_id: int, 
        document_number: str,
        is_verified: bool, 
        description: str
    ) -> bool:
        """
        Update security document verification status.
        
        Args:
            security_id: Security document ID
            user_id: User ID
            document_number: Document number (barcode)
            is_verified: Whether document is verified
            description: Human readable description
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            return self.client.update_user_security_document(
                security_id=security_id,
                user_id=user_id,
                document_number=document_number,
                document_verified_status=is_verified,
                hr_description=description
            )
        except Exception as e:
            print(f"Error updating security document status: {str(e)}")
            return False

    def update_document_by_event_type(
        self,
        event_type: str,
        document_id: str,
        user_id: str,
        document_number: str,
        is_verified: bool,
        description: str,
        **kwargs
    ) -> bool:
        """
        Update document status based on event type.
        
        Args:
            event_type: Type of event (UserEducationCreated, UserSecurityCreated, etc.)
            document_id: Document ID 
            user_id: User ID
            document_number: Document number (barcode)
            is_verified: Whether document is verified
            description: Human readable description
            **kwargs: Additional parameters specific to document type
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            return self.client.update_document_by_event_type(
                event_type=event_type,
                document_id=document_id,
                user_id=user_id,
                document_number=document_number,
                document_verified_status=is_verified,
                hr_description=description,
                **kwargs
            )
        except Exception as e:
            print(f"Error updating document by event type: {str(e)}")
            return False
    
    def close(self):
        """Close the backend connection."""
        try:
            self.client.close()
        except Exception as e:
            print(f"Error closing backend connection: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the backend connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to fetch a small amount of data to test connection
            result = self.client.fetch_documents_for_verification()
            return result is not None
        except Exception as e:
            print(f"Backend connection test failed: {str(e)}")
            return False
