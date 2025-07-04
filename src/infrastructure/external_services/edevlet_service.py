"""
E-Devlet Service - Infrastructure Layer
Clean Architecture - Complete E-Devlet automation service with advanced features
Direct port from original src/core/edevlet.py with enhancements
"""
import logging
import time
import os
import platform
from typing import Optional, Dict, Any, List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..browser import BrowserFactory, HumanBehaviorSimulator, StrategyFactory, ElementFinder


class EdevletService:
    """
    Complete E-Devlet automation service.
    
    Features:
    - Full document verification flow
    - Advanced anti-detection mechanisms
    - Human-like behavior simulation
    - Robust error handling and recovery
    - File download management
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize E-Devlet service.
        
        Args:
            headless: Run browser in headless mode
            timeout: Maximum wait time for operations
        """
        self.headless = headless
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
        # Advanced browser components
        self.browser_factory = BrowserFactory()
        self.strategy_factory = StrategyFactory()
        self.driver = None
        self.human_behavior = None
        self.element_finder = None
        
        # Download directory setup
        self.download_dir = self._setup_download_directory()
        
        self.logger.info("🌐 EdevletService initialized")
        self.logger.info(f"📁 Download directory: {self.download_dir}")
        self.logger.info(f"🖥️ Operating System: {platform.system()} {platform.machine()}")
    
    def _setup_download_directory(self) -> str:
        """Setup download directory for documents."""
        download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        return download_dir
    
    def _init_browser(self) -> bool:
        """Initialize advanced Chrome browser with stealth features."""
        try:
            self.logger.info("🚀 Starting WebDriver with advanced configuration...")
            
            # Create advanced browser with anti-detection
            self.driver = self.browser_factory.create_stealth_browser(
                headless=self.headless,
                timeout=self.timeout,
                download_dir=self.download_dir
            )
            
            # Initialize human behavior simulator
            self.human_behavior = HumanBehaviorSimulator(self.driver)
            
            # Initialize element finder with strategies
            self.element_finder = ElementFinder(self.driver, self.strategy_factory)
            
            self.logger.info("✅ WebDriver started successfully with stealth features")
            return True
            
        except Exception as e:
            self.logger.error(f"💥 WebDriver initialization failed: {str(e)}")
            return False
    
    def verify_document(self, barcode_number: str, tc_kimlik_no: str) -> Dict[str, Any]:
        """
        Complete document verification process.
        
        Args:
            barcode_number: Document barcode number
            tc_kimlik_no: TC Identity number
            
        Returns:
            Dict with verification results
        """
        if not self._init_browser():
            return {
                "success": False,
                "error": "Browser initialization failed",
                "files": []
            }
        
        try:
            result = self._perform_full_verification(barcode_number, tc_kimlik_no)
            return result
            
        except Exception as e:
            self.logger.error(f"💥 Document verification error: {str(e)}")
            return {
                "success": False,
                "error": f"Verification process failed: {str(e)}",
                "files": []
            }
        finally:
            self._cleanup_browser()
    
    def _perform_full_verification(self, barcode_number: str, tc_kimlik_no: str) -> Dict[str, Any]:
        """Perform the complete verification flow."""
        # Step 1: Navigate to E-Devlet verification page
        from ..config.app_config import AppConfig
        verification_config = AppConfig.get_verification_config()
        verification_url = verification_config["url"]
        self.logger.info(f"🌐 Navigating to E-Devlet verification page: {verification_url}")
        self.driver.get(verification_url)
        
        # Human behavior after page load
        self.human_behavior.random_sleep(2, 4)
        self.human_behavior.simulate_human_behavior()
        
        # Step 2: Enter barcode number
        self.logger.info(f"📋 Entering barcode number: {barcode_number}")
        barcode_input = self.element_finder.find_element_by_type("barcode_input")
        
        if not barcode_input:
            return {
                "success": False,
                "error": "Barcode input field not found",
                "files": []
            }
        
        # Human-like typing
        self.human_behavior.human_like_type(barcode_input, barcode_number)
        
        # Find and click submit button
        self.logger.info("🖱️ Clicking submit button...")
        submit_button = self.element_finder.find_element_by_type("submit_button")
        
        if not submit_button:
            return {
                "success": False,
                "error": "Submit button not found",
                "files": []
            }
        
        self.human_behavior.human_like_click(submit_button)
        self.logger.info("✅ Submit button clicked successfully")
        
        # Wait for page transition
        self.human_behavior.random_sleep(1, 2)
        
        # Step 3: Enter TC Kimlik No
        self.logger.info(f"🆔 Entering TC Kimlik No: {tc_kimlik_no[:3]}****{tc_kimlik_no[7:]}")
        
        # Wait for second input field
        tc_input = self.element_finder.find_element_by_type("tc_kimlik_input")
        
        if not tc_input:
            return {
                "success": False,
                "error": "TC Kimlik input field not found",
                "files": []
            }
        
        # Human-like typing
        self.human_behavior.human_like_type(tc_input, tc_kimlik_no)
        
        # Find and click submit button again
        self.logger.info("🖱️ Clicking submit button for TC Kimlik...")
        submit_button = self.element_finder.find_element_by_type("submit_button")
        
        if not submit_button:
            return {
                "success": False,
                "error": "Second submit button not found",
                "files": []
            }
        
        self.human_behavior.human_like_click(submit_button)
        self.logger.info("✅ TC Kimlik submit button clicked")
        
        # Wait for next page
        self.human_behavior.random_sleep(3, 5)

        # Step 4: Handle checkbox if present
        self.logger.info("☑️ Looking for checkbox...")
        checkbox = self.element_finder.find_element_by_type("checkbox")
        
        if checkbox:
            self.logger.info("☑️ Checkbox found, clicking...")
            self.human_behavior.human_like_click(checkbox)
            self.logger.info("✅ Checkbox clicked")
            
            # Wait a bit
            self.human_behavior.random_sleep(2, 3)
            
            # Find final submit button
            final_submit = self.element_finder.find_element_by_type("submit_button")
            if final_submit:
                self.logger.info("🖱️ Clicking final submit button...")
                self.human_behavior.human_like_click(final_submit)
                self.logger.info("✅ Final submit button clicked")
        else:
            self.logger.info("ℹ️ No checkbox found, proceeding...")
        
        # Wait for final result
        self.human_behavior.random_sleep(3, 5)
        
        # Step 5: Check result and handle downloads
        return self._handle_verification_result()
    
    def _handle_verification_result(self) -> Dict[str, Any]:
        """Handle the verification result and file downloads."""
        current_url = self.driver.current_url
        self.logger.info(f"📍 Current URL: {current_url}")
        
        if "belge=goster" in current_url or "belge-dogrulama" in current_url:
            self.logger.info("✅ Verification successful! Result page reached.")
            
            # Try to download files
            downloaded_files = self._download_verification_files()
            
            return {
                "success": True,
                "message": "Document verification successful",
                "files": downloaded_files,
                "url": current_url
            }
        
        elif "hata=sayfasi" in current_url:
            # Handle error page
            error_message = self._extract_error_message()
            self.logger.warning(f"❌ Verification failed: {error_message}")
            
            return {
                "success": False,
                "error": error_message,
                "files": [],
                "url": current_url
            }
        
        else:
            self.logger.warning(f"⚠️ Unexpected state. URL: {current_url}")
            self.element_finder._take_screenshot(f"unexpected_state_{int(time.time())}")
            
            return {
                "success": False,
                "error": f"Unexpected page state: {current_url}",
                "files": [],
                "url": current_url
            }
    
    def _download_verification_files(self) -> List[str]:
        """Download verification files."""
        downloaded_files = []
        
        try:
            # Look for download link
            self.logger.info("🔍 Looking for download link...")
            
            download_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.download"))
            )
            
            download_link_url = download_link.get_attribute("href")
            self.logger.info(f"📎 Download link found: {download_link_url}")
            
            # Click download link with human behavior
            self.human_behavior.human_like_click(download_link)
            self.logger.info("✅ Download link clicked")
            
            # Wait for download to complete
            self.human_behavior.random_sleep(3, 5)
            
            # Check downloaded files
            pdf_files = self._check_downloaded_files()
            
            if pdf_files:
                self.logger.info(f"📄 Downloaded {len(pdf_files)} PDF files:")
                for pdf_file in pdf_files:
                    full_path = os.path.join(self.download_dir, pdf_file)
                    file_size = os.path.getsize(full_path) / 1024  # KB
                    self.logger.info(f"  - {pdf_file} ({file_size:.2f} KB)")
                    downloaded_files.append(full_path)
            else:
                # Try alternative download method
                self.logger.info("📥 Trying alternative download method...")
                self.driver.get(download_link_url)
                self.human_behavior.random_sleep(5, 7)
                
                pdf_files = self._check_downloaded_files()
                if pdf_files:
                    self.logger.info(f"📄 Downloaded via alternative method: {len(pdf_files)} files")
                    for pdf_file in pdf_files:
                        full_path = os.path.join(self.download_dir, pdf_file)
                        downloaded_files.append(full_path)
                else:
                    self.logger.warning("❌ No PDF files downloaded")
            
        except TimeoutException:
            self.logger.warning("⏰ Download link not found within timeout")
        except Exception as e:
            self.logger.error(f"💥 Download error: {str(e)}")
        
        return downloaded_files
    
    def _check_downloaded_files(self) -> List[str]:
        """Check for downloaded PDF files."""
        try:
            downloaded_files = os.listdir(self.download_dir)
            pdf_files = [f for f in downloaded_files if f.endswith('.pdf')]
            return pdf_files
        except Exception as e:
            self.logger.error(f"💥 Error checking downloaded files: {str(e)}")
            return []
    
    def _extract_error_message(self) -> str:
        """Extract error message from error page."""
        try:
            error_containers = self.element_finder.find_elements_with_strategies(
                self.strategy_factory.get_strategies_for("error_container"),
                "Error message extraction"
            )
            
            for container in error_containers:
                error_text = self.element_finder.get_element_text_safe(container)
                if error_text:
                    return error_text
            
            # Fallback: check page source for common error patterns
            page_source = self.driver.page_source.lower()
            
            if "doğrulama kodu sistem kayıtlarında bulunamadı" in page_source:
                return "Doğrulama kodu sistem kayıtlarında bulunamadı"
            elif "geçersiz barkod" in page_source:
                return "Geçersiz barkod numarası"
            elif "geçersiz tc kimlik" in page_source:
                return "Geçersiz TC Kimlik numarası"
            else:
                return "Bilinmeyen doğrulama hatası"
                
        except Exception as e:
            self.logger.error(f"💥 Error message extraction failed: {str(e)}")
            return "Error message could not be extracted"
    
    def _cleanup_browser(self) -> None:
        """Clean up browser resources."""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("🔄 WebDriver closed")
        except Exception as e:
            self.logger.error(f"💥 Browser cleanup error: {str(e)}")
    
    def get_download_directory_info(self) -> Dict[str, Any]:
        """Get information about the download directory."""
        try:
            files = os.listdir(self.download_dir)
            pdf_files = [f for f in files if f.endswith('.pdf')]
            
            file_info = []
            for pdf_file in pdf_files:
                full_path = os.path.join(self.download_dir, pdf_file)
                stat = os.stat(full_path)
                file_info.append({
                    "name": pdf_file,
                    "path": full_path,
                    "size_kb": stat.st_size / 1024,
                    "modified": time.ctime(stat.st_mtime)
                })
            
            return {
                "directory": self.download_dir,
                "total_files": len(files),
                "pdf_files": len(pdf_files),
                "files": file_info
            }
            
        except Exception as e:
            self.logger.error(f"💥 Download directory info error: {str(e)}")
            return {
                "directory": self.download_dir,
                "error": str(e)
            } 