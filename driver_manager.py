from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import config

class DriverManager:
    """WebDriver kurulumu ve yönetimini sağlayan sınıf"""
    
    @staticmethod
    def setup_driver():
        """WebDriver'ı yapılandırma ve başlatma"""
        print("WebDriver başlatılıyor...")
        
        # Chrome options
        chrome_options = Options()
        
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
        
        # İndirme tercihleri
        chrome_options.add_experimental_option("prefs", config.DOWNLOAD_PREFS)
        
        try:
            # WebDriver'ı başlat
            driver = webdriver.Chrome(options=chrome_options)
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