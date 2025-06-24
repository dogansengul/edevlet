import logging
import requests
from typing import Optional, Dict, Any, List
import json


class BackendAPIClient:
    """
    A client for interacting with the backend API.
    Manages authentication, token refresh, and various API operations.
    """
    
    def __init__(self, base_url: str, email: str, password: str):
        """
        Initialize the BackendAPIClient.
        
        Args:
            base_url (str): The base URL for the API
            email (str): User email for authentication
            password (str): User password for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        
        # Set up logger
        self.logger = logging.getLogger(__name__)
        
        # Configure session for reusing connections
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _is_token_expired(self) -> bool:
        """
        Check if the current access token is expired.
        
        Returns:
            bool: True if token is expired or doesn't exist, False otherwise
        """
        if not self.access_token:
            return True
        # Simplified: assume token is valid if it exists
        return False
    
    def is_token_valid(self) -> bool:
        """
        Check if the current access token is valid and not expiring soon.
        
        Returns:
            bool: True if token exists, False otherwise
        """
        return bool(self.access_token)
    
    def ensure_token_valid(self) -> bool:
        """
        Ensure the client has a valid token, refreshing or logging in as needed.
        
        Returns:
            bool: True if a valid token is ensured, False otherwise
        """
        if self.is_token_valid():
            self.logger.debug("Current token is still valid")
            return True
        
        self.logger.info("Token is invalid or expiring soon, attempting to refresh")
        
        # If we have an access token, try to refresh it first
        if self.access_token:
            if self.refresh_access_token():
                self.logger.info("Successfully refreshed token")
                return True
            else:
                self.logger.warning("Token refresh failed, attempting to login")
        else:
            self.logger.info("No access token present, attempting to login")
        
        # If refresh failed or no token was present, try to login
        if self.login():
            self.logger.info("Successfully logged in with new token")
            return True
        else:
            self.logger.error("Failed to ensure valid token - both refresh and login failed")
            return False
    
    def _update_auth_header(self):
        """Update the session headers with the current access token."""
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
    
    def login(self) -> bool:
        """
        Authenticate with the backend API using email and password.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            login_data = {
                'email': self.email,
                'password': self.password,
                'authenticatorCode': 'string'
            }
            
            # Set specific headers for login request
            headers = {
                'accept': '*/*',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f'{self.base_url}/api/Auth/Login',
                json=login_data,
                headers=headers
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract access token from response
                access_token_data = response_data.get('accessToken', {})
                self.access_token = access_token_data.get('token')
                
                # Extract refresh token if available
                self.refresh_token = response_data.get('refreshToken')
                
                self._update_auth_header()
                self.logger.info("Successfully logged in to backend API")
                return True
            else:
                self.logger.error(f"Login failed with status code: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during login: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {str(e)}")
            return False
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using the current access token.
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        try:
            if not self.access_token:
                self.logger.warning("No access token available, need to login again")
                return self.login()
            
            # Set specific headers for refresh token request
            headers = {
                'accept': '*/*',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = self.session.get(
                f'{self.base_url}/api/Auth/RefreshToken',
                headers=headers
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract access token from response
                access_token_data = response_data.get('accessToken', {})
                self.access_token = access_token_data.get('token')
                
                # Update refresh token if available
                if 'refreshToken' in response_data:
                    self.refresh_token = response_data.get('refreshToken')
                
                self._update_auth_header()
                self.logger.info("Successfully refreshed access token")
                return True
            else:
                self.logger.error(f"Token refresh failed with status code: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                # If refresh fails, try to login again
                return self.login()
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during token refresh: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during token refresh: {str(e)}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """
        Ensure the client is authenticated with a valid token.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.ensure_token_valid()
    
    def get_users(self, limit: int = 100, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve users from the backend API.
        
        Args:
            limit (int): Maximum number of users to retrieve
            offset (int): Number of users to skip
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of users or None if failed
        """
        try:
            if not self._ensure_authenticated():
                return None
            
            params = {
                'limit': limit,
                'offset': offset
            }
            
            response = self.session.get(
                f'{self.base_url}/users',
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Retrieved {len(data.get('users', []))} users")
                return data.get('users', [])
            else:
                self.logger.error(f"Failed to get users. Status code: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error while getting users: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error while getting users: {str(e)}")
            return None
    
    def get_documents(self, user_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve documents from the backend API.
        
        Args:
            user_id (Optional[str]): Filter documents by user ID
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of documents or None if failed
        """
        try:
            if not self._ensure_authenticated():
                return None
            
            params = {}
            if user_id:
                params['user_id'] = user_id
            
            response = self.session.get(
                f'{self.base_url}/documents',
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Retrieved {len(data.get('documents', []))} documents")
                return data.get('documents', [])
            else:
                self.logger.error(f"Failed to get documents. Status code: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error while getting documents: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error while getting documents: {str(e)}")
            return None
    
    def update_education_history(self, education_id: str, user_id: str, document_number: str, 
                               document_verified_status: bool, hr_description: str,
                               education_level: str = "string", school: str = "string",
                               school_address: str = "string", approved: bool = True) -> bool:
        """
        Update education history for a specific education record.
        
        Args:
            education_id (str): The ID of the education record
            user_id (str): The ID of the user
            document_number (str): The document number
            document_verified_status (bool): Document verification status
            hr_description (str): HR description
            education_level (str): Education level (use existing value if available)
            school (str): School name (use existing value if available)
            school_address (str): School address (use existing value if available)
            approved (bool): Approval status (use existing value if available)
            
        Returns:
            bool: True if update successful, False otherwise
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Ensure we have a valid token before making the request
                if not self.ensure_token_valid():
                    self.logger.error(f"Failed to ensure valid token for education history update (attempt {retry_count + 1})")
                    retry_count += 1
                    continue
                
                # Prepare the JSON payload
                education_data = {
                    "id": education_id,
                    "educationLevel": education_level,
                    "school": school,
                    "schoolAddress": school_address,
                    "documentNumber": document_number,
                    "documentVerified": document_verified_status,
                    "hrDescription": hr_description,
                    "approved": approved,
                    "userId": user_id
                }
                
                # Set specific headers for the request
                headers = {
                    'accept': '*/*',
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
                
                self.logger.info(f"Attempting to update education history (attempt {retry_count + 1}/{max_retries})")
                self.logger.debug(f"Update data: {education_data}")
                
                response = self.session.put(
                    f'{self.base_url}/api/UserEducationHistories',
                    json=education_data,
                    headers=headers,
                    timeout=30  # Add timeout
                )
                
                # Success cases
                if response.status_code in [200, 204]:
                    self.logger.info(f"✅ Successfully updated education history for education ID {education_id} (user {user_id})")
                    self.logger.info(f"Document verified: {document_verified_status}, HR description: {hr_description}")
                    return True
                
                # Client errors (4xx) - generally not retriable
                elif 400 <= response.status_code < 500:
                    self.logger.error(f"❌ Client error updating education history. Status: {response.status_code}")
                    self.logger.error(f"Response: {response.text}")
                    if response.status_code == 401:  # Unauthorized - might be retriable with new token
                        self.access_token = None  # Force token refresh
                        retry_count += 1
                        continue
                    else:
                        return False  # Other 4xx errors are not retriable
                
                # Server errors (5xx) - retriable
                elif response.status_code >= 500:
                    self.logger.warning(f"⚠️ Server error updating education history. Status: {response.status_code}")
                    self.logger.warning(f"Response: {response.text}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        wait_time = 2 ** retry_count  # Exponential backoff
                        self.logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    continue
                
                else:
                    self.logger.error(f"❌ Unexpected status code: {response.status_code}")
                    self.logger.error(f"Response: {response.text}")
                    return False
                    
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"⚠️ Timeout error updating education history (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
                
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"⚠️ Connection error updating education history (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ Network error updating education history (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
                
            except Exception as e:
                self.logger.error(f"❌ Unexpected error updating education history (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
        
        # If we get here, all retries failed
        self.logger.error(f"❌ All {max_retries} attempts to update education history failed for education ID {education_id}")
        return False
    
    def update_user_security_document(self, security_id: str, user_id: str, document_number: str,
                                     document_verified_status: bool, hr_description: str,
                                     approved: bool = True) -> bool:
        """
        Update security document for a specific security record.
        
        Args:
            security_id (str): The ID of the security record
            user_id (str): The ID of the user
            document_number (str): The document number
            document_verified_status (bool): Document verification status
            hr_description (str): HR description
            approved (bool): Approval status (use existing value if available)
            
        Returns:
            bool: True if update successful, False otherwise
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Ensure we have a valid token before making the request
                if not self.ensure_token_valid():
                    self.logger.error(f"Failed to ensure valid token for security document update (attempt {retry_count + 1})")
                    retry_count += 1
                    continue
                
                # Prepare the JSON payload
                security_data = {
                    "id": security_id,
                    "documentNumber": document_number,
                    "documentVerified": document_verified_status,
                    "hrDescription": hr_description,
                    "approved": approved,
                    "userId": user_id
                }
                
                # Set specific headers for the request
                headers = {
                    'accept': '*/*',
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
                
                self.logger.info(f"Attempting to update security document (attempt {retry_count + 1}/{max_retries})")
                self.logger.debug(f"Update data: {security_data}")
                
                response = self.session.put(
                    f'{self.base_url}/api/UserSecurities',
                    json=security_data,
                    headers=headers,
                    timeout=30  # Add timeout
                )
                
                # Success cases
                if response.status_code in [200, 204]:
                    self.logger.info(f"✅ Successfully updated security document for security ID {security_id} (user {user_id})")
                    self.logger.info(f"Document verified: {document_verified_status}, HR description: {hr_description}")
                    return True
                
                # Client errors (4xx) - generally not retriable
                elif 400 <= response.status_code < 500:
                    self.logger.error(f"❌ Client error updating security document. Status: {response.status_code}")
                    self.logger.error(f"Response: {response.text}")
                    if response.status_code == 401:  # Unauthorized - might be retriable with new token
                        self.access_token = None  # Force token refresh
                        retry_count += 1
                        continue
                    else:
                        return False  # Other 4xx errors are not retriable
                
                # Server errors (5xx) - retriable
                elif response.status_code >= 500:
                    self.logger.warning(f"⚠️ Server error updating security document. Status: {response.status_code}")
                    self.logger.warning(f"Response: {response.text}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        wait_time = 2 ** retry_count  # Exponential backoff
                        self.logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    continue
                
                else:
                    self.logger.error(f"❌ Unexpected status code: {response.status_code}")
                    self.logger.error(f"Response: {response.text}")
                    return False
                    
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"⚠️ Timeout error updating security document (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
                
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"⚠️ Connection error updating security document (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ Network error updating security document (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
                
            except Exception as e:
                self.logger.error(f"❌ Unexpected error updating security document (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    wait_time = 2 ** retry_count
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                continue
        
        # If we get here, all retries failed
        self.logger.error(f"❌ All {max_retries} attempts to update security document failed for security ID {security_id}")
        return False
    
    def fetch_documents_for_verification(self, page_index: int = 0, page_size: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch documents for verification with pagination support.
        
        Args:
            page_index (int): The page index to retrieve (default: 0)
            page_size (int): The number of items per page (default: 100)
            
        Returns:
            Optional[List[Dict[str, Any]]]: List of documents or None if failed
        """
        try:
            # Ensure we have a valid token before making the request
            if not self.ensure_token_valid():
                self.logger.error("Failed to ensure valid token for document verification request")
                return None
            
            # Set specific headers for the request
            headers = {
                'accept': '*/*',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            # Construct the URL with query parameters
            url = f'{self.base_url}/api/Users/cv-edu-security/list?PageRequest.PageIndex={page_index}&PageRequest.PageSize={page_size}'
            
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                items = response_data.get('items', [])
                self.logger.info(f"Successfully fetched {len(items)} documents for verification (page {page_index}, size {page_size})")
                return items
            else:
                self.logger.error(f"Failed to fetch documents for verification. Status code: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error while fetching documents for verification: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching documents for verification: {str(e)}")
            return None
    
    def close(self):
        """Close the session and clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
            self.logger.info("Backend API client session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def update_document_by_event_type(self, event_type: str, document_id: str, user_id: str, 
                                    document_number: str, document_verified_status: bool, 
                                    hr_description: str, **kwargs) -> bool:
        """
        Update document based on event type - routes to appropriate update method.
        
        Args:
            event_type (str): Type of event (UserEducationCreated, UserSecurityCreated, etc.)
            document_id (str): The ID of the document record
            user_id (str): The ID of the user
            document_number (str): The document number
            document_verified_status (bool): Document verification status
            hr_description (str): HR description
            **kwargs: Additional parameters specific to document type
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            self.logger.info(f"🎯 Routing update for event type: {event_type}")
            
            if "Education" in event_type:
                # For education documents, extract additional parameters
                education_level = kwargs.get('education_level', 'string')
                school = kwargs.get('school', 'string')
                school_address = kwargs.get('school_address', 'string')
                approved = kwargs.get('approved', True)
                
                return self.update_education_history(
                    education_id=document_id,
                    user_id=user_id,
                    document_number=document_number,
                    document_verified_status=document_verified_status,
                    hr_description=hr_description,
                    education_level=education_level,
                    school=school,
                    school_address=school_address,
                    approved=approved
                )
                
            elif "Security" in event_type:
                # For security documents
                approved = kwargs.get('approved', True)
                
                return self.update_user_security_document(
                    security_id=document_id,
                    user_id=user_id,
                    document_number=document_number,
                    document_verified_status=document_verified_status,
                    hr_description=hr_description,
                    approved=approved
                )
            else:
                self.logger.error(f"❌ Unknown event type for document update: {event_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error routing document update: {str(e)}")
            return False
