"""
Document verification service for eDevlet operations.
"""
from typing import Optional
from selenium import webdriver

from ..models.entities import ValidationResult
from ..exceptions import ValidationError, DriverError
from ..utils.driver_manager import DriverManager
from ..utils.file_manager import FileManager
from ..core.document_validator import DocumentValidator
from ..config.config import config
from ..constants import ErrorType


class DocumentVerificationService:
    """Service for handling document verification through eDevlet."""
    
    def __init__(self):
        """Initialize the service."""
        self.driver: Optional[webdriver.Chrome] = None
        self.file_manager: Optional[FileManager] = None
        self.validator: Optional[DocumentValidator] = None
    
    def verify_document(self, barcode: str, tc_kimlik_no: str) -> ValidationResult:
        """
        Verify a document through eDevlet.
        
        Args:
            barcode: Document barcode number
            tc_kimlik_no: TC Identity number
            
        Returns:
            ValidationResult: Result of the verification process
        """
        try:
            return self._perform_verification(barcode, tc_kimlik_no)
        except ValidationError as e:
            return ValidationResult.error_result(
                error_type=e.error_type or ErrorType.VALIDATION_FAILED.value,
                message=str(e)
            )
        except Exception as e:
            return ValidationResult.error_result(
                error_type=ErrorType.SYSTEM_ERROR.value,
                message=str(e)
            )
        finally:
            self._cleanup()
    
    def _perform_verification(self, barcode: str, tc_kimlik_no: str) -> ValidationResult:
        """Perform the actual verification process."""
        # Setup WebDriver
        self._setup_driver()
        
        # Print system info
        print(f"İndirme dizini: {config.DOWNLOAD_DIR}")
        print(config.SYSTEM_INFO)
        
        # Check existing files before download
        existing_files = self.file_manager.check_downloaded_files()
        print(f"İşlem öncesi klasörde bulunan dosya sayısı: {len(existing_files)}")
        
        # Navigate to validation page
        self.validator.navigate_to_validation_page()
        
        # Enter barcode
        barcode_result = self.validator.enter_barcode(barcode)
        if isinstance(barcode_result, dict) and not barcode_result.get('success', True):
            raise ValidationError(
                barcode_result['message'],
                error_type=barcode_result['error_type']
            )
        
        # Validate TC Identity number
        tc_validation_result = self.validator.enter_tc_kimlik_no(tc_kimlik_no)
        if not tc_validation_result["success"]:
            raise ValidationError(
                tc_validation_result['message'],
                error_type=tc_validation_result['error_type']
            )
        
        # Accept terms
        if not self.validator.accept_terms():
            raise ValidationError(
                "Onay işlemi yapılamadı.",
                error_type=ErrorType.TERMS_ACCEPTANCE_ERROR.value
            )
        
        # Check if validation is successful
        validation_result = self.validator.is_validation_successful()
        if not validation_result.get('success', False):
            raise ValidationError(
                validation_result.get('message', 'Belge doğrulama işlemi başarısız oldu.'),
                error_type=validation_result.get('error_type', ErrorType.VALIDATION_FAILED.value)
            )
        
        # Get download link and download file
        download_link, download_link_url = self.validator.get_download_link()
        
        if download_link and download_link_url:
            return self._download_and_verify_files(
                download_link, 
                download_link_url, 
                existing_files
            )
        
        raise ValidationError(
            "Dosya indirme bağlantısı bulunamadı veya dosya indirilemedi.",
            error_type=ErrorType.DOWNLOAD_FAILED.value
        )
    
    def _download_and_verify_files(self, download_link, download_link_url, existing_files) -> ValidationResult:
        """Download files and verify success."""
        # Download file
        if self.file_manager.download_file(download_link):
            # Check downloaded files
            all_files_after = self.file_manager.check_downloaded_files()
            
            # If file wasn't downloaded, try alternative method
            if len(all_files_after) <= len(existing_files):
                self.file_manager.download_file_alternative(download_link_url)
                all_files_after = self.file_manager.check_downloaded_files()
            
            # Identify newly downloaded files
            new_files = [f for f in all_files_after if f not in existing_files]
            print(f"Yeni indirilen dosya sayısı: {len(new_files)}")
            
            return ValidationResult.success_result(
                files=new_files,
                message="Document verified and downloaded."
            )
        
        raise ValidationError(
            "Dosya indirme işlemi başarısız oldu.",
            error_type=ErrorType.DOWNLOAD_FAILED.value
        )
    
    def _setup_driver(self):
        """Setup WebDriver and related components."""
        try:
            self.driver = DriverManager.setup_driver()
            self.driver.maximize_window()
            
            self.file_manager = FileManager(self.driver)
            self.validator = DocumentValidator(self.driver)
            
        except Exception as e:
            raise DriverError(f"WebDriver setup failed: {str(e)}")
    
    def _cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                DriverManager.close_driver(self.driver)
            except Exception as e:
                print(f"Driver cleanup error: {str(e)}")
            finally:
                self.driver = None
                self.file_manager = None
                self.validator = None
