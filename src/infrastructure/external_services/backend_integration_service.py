"""
Backend Integration Service - Infrastructure Layer
Clean Architecture - Backend API integration implementation
"""
import logging
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

from application.use_cases.process_document_use_case import IBackendNotifier, ValidationResult
from domain.entities.event import Event


class BackendIntegrationService(IBackendNotifier):
    """
    Backend API integration service.
    
    Implements IBackendNotifier interface (Liskov Substitution Principle)
    Single Responsibility: Only handles backend API communication
    """
    
    def __init__(self, base_url: str, email: str, password: str, timeout: int = 30):
        """
        Initialize backend integration service.
        
        Args:
            base_url: Backend API base URL
            email: Authentication email
            password: Authentication password
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        self.timeout = timeout
        self.logger = logging.getLogger("backend")
        self._auth_token: Optional[str] = None
        self.session = requests.Session()
    
    def notify_verification_result(self, event: Event, result: ValidationResult) -> bool:
        """
        Notify backend about verification result.
        
        Args:
            event: The processed event
            result: Validation result
            
        Returns:
            True if notification was successful
        """
        try:
            self.logger.info(f"📡 Notifying backend about event: {event.id}")
            self.logger.info(f"📊 Validation result: {result.success}")
            
            # Authenticate if needed
            if not self._authenticate():
                return False
            
            # Determine document type and endpoint
            endpoint, document_id = self._get_update_endpoint_and_id(event)
            if not endpoint:
                self.logger.error(f"❌ Cannot determine update endpoint for event type: {event.event_type}")
                return False
            
            # Prepare update data
            update_data = self._prepare_update_data(event, result, document_id)
            
            # Send update request
            success = self._send_update_request(endpoint, update_data)
            
            if success:
                self.logger.info(f"✅ Backend notification successful for event: {event.id}")
            else:
                self.logger.error(f"❌ Backend notification failed for event: {event.id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"💥 Backend notification error: {str(e)}")
            return False
    
    def update_education_document(
        self, 
        user_id: str, 
        education_id: str, 
        document_number: str,
        is_verified: bool, 
        description: str
    ) -> bool:
        """
        Update education document verification status.
        
        Args:
            user_id: User identifier
            education_id: Education document identifier
            document_number: Document barcode number
            is_verified: Verification result
            description: Description of verification
            
        Returns:
            True if update was successful
        """
        try:
            if not self._authenticate():
                return False
            
            endpoint = f"{self.base_url}/api/UserEducation/UpdateDocumentVerification"
            
            data = {
                "userId": user_id,
                "educationId": education_id,
                "documentNumber": document_number,
                "documentVerified": is_verified,
                "verificationDescription": description,
                "verifiedAt": datetime.now().isoformat()
            }
            
            return self._send_update_request(endpoint, data)
            
        except Exception as e:
            self.logger.error(f"💥 Education document update error: {str(e)}")
            return False
    
    def update_security_document(
        self, 
        user_id: str, 
        security_id: str, 
        document_number: str,
        is_verified: bool, 
        description: str
    ) -> bool:
        """
        Update security document verification status.
        
        Args:
            user_id: User identifier
            security_id: Security document identifier
            document_number: Document barcode number
            is_verified: Verification result
            description: Description of verification
            
        Returns:
            True if update was successful
        """
        try:
            if not self._authenticate():
                return False
            
            endpoint = f"{self.base_url}/api/UserSecurity/UpdateDocumentVerification"
            
            data = {
                "userId": user_id,
                "securityId": security_id,
                "documentNumber": document_number,
                "documentVerified": is_verified,
                "verificationDescription": description,
                "verifiedAt": datetime.now().isoformat()
            }
            
            return self._send_update_request(endpoint, data)
            
        except Exception as e:
            self.logger.error(f"💥 Security document update error: {str(e)}")
            return False
    
    def _authenticate(self) -> bool:
        """Authenticate with backend API."""
        try:
            if self._auth_token:
                # Token exists, assume it's valid for now
                # TODO: Implement token validation/refresh
                return True
            
            auth_endpoint = f"{self.base_url}/api/Auth/login"
            
            auth_data = {
                "email": self.email,
                "password": self.password
            }
            
            self.logger.info(f"🔐 Authenticating with backend...")
            
            response = requests.post(
                auth_endpoint,
                json=auth_data,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                auth_result = response.json()
                self._auth_token = auth_result.get('token')
                if self._auth_token:
                    self.logger.info("✅ Backend authentication successful")
                    return True
                else:
                    self.logger.error("❌ No token in authentication response")
                    return False
            else:
                self.logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"💥 Authentication request error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"💥 Authentication error: {str(e)}")
            return False
    
    def _get_update_endpoint_and_id(self, event: Event) -> tuple[Optional[str], Optional[str]]:
        """Get appropriate update endpoint and document ID for event."""
        event_type_str = str(event.event_type)
        
        if "Education" in event_type_str:
            endpoint = f"{self.base_url}/api/UserEducation/UpdateDocumentVerification"
            document_id = event.event_data.get('id', event.user_id)
            return endpoint, document_id
        elif "Security" in event_type_str:
            endpoint = f"{self.base_url}/api/UserSecurity/UpdateDocumentVerification"
            document_id = event.event_data.get('id', event.user_id)
            return endpoint, document_id
        else:
            return None, None
    
    def _prepare_update_data(self, event: Event, result: ValidationResult, document_id: str) -> Dict[str, Any]:
        """Prepare update data for backend request."""
        return {
            "userId": event.user_id,
            "documentId": document_id,
            "documentNumber": str(event.document_number) if event.document_number else "",
            "documentVerified": result.success,
            "verificationDescription": result.message or ("Verification successful" if result.success else "Verification failed"),
            "verifiedAt": datetime.now().isoformat(),
            "files": result.files,
            "eventId": event.id
        }
    
    def _send_update_request(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Send update request to backend."""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._auth_token}"
            }
            
            self.logger.info(f"📤 Sending update to: {endpoint}")
            self.logger.debug(f"📋 Update data: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                endpoint,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201, 204]:
                self.logger.info(f"✅ Backend update successful: {response.status_code}")
                return True
            else:
                self.logger.error(f"❌ Backend update failed: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"💥 Backend update request error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"💥 Backend update error: {str(e)}")
            return False
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from backend.
        
        Args:
            user_id: User identifier
            
        Returns:
            User data dictionary or None if not found
        """
        try:
            if not self._authenticate():
                return None
            
            endpoint = f"{self.base_url}/api/User/{user_id}"
            
            headers = {
                "Authorization": f"Bearer {self._auth_token}"
            }
            
            response = requests.get(
                endpoint,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"❌ User data fetch failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"💥 User data fetch error: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """Test backend connection."""
        try:
            endpoint = f"{self.base_url}/api/health"
            
            response = requests.get(endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                self.logger.info("✅ Backend connection test successful")
                return True
            else:
                self.logger.error(f"❌ Backend connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"💥 Backend connection test error: {str(e)}")
            return False 