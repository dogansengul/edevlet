"""
System setup utilities for the eDevlet automation system.
"""
import platform
import ssl
import os
import certifi
from typing import List


class SystemSetup:
    """Handles system configuration and setup."""
    
    @staticmethod
    def setup_ssl_certificates():
        """Configure SSL certificates for macOS."""
        if platform.system() == 'Darwin':  # macOS için
            # SSL doğrulamasını devre dışı bırak
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # Certifi sertifika yolunu al ve ortam değişkenlerine ekle
            try:
                certifi_path = certifi.where()
                os.environ['SSL_CERT_FILE'] = certifi_path
                os.environ['REQUESTS_CA_BUNDLE'] = certifi_path
                print(f"SSL sertifikaları ayarlandı: {certifi_path}")
            except Exception as e:
                print(f"Certifi sertifika ayarlama hatası: {str(e)}")
    
    @staticmethod
    def setup_directories(base_dir: str, required_dirs: List[str] = None):
        """
        Create required directories.
        
        Args:
            base_dir: Base directory path
            required_dirs: List of required directory names
        """
        if required_dirs is None:
            required_dirs = ["logs", "screenshots"]
        
        try:
            for dir_name in required_dirs:
                dir_path = os.path.join(base_dir, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                print(f"{dir_name.capitalize()} dizini oluşturuldu/kontrol edildi: {dir_path}")
        except Exception as e:
            print(f"Dizin oluşturma hatası: {str(e)}")
            raise
    
    @staticmethod
    def get_project_root() -> str:
        """Get the project root directory."""
        # src dizinini bul
        current_file = os.path.abspath(__file__)
        src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        return src_dir
    
    @staticmethod
    def validate_environment():
        """Validate that all required environment variables are set."""
        required_env_vars = [
            'BACKEND_API_BASE_URL',
            'BACKEND_API_EMAIL', 
            'BACKEND_API_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print("Environment validation passed.")


class DirectoryManager:
    """Manages directory operations."""
    
    def __init__(self, base_directory: str):
        """
        Initialize DirectoryManager.
        
        Args:
            base_directory: Base directory for all operations
        """
        self.base_directory = base_directory
        self.logs_dir = os.path.join(base_directory, "logs")
        self.screenshots_dir = os.path.join(base_directory, "screenshots")
        self.downloads_dir = os.path.join(base_directory, "downloads")
    
    def setup_all_directories(self):
        """Setup all required directories."""
        directories = [
            self.logs_dir,
            self.screenshots_dir,
            self.downloads_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"Directory created/verified: {directory}")
    
    def get_logs_directory(self) -> str:
        """Get logs directory path."""
        return self.logs_dir
    
    def get_screenshots_directory(self) -> str:
        """Get screenshots directory path."""
        return self.screenshots_dir
    
    def get_downloads_directory(self) -> str:
        """Get downloads directory path."""
        return self.downloads_dir
