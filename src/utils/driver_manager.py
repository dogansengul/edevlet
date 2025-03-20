import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import random
from ..config.config import config
import os
import ssl
import platform
from fake_useragent import UserAgent

# SSL sertifika doğrulama hatasını çözmek için
if platform.system() == 'Darwin':  # macOS için
    ssl._create_default_https_context = ssl._create_unverified_context

class DriverManager:
    """WebDriver kurulumu ve yönetimini sağlayan sınıf"""
    
    @staticmethod
    def get_random_proxy():
        """Rastgele bir proxy seç"""
        if config.PROXY_LIST:
            return random.choice(config.PROXY_LIST)
        return None
    
    @staticmethod
    def get_random_user_agent():
        """Rastgele bir user agent seç"""
        ua = UserAgent()
        return ua.random
    
    @staticmethod
    def setup_driver():
        """WebDriver'ı yapılandırma ve başlatma"""
        print("WebDriver başlatılıyor...")
        
        # Chrome options
        chrome_options = uc.ChromeOptions()
        
        # Config'den ayarları al
        if config.CHROME_OPTIONS.get("headless"):
            chrome_options.add_argument("--headless=new")
        if config.CHROME_OPTIONS.get("disable_gpu"):
            chrome_options.add_argument("--disable-gpu")
        if config.CHROME_OPTIONS.get("window_size"):
            chrome_options.add_argument(f"--window-size={config.CHROME_OPTIONS['window_size']}")
        if config.CHROME_OPTIONS.get("no_sandbox"):
            chrome_options.add_argument("--no-sandbox")
        if config.CHROME_OPTIONS.get("disable_dev_shm_usage"):
            chrome_options.add_argument("--disable-dev-shm-usage")
        
        # SSL hatalarını yoksay
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        
        # Tarayıcı parmak izi ayarları
        chrome_options.add_argument(f"--platform={config.BROWSER_FINGERPRINT['platform']}")
        chrome_options.add_argument(f"--user-agent={DriverManager.get_random_user_agent()}")
        
        # Proxy ayarları - Proxy kullanımını devre dışı bıraktık
        # proxy = DriverManager.get_random_proxy()
        # if proxy:
        #     chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # İndirme tercihleri
        chrome_options.add_experimental_option("prefs", config.DOWNLOAD_PREFS)
        
        try:
            # WebDriver'ı başlat
            driver = uc.Chrome(options=chrome_options)
            
            # JavaScript ile otomasyon tespitini engelle
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            print("WebDriver başarıyla başlatıldı.")
            return driver
        except Exception as e:
            print(f"WebDriver başlatılırken hata oluştu: {str(e)}")
            raise
    
    @staticmethod
    def close_driver(driver):
        """WebDriver'ı güvenli bir şekilde kapatma"""
        try:
            if driver:
                driver.quit()
                print("WebDriver kapatıldı.")
        except Exception as e:
            print(f"WebDriver kapatılırken hata oluştu: {str(e)}")
    
    @staticmethod
    def rotate_proxy(driver):
        """Proxy'yi değiştir - Artık kullanılmıyor"""
        # Proxy kullanımını devre dışı bıraktık
        pass 