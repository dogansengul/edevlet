"""
Browser Factory - Infrastructure Layer
Clean Architecture - Advanced browser creation with anti-detection features
"""
import logging
import os
import random
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
# from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import subprocess
import re
import ssl
import platform

# SSL sertifika doğrulama hatasını çözmek için
if platform.system() == 'Darwin':  # macOS için
    ssl._create_default_https_context = ssl._create_unverified_context


class BrowserFactory:
    """
    Factory for creating configured Chrome browser instances.
    
    Single Responsibility: Only handles browser creation and configuration
    Encapsulates all anti-detection and stealth configurations
    """
    
    def __init__(self):
        """Initialize browser factory."""
        self.logger = logging.getLogger(__name__)
        self.download_dir = self._ensure_download_directory()
        
    def create_chrome_browser(
        self,
        headless: Optional[bool] = None,
        download_dir: Optional[str] = None,
        stealth_mode: Optional[bool] = None,
        window_size: Optional[str] = None,
        timeout: Optional[int] = None,
        use_undetected: Optional[bool] = None
    ) -> Chrome:
        """
        Create configured Chrome browser with anti-detection features.
        
        Args:
            headless: Run browser in headless mode (uses config default if None)
            download_dir: Custom download directory
            stealth_mode: Enable stealth/anti-detection features (uses config default if None)
            window_size: Browser window size (uses config default if None)
            timeout: Page load timeout (uses config default if None)
            use_undetected: Use undetected chrome (uses config default if None)
            
        Returns:
            Configured Chrome WebDriver instance
        """
        from ...config.app_config import AppConfig
        browser_config = AppConfig.get_browser_config()
        
        # Use provided values or fall back to config defaults
        headless = headless if headless is not None else browser_config["headless"]
        stealth_mode = stealth_mode if stealth_mode is not None else browser_config["stealth_mode"]
        window_size = window_size if window_size is not None else browser_config["window_size"]
        timeout = timeout if timeout is not None else browser_config["timeout"]
        use_undetected = use_undetected if use_undetected is not None else browser_config["use_undetected"]
        
        self.logger.info("🏭 Creating Chrome browser with advanced configuration")
        self.logger.info(f"📊 Using config: headless={headless}, stealth={stealth_mode}, size={window_size}")
        
        # Use custom download dir or default
        download_path = download_dir or self.download_dir
        
        # Create Chrome options
        chrome_options = self._create_chrome_options(
            headless=headless,
            download_dir=download_path,
            stealth_mode=stealth_mode,
            window_size=window_size
        )
        
        # Create Chrome service
        service = self._create_chrome_service()
        
        try:
            # Create driver instance with optional undetected chrome
            if use_undetected and stealth_mode:
                self.logger.info("🥷 Creating undetected Chrome browser...")
                driver = self._create_undetected_chrome(
                    chrome_options, headless, download_path
                )
            else:
                self.logger.info("🌐 Creating standard Chrome browser...")
                driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configure timeouts
            driver.set_page_load_timeout(timeout)
            driver.implicitly_wait(10)
            
            # Apply stealth configurations
            if stealth_mode:
                self._apply_stealth_configurations(driver)
            
            self.logger.info("✅ Chrome browser created successfully")
            self.logger.info(f"📁 Download directory: {download_path}")
            self.logger.info(f"🖥️ Window size: {window_size}")
            self.logger.info(f"👤 Headless mode: {headless}")
            self.logger.info(f"🥷 Stealth mode: {stealth_mode}")
            self.logger.info(f"🔍 Undetected mode: {use_undetected}")
            
            return driver
            
        except Exception as e:
            self.logger.error(f"💥 Browser creation failed: {str(e)}")
            raise
    
    def _create_chrome_options(
        self,
        headless: bool,
        download_dir: str,
        stealth_mode: bool,
        window_size: str
    ) -> Options:
        """Create Chrome options with advanced configurations."""
        chrome_options = Options()
        
        # Basic options
        if headless:
            chrome_options.add_argument("--headless=new")  # New headless mode
        
        chrome_options.add_argument(f"--window-size={window_size}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Anti-detection options
        if stealth_mode:
            self._add_stealth_options(chrome_options)
        
        # Performance optimizations
        self._add_performance_options(chrome_options)
        
        # Download preferences
        download_prefs = self._create_download_preferences(download_dir)
        chrome_options.add_experimental_option("prefs", download_prefs)
        
        # Additional experimental options
        # chrome_options.add_experimental_option("useAutomationExtension", False)
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        return chrome_options
    
    def _add_stealth_options(self, chrome_options: Options) -> None:
        """Add stealth/anti-detection Chrome options."""
        stealth_options = [
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-save-password-bubble",
            "--disable-translate",
            "--disable-web-security",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-component-extensions-with-background-pages",
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--ignore-certificate-errors-spki-list",
            "--ignore-certificate-errors-ssl"
        ]
        
        for option in stealth_options:
            chrome_options.add_argument(option)
        
        self.logger.debug(f"🥷 Added {len(stealth_options)} stealth options")
    
    def _add_performance_options(self, chrome_options: Options) -> None:
        """Add performance optimization options."""
        performance_options = [
            "--disable-images",
            "--disable-javascript",  # Only for document verification
            "--disable-plugins",
            "--disable-java",
            "--disable-flash",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-translate",
            "--hide-scrollbars",
            "--mute-audio",
            "--no-sandbox",
            "--memory-pressure-off",
            "--max_old_space_size=4096"
        ]
        
        for option in performance_options:
            chrome_options.add_argument(option)
        
        self.logger.debug(f"⚡ Added {len(performance_options)} performance options")
    
    def _create_download_preferences(self, download_dir: str) -> Dict[str, Any]:
        """Create download preferences."""
        return {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
    
    def _create_chrome_service(self) -> Service:
        """Create Chrome service, preferring system PATH."""
        self.logger.info("🔧 Creating Chrome service...")
        try:
            # Selenium 4.6+, PATH'te chromedriver'ı otomatik olarak bulur.
            # Bu, webdriver-manager'dan daha güvenilirdir, özellikle ARM tabanlı sistemlerde.
            service = Service()
            self.logger.info("✅ Chrome service created using system PATH.")
            return service
        except Exception as e:
            self.logger.error(f"💥 System PATH'te chromedriver bulunamadı: {e}. Lütfen 'brew install chromedriver' komutu ile kurun.")
            # Fallback olarak eski yöntemi deneyebiliriz ama genellikle PATH'e kurmak daha iyidir.
            # from webdriver_manager.chrome import ChromeDriverManager
            # self.logger.info("🔄 Fallback: webdriver-manager ile denenecek...")
            # return Service(ChromeDriverManager().install())
            raise
    
    def _apply_stealth_configurations(self, driver: Chrome) -> None:
        """Apply JavaScript-based stealth configurations."""
        try:
            # Hide webdriver property
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Mock realistic user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            
            selected_ua = random.choice(user_agents)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": selected_ua})
            
            # Mock plugins
            driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            
            # Mock languages
            driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['tr-TR', 'tr', 'en-US', 'en'],
                });
            """)
            
            # Mock hardware concurrency
            driver.execute_script("""
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });
            """)
            
            # Mock device memory
            driver.execute_script("""
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
            """)
            
            # Mock WebGL
            driver.execute_script("""
                const getParameter = WebGLRenderingContext.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel(R) Iris(TM) Graphics 6100';
                    }
                    return getParameter(parameter);
                };
            """)
            
            self.logger.debug("🥷 Stealth JavaScript configurations applied")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Stealth configuration warning: {str(e)}")
    
    def _ensure_download_directory(self) -> str:
        """Ensure download directory exists."""
        download_dir = os.path.join(os.getcwd(), "downloads")
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            self.logger.debug(f"📁 Created download directory: {download_dir}")
        
        return download_dir
    
    def create_headless_browser(self, **kwargs) -> Chrome:
        """Create headless browser (convenience method)."""
        kwargs['headless'] = True
        return self.create_chrome_browser(**kwargs)
    
    def create_visible_browser(self, **kwargs) -> Chrome:
        """Create visible browser (convenience method)."""
        kwargs['headless'] = False
        return self.create_chrome_browser(**kwargs)
    
    def create_stealth_browser(self, **kwargs) -> Chrome:
        """Create browser with maximum stealth features."""
        kwargs['stealth_mode'] = True
        kwargs['headless'] = kwargs.get('headless', True)
        return self.create_chrome_browser(**kwargs)
    
    def _create_undetected_chrome(self, options: Options, headless: bool, download_path: str) -> Chrome:
        """Create undetected Chrome browser."""
        try:
            # Convert regular Options to ChromeOptions for undetected_chromedriver  
            uc_options = uc.ChromeOptions()
            
            # Copy arguments from regular options
            for arg in options.arguments:
                uc_options.add_argument(arg)
            
            # Copy experimental options
            for name, value in options.experimental_options.items():
                uc_options.add_experimental_option(name, value)
            
            # Add undetected-specific optimizations
            uc_options.add_argument("--disable-blink-features=AutomationControlled")
            uc_options.add_argument("--remote-allow-origins=*")
            uc_options.add_argument("--enable-javascript")
            uc_options.add_argument("--disable-dev-shm-usage")
            uc_options.add_argument("--disable-software-rasterizer")
            
            # Get Chrome version for better compatibility
            chrome_version = self._get_chrome_version()
            
            # Random user agent for better stealth
            ua = UserAgent()
            uc_options.add_argument(f"--user-agent={ua.random}")
            
            # Create undetected Chrome driver
            if chrome_version:
                self.logger.debug(f"🔍 Detected Chrome version: {chrome_version}")
                driver = uc.Chrome(
                    options=uc_options,
                    headless=headless,
                    use_subprocess=True,
                    version_main=chrome_version
                )
            else:
                self.logger.debug("🔍 Using automatic Chrome version detection")
                driver = uc.Chrome(
                    options=uc_options,
                    headless=headless,
                    use_subprocess=True
                )
            
            # Wait for browser to fully load
            import time
            time.sleep(3)
            
            self.logger.info("✅ Undetected Chrome browser created successfully")
            return driver
            
        except Exception as e:
            self.logger.error(f"💥 Undetected Chrome creation failed: {str(e)}")
            # Fallback to regular Chrome
            self.logger.info("🔄 Falling back to regular Chrome browser...")
            service = self._create_chrome_service()
            return webdriver.Chrome(service=service, options=options)
    
    def _get_chrome_version(self) -> Optional[int]:
        """Get Chrome browser version."""
        try:
            if platform.system() == 'Darwin':  # macOS
                result = subprocess.run(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                    capture_output=True, text=True
                )
            elif platform.system() == 'Linux':
                result = subprocess.run(
                    ['google-chrome', '--version'], 
                    capture_output=True, text=True
                )
            elif platform.system() == 'Windows':
                result = subprocess.run(
                    ['chrome.exe', '--version'], 
                    capture_output=True, text=True
                )
            else:
                return None
                
            if result.returncode == 0:
                version_match = re.search(r'(\d+)\.\d+\.\d+\.\d+', result.stdout)
                if version_match:
                    return int(version_match.group(1))
                    
        except Exception as e:
            self.logger.debug(f"Chrome version detection failed: {str(e)}")
        
        return None
    
    def get_browser_info(self, driver: Chrome) -> Dict[str, Any]:
        """Get browser information for debugging."""
        try:
            return {
                "session_id": driver.session_id,
                "capabilities": driver.capabilities,
                "current_url": driver.current_url,
                "window_size": driver.get_window_size(),
                "window_position": driver.get_window_position(),
            }
        except Exception as e:
            self.logger.error(f"💥 Browser info error: {str(e)}")
            return {"error": str(e)} 