"""
Logging utilities for the eDevlet automation system.
"""
import os
from datetime import datetime
from typing import Optional
from ..models.entities import ValidationResult
from ..constants import LOG_FILENAME_ALL, LOG_FILENAME_FAILED


class LogManager:
    """Manages logging operations for the system."""
    
    def __init__(self, log_directory: str):
        """
        Initialize LogManager.
        
        Args:
            log_directory: Directory where log files will be stored
        """
        self.log_directory = log_directory
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists."""
        os.makedirs(self.log_directory, exist_ok=True)
    
    def log_operation(self, tc_kimlik_no: str, barcode: str, result: ValidationResult):
        """
        Log an operation result.
        
        Args:
            tc_kimlik_no: TC Identity number
            barcode: Document barcode
            result: Validation result
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Prepare log content
            log_content = self._format_log_content(tc_kimlik_no, barcode, result)
            
            # Write to all operations log
            all_log_file = os.path.join(self.log_directory, LOG_FILENAME_ALL)
            self._write_to_file(all_log_file, log_content)
            
            # Write to failed operations log if failed
            if not result.success:
                failed_log_file = os.path.join(self.log_directory, LOG_FILENAME_FAILED)
                self._write_to_file(failed_log_file, log_content)
                print(f"Başarısız işlem logu güncellendi: {failed_log_file}")
            
            print(f"Log dosyaları güncellendi: {all_log_file}")
            
        except Exception as e:
            print(f"Log dosyası oluşturma hatası: {str(e)}")
    
    def _format_log_content(self, tc_kimlik_no: str, barcode: str, result: ValidationResult) -> str:
        """Format log content."""
        log_content = f"İşlem Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_content += f"TC Kimlik No: {tc_kimlik_no}\n"
        log_content += f"Barkod No: {barcode}\n"
        log_content += f"İşlem Sonucu: {'Başarılı' if result.success else 'Başarısız'}\n"
        
        if not result.success and result.error:
            log_content += f"Hata Tipi: {result.error.error_type}\n"
            log_content += f"Hata Mesajı: {result.error.message}\n"
        else:
            log_content += f"İndirilen Dosya Sayısı: {len(result.files)}\n"
            log_content += "İndirilen Dosyalar:\n"
            for file in result.files:
                log_content += f"- {file}\n"
        
        log_content += "\n" + "="*50 + "\n"
        return log_content
    
    def _write_to_file(self, file_path: str, content: str):
        """Write content to file."""
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
    
    def log_processing_cycle(self, message: str, level: str = "INFO"):
        """Log processing cycle information."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        all_log_file = os.path.join(self.log_directory, LOG_FILENAME_ALL)
        self._write_to_file(all_log_file, log_message)
        print(f"[{timestamp}] {message}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error information."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"[{timestamp}] [ERROR] {context}: {str(error)}\n"
        
        # Write to all operations log
        all_log_file = os.path.join(self.log_directory, LOG_FILENAME_ALL)
        self._write_to_file(all_log_file, error_message)
        
        # Write to failed operations log
        failed_log_file = os.path.join(self.log_directory, LOG_FILENAME_FAILED)
        self._write_to_file(failed_log_file, error_message)
        
        print(f"[{timestamp}] HATA {context}: {str(error)}")
