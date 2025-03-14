import os
import platform

# İndirilen dosyaların kaydedileceği klasör
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Chrome ayarları
CHROME_OPTIONS = {
    "headless": True,  # Headless mod
    "disable_gpu": True,
    "window_size": "1920,1080",
    "no_sandbox": True,
    "disable_dev_shm_usage": True
}

# İndirme tercihleri
DOWNLOAD_PREFS = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True  # PDF'leri otomatik olarak indir
}

# E-Devlet URL'leri
EDEVLET_BELGE_DOGRULAMA_URL = "https://www.turkiye.gov.tr/belge-dogrulama"

# Belge bilgileri (gerçek uygulamada bu bilgiler parametre olarak alınabilir)
BARCODE_NUMBER = "ADB02978118576"  # Belge Barkod numarası
TC_KIMLIK_NO = "23327276170"  # TC Kimlik No

# Sistem bilgileri
SYSTEM_INFO = f"İşletim sistemi: {platform.system()} {platform.machine()}" 