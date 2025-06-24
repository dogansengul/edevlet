"""
Custom exceptions for the eDevlet automation system.
"""


class EDevletAutomationError(Exception):
    """Base exception for eDevlet automation system."""
    pass


class ValidationError(EDevletAutomationError):
    """Exception raised during document validation."""
    
    def __init__(self, message: str, error_type: str = None):
        super().__init__(message)
        self.error_type = error_type


class BackendAPIError(EDevletAutomationError):
    """Exception raised during backend API operations."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(BackendAPIError):
    """Exception raised during authentication operations."""
    pass


class DocumentProcessingError(EDevletAutomationError):
    """Exception raised during document processing."""
    
    def __init__(self, message: str, document_id: str = None):
        super().__init__(message)
        self.document_id = document_id


class DriverError(EDevletAutomationError):
    """Exception raised during WebDriver operations."""
    pass


class ConfigurationError(EDevletAutomationError):
    """Exception raised for configuration issues."""
    pass


class NetworkError(EDevletAutomationError):
    """Exception raised for network-related issues."""
    pass


class DataValidationError(EDevletAutomationError):
    """Exception raised for data validation issues."""
    
    def __init__(self, message: str, field_name: str = None):
        super().__init__(message)
        self.field_name = field_name
