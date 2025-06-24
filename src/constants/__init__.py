"""
Constants used throughout the eDevlet automation system.
"""
from enum import Enum


class ErrorType(Enum):
    """Error type constants."""
    BARCODE_INPUT_ERROR = "barcode_input_error"
    TC_VALIDATION_ERROR = "tc_validation_error"
    TERMS_ACCEPTANCE_ERROR = "terms_acceptance_error"
    VALIDATION_FAILED = "validation_failed"
    DOWNLOAD_FAILED = "download_failed"
    SYSTEM_ERROR = "system_error"
    BACKEND_API_ERROR = "backend_api_error"
    AUTHENTICATION_ERROR = "authentication_error"
    NETWORK_ERROR = "network_error"
    DATA_ERROR = "data_error"


class LogLevel(Enum):
    """Log level constants."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Time constants (in seconds)
DEFAULT_PROCESSING_INTERVAL = 600  # 10 minutes
ERROR_RETRY_INTERVAL = 300  # 5 minutes
TOKEN_REFRESH_BUFFER = 300  # 5 minutes before expiry

# File paths
LOG_FILENAME_ALL = "all_operations.txt"
LOG_FILENAME_FAILED = "failed_operations.txt"

# API constants
MAX_RETRY_ATTEMPTS = 3
REQUEST_TIMEOUT = 30

# Processing constants
MAX_USERS_PER_BATCH = 100
MAX_DOCUMENTS_PER_USER = 50

# Status messages
SUCCESS_MESSAGES = {
    "verification": "Verified successfully",
    "download": "Document verified and downloaded.",
    "update": "Backend güncellemesi başarılı."
}

ERROR_MESSAGES = {
    "no_user_id": "Kullanıcı ID bulunamadı, bu kullanıcı atlanıyor.",
    "no_tc_number": "TC Kimlik No bulunamadı, atlanıyor.",
    "no_education_id": "Eğitim ID bulunamadı, bu belge atlanıyor.",
    "no_barcode": "Barkod numarası bulunamadı, bu belge atlanıyor.",
    "backend_update_failed": "Backend güncellemesi başarısız.",
    "verification_failed": "Belge doğrulama işlemi başarısız oldu.",
    "already_verified": "Belge zaten doğrulanmış, atlanıyor."
}
