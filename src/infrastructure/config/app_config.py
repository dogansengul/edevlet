"""
Simple Application Configuration
Environment-based configuration management
"""
import os
from typing import Dict, Any, List


class AppConfig:
    """Simple application configuration from environment variables."""
    
    @classmethod
    def get_flask_config(cls) -> Dict[str, Any]:
        """Get Flask configuration."""
        return {
            "host": os.getenv("FLASK_HOST", "0.0.0.0"),
            "port": int(os.getenv("FLASK_PORT", "5002")),
            "debug": os.getenv("FLASK_DEBUG", "false").lower() == "true"
        }
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "path": os.getenv("DATABASE_PATH", "queue_clean.db")
        }
    
    @classmethod
    def get_backend_config(cls) -> Dict[str, Any]:
        """Get backend API configuration."""
        return {
            "base_url": os.getenv("BACKEND_API_BASE_URL", ""),
            "email": os.getenv("BACKEND_API_EMAIL", ""),
            "password": os.getenv("BACKEND_API_PASSWORD", ""),
            "timeout": int(os.getenv("BACKEND_API_TIMEOUT", "30"))
        }
    
    @classmethod
    def get_verification_config(cls) -> Dict[str, Any]:
        """Get document verification configuration."""
        return {
            "enabled": os.getenv("EDEVLET_VERIFICATION_ENABLED", "false").lower() == "true",
            "url": os.getenv("EDEVLET_VERIFICATION_URL", "https://www.turkiye.gov.tr/belge-dogrulama"),
            "timeout": int(os.getenv("VERIFICATION_TIMEOUT", "30")),
            "headless": os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        }
    
    @classmethod
    def get_browser_config(cls) -> Dict[str, Any]:
        """Get browser configuration."""
        return {
            "headless": os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
            "timeout": int(os.getenv("BROWSER_TIMEOUT", "30"))
        }
    
    @classmethod
    def get_processing_config(cls) -> Dict[str, Any]:
        """Get processing configuration."""
        return {
            "batch_size": int(os.getenv("BATCH_SIZE", "1")),
            "processing_interval_hours": int(os.getenv("PROCESSING_INTERVAL_HOURS", "2")),
            "max_retry_count": int(os.getenv("MAX_RETRY_COUNT", "3"))
        }
    
    @classmethod
    def is_development_mode(cls) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            "cors_origins": ["*"]  # Simple CORS for development
        } 