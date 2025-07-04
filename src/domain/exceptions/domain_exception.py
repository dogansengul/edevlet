"""
Domain Exceptions - Domain Layer
Clean Architecture - Domain-specific error handling
"""


class DomainException(Exception):
    """Base domain exception."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ValidationException(DomainException):
    """Exception for domain validation errors."""
    
    def __init__(self, message: str, field_name: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field_name = field_name


class BusinessRuleException(DomainException):
    """Exception for business rule violations."""
    
    def __init__(self, message: str, rule_name: str = None):
        super().__init__(message, "BUSINESS_RULE_VIOLATION")
        self.rule_name = rule_name


class InvalidEventStateException(DomainException):
    """Exception for invalid event state transitions."""
    
    def __init__(self, message: str, current_state: str = None, attempted_state: str = None):
        super().__init__(message, "INVALID_EVENT_STATE")
        self.current_state = current_state
        self.attempted_state = attempted_state 