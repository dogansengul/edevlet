import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import random
from ..config.config import config
import os
import ssl
import platform
from fake_useragent import UserAgent
import time
import subprocess
import re

# SSL sertifika doğrulama hatasını çözmek için
if platform.system() == 'Darwin':  # macOS için
    ssl._create_default_https_context = ssl._create_unverified_context

class DriverManager:
    """WebDriver kurulumu ve yönetimini sağlayan sınıf"""
    
    @staticmethod
    def get_chrome_version():
        """Chrome tarayıcı sürümünü tespit et"""
        try:
            if platform.system() == 'Darwin':  # macOS
                result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                      capture_output=True, text=True)
            elif platform.system() == 'Linux':
                result = subprocess.run(['google-chrome', '--version'], 
                                      capture_output=True, text=True)
            elif platform.system() == 'Windows':
                result = subprocess.run(['chrome.exe', '--version'], 
                                      capture_output=True, text=True)
            else:
                return None
                
            if result.returncode == 0:
                version_match = re.search(r'(\d+)\.\d+\.\d+\.\d+', result.stdout)
                if version_match:
                    return int(version_match.group(1))
        except Exception as e:
            print(f"Chrome sürümü tespit edilemedi: {e}")
        return None
    
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

        chrome_options.add_argument("--disable-gpu")  # GPU kullanımını devre dışı bırak
        chrome_options.add_argument("--remote-allow-origins=*")  # CORS sorunlarını çöz
        chrome_options.add_argument("--enable-javascript")  # JavaScript'i zorla etkinleştir
        
        # Linux için gerekli ek ayarlar
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        if config.CHROME_OPTIONS.get("window_size"):
            chrome_options.add_argument(f"--window-size={config.CHROME_OPTIONS['window_size']}")
        
        # SSL hatalarını yoksay
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        
        # JavaScript hatalarını önlemek için ek ayarlar
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Tarayıcı parmak izi ayarları
        chrome_options.add_argument(f"--platform={config.BROWSER_FINGERPRINT['platform']}")
        chrome_options.add_argument(f"--user-agent={DriverManager.get_random_user_agent()}")
        #chrome_options.add_argument("--headless=new")  # Yeni headless modu kullan
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-software-rasterizer")
        
        # İndirme tercihleri
        chrome_options.add_experimental_option("prefs", config.DOWNLOAD_PREFS)
        
        try:
            # Chrome sürümünü tespit et
            chrome_version = DriverManager.get_chrome_version()
            if chrome_version:
                print(f"Tespit edilen Chrome sürümü: {chrome_version}")
            
            # Headless parametresini doğrudan Chrome sınıfına geçiriyoruz, options'a değil
            is_headless = config.CHROME_OPTIONS.get("headless", False)
            
            # WebDriver'ı başlat - otomatik sürüm algılaması ile
            if chrome_version:
                driver = uc.Chrome(
                    options=chrome_options,
                    headless=is_headless,
                    use_subprocess=True,
                    version_main=chrome_version
                )
            else:
                # Sürüm tespit edilemezse otomatik algılamaya bırak
                driver = uc.Chrome(
                    options=chrome_options,
                    headless=is_headless,
                    use_subprocess=True
                )
            
            # Chrome'un tamamen yüklenmesi için bekle
            time.sleep(3)
            
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