import os
import platform
import random
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    # İndirilen dosyaların kaydedileceği klasör
    DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    # Chrome ayarları
    CHROME_OPTIONS = {
        "headless": False,  # Captcha için headless modu kapalı tutuyoruz
        "disable_gpu": True,
        "window_size": "1920,1080",
        "no_sandbox": True,
        "disable_dev_shm_usage": True,
        "disable-blink-features=AutomationControlled": True,
        "disable-extensions": True,
        "disable-infobars": True,
        "disable-notifications": True,
        "disable-popup-blocking": True,
        "disable-save-password-bubble": True,
        "disable-translate": True,
        "disable-web-security": True,
        "ignore-certificate-errors": True,
        "ignore-ssl-errors": True,
        "start-maximized": True
    }

    # İndirme tercihleri
    DOWNLOAD_PREFS = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }

    # E-Devlet URL'leri
    EDEVLET_BELGE_DOGRULAMA_URL = "https://www.turkiye.gov.tr/belge-dogrulama"

    # Belge bilgileri
    BARCODE_NUMBER = "ADB02978118577"
    TC_KIMLIK_NO = "23327276170"

    # Sistem bilgileri
    SYSTEM_INFO = f"İşletim sistemi: {platform.system()} {platform.machine()}"

    # Proxy ayarları - Proxy kullanımını devre dışı bırakmak için boş liste
    PROXY_LIST = []

    # Bekleme süreleri (saniye)
    WAIT_TIMES = {
        "min": 1,
        "max": 3,
        "page_load": 5,
        "element_load": 2
    }

    # İnsan benzeri davranış ayarları
    HUMAN_BEHAVIOR = {
        "mouse_movement_speed": random.uniform(0.5, 1.5),
        "scroll_speed": random.uniform(0.3, 0.8),
        "typing_speed": random.uniform(0.1, 0.3),
        "pause_between_actions": random.uniform(0.5, 2.0)
    }

    # Tarayıcı parmak izi ayarları
    BROWSER_FINGERPRINT = {
        "platform": "Win32",
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Ti Direct3D11 vs_5_0 ps_5_0)",
        "hardware_concurrency": 8,
        "device_memory": 8,
        "color_depth": 24,
        "pixel_ratio": 1
    }

# Global config nesnesi
config = Config() 