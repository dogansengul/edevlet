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

    # Chrome ayarları - .env'den alınır
    CHROME_OPTIONS = {
        "headless": os.getenv('HEADLESS', 'false').lower() == 'true',
        "disable_gpu": True,
        "window_size": os.getenv('WINDOW_SIZE', '1920,1080'),
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

    # Backend API ayarları
    BACKEND_API_BASE_URL = os.getenv('BACKEND_API_BASE_URL', 'https://shut-b0g3czdtc0fgajbq.northeurope-01.azurewebsites.net/')
    BACKEND_API_EMAIL = os.getenv('BACKEND_API_EMAIL')
    BACKEND_API_PASSWORD = os.getenv('BACKEND_API_PASSWORD')
    
    # Document processing configuration
    # Control which documents should be processed based on documentVerified status
    PROCESS_DOCUMENTS_CONFIG = {
        "process_null_documents": True,    # Process documents with documentVerified=null
        "process_false_documents": False,  # Process documents with documentVerified=false
        "process_true_documents": False    # Process documents with documentVerified=true (re-verification)
    }

    # Processing intervals - .env'den alınır
    PROCESSING_WAIT_INTERVAL_SECONDS = int(os.getenv('PROCESSING_WAIT_INTERVAL_SECONDS', 600))

    # Security settings - IP Whitelist for Event Receiver
    ALLOWED_IPS = os.getenv('ALLOWED_IPS', '127.0.0.1,::1').split(',') if os.getenv('ALLOWED_IPS') else [
        "127.0.0.1",           # Localhost IPv4
        "::1",                 # Localhost IPv6
        "192.168.1.0/24",      # Local network range (example)
    ]

    # Production Settings - .env'den alınır
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Production optimizations
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    WORKER_TIMEOUT = int(os.getenv('WORKER_TIMEOUT', 120))
    MAX_REQUESTS = int(os.getenv('MAX_REQUESTS', 10000))
    
    # Monitoring
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 300))
    
    # Logging configuration
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

    # Sistem bilgileri
    SYSTEM_INFO = f"İşletim sistemi: {platform.system()} {platform.machine()}"

    # Proxy ayarları - Proxy kullanımını devre dışı bırakmak için boş liste
    PROXY_LIST = []

    # Bekleme süreleri (saniye) - .env'den alınır
    WAIT_TIMES = {
        "min": int(os.getenv('MIN_WAIT', 1)),
        "max": int(os.getenv('MAX_WAIT', 3)),
        "page_load": int(os.getenv('PAGE_LOAD_WAIT', 5)),
        "element_load": int(os.getenv('ELEMENT_LOAD_WAIT', 2))
    }

    # İnsan benzeri davranış ayarları - .env'den alınır
    HUMAN_BEHAVIOR = {
        "mouse_movement_speed": float(os.getenv('MOUSE_MOVEMENT_SPEED', 0.8)),
        "scroll_speed": float(os.getenv('SCROLL_SPEED', 0.5)),
        "typing_speed": float(os.getenv('TYPING_SPEED', 0.2)),
        "pause_between_actions": float(os.getenv('PAUSE_BETWEEN_ACTIONS', 1.0))
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

    # Validation - Required environment variables kontrolü
    @classmethod
    def validate_required_config(cls):
        """Required environment variables'ları kontrol et."""
        required_vars = [
            'BACKEND_API_EMAIL',
            'BACKEND_API_PASSWORD',
            'SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Global config nesnesi
config = Config()

# Production'da required variables'ları kontrol et
if config.FLASK_ENV == 'production':
    config.validate_required_config()
