import platform
import ssl
import os
import certifi
import csv
import time
from datetime import datetime, timedelta
from ..config.config import config
from ..utils.driver_manager import DriverManager
from .document_validator import DocumentValidator
from ..utils.file_manager import FileManager

# SSL sertifika doğrulama hatasını çözmek için
if platform.system() == 'Darwin':  # macOS için
    # SSL doğrulamasını devre dışı bırak
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Certifi sertifika yolunu al ve ortam değişkenlerine ekle
    try:
        certifi_path = certifi.where()
        os.environ['SSL_CERT_FILE'] = certifi_path
        os.environ['REQUESTS_CA_BUNDLE'] = certifi_path
        print(f"SSL sertifikaları ayarlandı: {certifi_path}")
    except Exception as e:
        print(f"Certifi sertifika ayarlama hatası: {str(e)}")

# Gerekli dizinleri oluştur
def setup_directories():
    """Çalışma için gerekli dizinleri oluşturur"""
    try:
        # src dizinini bul
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Logs dizini
        logs_dir = os.path.join(src_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        print(f"Log dizini oluşturuldu/kontrol edildi: {logs_dir}")
        
        # Screenshots dizini
        screenshots_dir = os.path.join(src_dir, "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        print(f"Screenshots dizini oluşturuldu/kontrol edildi: {screenshots_dir}")
    except Exception as e:
        print(f"Dizin oluşturma hatası: {str(e)}")

def log_operation(tc_kimlik_no, barcode, result):
    """İşlem sonucunu log dosyalarına kaydet"""
    try:
        # src dizinini bul
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(src_dir, "logs")
        
        # Logs dizinini oluştur
        os.makedirs(log_dir, exist_ok=True)
        print(f"Log dizini: {log_dir}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Tüm işlemler için log dosyası
        all_log_file = os.path.join(log_dir, "all_operations.txt")
        
        # Başarısız işlemler için log dosyası
        failed_log_file = os.path.join(log_dir, "failed_operations.txt")
        
        # Log içeriğini hazırla
        log_content = f"İşlem Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_content += f"TC Kimlik No: {tc_kimlik_no}\n"
        log_content += f"Barkod No: {barcode}\n"
        log_content += f"İşlem Sonucu: {'Başarılı' if result['success'] else 'Başarısız'}\n"
        
        if not result['success']:
            log_content += f"Hata Tipi: {result['error']['error_type']}\n"
            log_content += f"Hata Mesajı: {result['error']['message']}\n"
        else:
            log_content += f"İndirilen Dosya Sayısı: {len(result['files'])}\n"
            log_content += "İndirilen Dosyalar:\n"
            for file in result['files']:
                log_content += f"- {file}\n"
        
        log_content += "\n" + "="*50 + "\n"
        
        # Tüm işlemleri log dosyasına ekle
        with open(all_log_file, "a", encoding="utf-8") as f:
            f.write(log_content)
        
        # Başarısız işlemleri ayrı dosyaya ekle
        if not result['success']:
            with open(failed_log_file, "a", encoding="utf-8") as f:
                f.write(log_content)
        
        print(f"Log dosyaları güncellendi: {all_log_file}")
        if not result['success']:
            print(f"Başarısız işlem logu güncellendi: {failed_log_file}")
            
    except Exception as e:
        print(f"Log dosyası oluşturma hatası: {str(e)}")

def process_csv_row(csv_file_path, row_index):
    """CSV dosyasından belirli bir satırı okuyup işlemi gerçekleştir"""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            rows = list(csv_reader)
            
            if row_index < len(rows):
                row = rows[row_index]
                tc_kimlik_no = row.get('tc_kimlik_no')
                barcode = row.get('barcode')
                
                if tc_kimlik_no and barcode:
                    print(f"\nİşleniyor: TC Kimlik No: {tc_kimlik_no}, Barkod: {barcode}")
                    result = validate_and_download_document(barcode, tc_kimlik_no)
                    log_operation(tc_kimlik_no, barcode, result)
                    return result, len(rows)
                else:
                    print(f"Hatalı satır: TC Kimlik No veya Barkod eksik")
                    return {
                        "success": False,
                        "error": {
                            "error_type": "missing_data",
                            "message": "TC Kimlik No veya Barkod eksik"
                        },
                        "files": []
                    }, len(rows)
            else:
                return None, len(rows)
    except Exception as e:
        print(f"CSV dosyası okuma hatası: {str(e)}")
        return {
            "success": False,
            "error": {
                "error_type": "csv_read_error",
                "message": str(e)
            },
            "files": []
        }, 0

def validate_and_download_document(barcode=None, tc_kimlik_no=None):
    """Belge doğrulama ve indirme işlemini gerçekleştir"""
    driver = None
    
    try:
        # Sistem bilgilerini göster
        print(f"İndirme dizini: {config.DOWNLOAD_DIR}")
        print(config.SYSTEM_INFO)
        
        # WebDriver'ı başlat
        driver = DriverManager.setup_driver()
        
        # Tarayıcı penceresini maksimize et
        driver.maximize_window()
        
        # İndirme işlemi öncesi mevcut dosyaları kontrol et
        file_manager = FileManager(driver)
        existing_files = file_manager.check_downloaded_files()
        print(f"İşlem öncesi klasörde bulunan dosya sayısı: {len(existing_files)}")
        
        # Belge doğrulama işlemleri
        validator = DocumentValidator(driver)
        validator.navigate_to_validation_page()
        
        # Barkod girişi
        barcode_result = validator.enter_barcode(barcode)
        if isinstance(barcode_result, dict) and not barcode_result.get('success', True):
            print(f"Barkod girişi başarısız oldu: {barcode_result['message']}")
            return {
                "success": False,
                "error": {
                    "error_type": barcode_result['error_type'],
                    "message": barcode_result['message']
                },
                "files": []
            }
        
        # TC Kimlik No doğrulama sonucunu kontrol et
        tc_validation_result = validator.enter_tc_kimlik_no(tc_kimlik_no)
        
        # TC Kimlik No doğrulama başarısız ise işlemi sonlandır
        if not tc_validation_result["success"]:
            print(f"TC Kimlik No doğrulama hatası: {tc_validation_result['message']}")
            return {
                "success": False,
                "error": {
                    "error_type": tc_validation_result['error_type'],
                    "message": tc_validation_result['message']
                },
                "files": []
            }
        
        # Onay işlemi
        if not validator.accept_terms():
            print("Onay işlemi başarısız oldu.")
            return {
                "success": False,
                "error": {
                    "error_type": "terms_acceptance_error",
                    "message": "Onay işlemi yapılamadı."
                },
                "files": []
            }
        
        # Doğrulama başarılı mı kontrol et
        validation_result = validator.is_validation_successful()
        if not validation_result.get('success', False):
            print(f"Doğrulama başarısız: {validation_result.get('message', 'Bilinmeyen hata')}")
            return {
                "success": False,
                "error": {
                    "error_type": validation_result.get('error_type', 'validation_failed'),
                    "message": validation_result.get('message', 'Belge doğrulama işlemi başarısız oldu.')
                },
                "files": []
            }
            
        # Dosya indirme bağlantısını al
        download_link, download_link_url = validator.get_download_link()
        
        if download_link and download_link_url:
            # Dosyayı indir
            if file_manager.download_file(download_link):
                # İndirilen dosyaları kontrol et
                all_files_after = file_manager.check_downloaded_files()
                
                # Eğer dosya indirilemediyse alternatif yöntemi dene
                if len(all_files_after) <= len(existing_files):
                    file_manager.download_file_alternative(download_link_url)
                    all_files_after = file_manager.check_downloaded_files()
                
                # Sadece yeni indirilen dosyaları tespit et
                new_files = [f for f in all_files_after if f not in existing_files]
                print(f"Yeni indirilen dosya sayısı: {len(new_files)}")
                
                return {
                    "success": True,
                    "files": new_files
                }
        
        return {
            "success": False,
            "error": {
                "error_type": "download_failed",
                "message": "Dosya indirme bağlantısı bulunamadı veya dosya indirilemedi."
            },
            "files": []
        }
    
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return {
            "success": False,
            "error": {
                "error_type": "system_error",
                "message": str(e)
            },
            "files": []
        }
    
    finally:
        # WebDriver'ı kapat
        DriverManager.close_driver(driver)

if __name__ == "__main__":
    # Gerekli dizinleri oluştur
    setup_directories()
    
    # Sıradaki işlenecek satırı izle
    current_row_index = 0
    
    # Devamlı çalışacak bir döngü oluştur
    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] İşlem başlatılıyor...")
            
            # CSV dosyasından TC kimlik ve barkod numaralarını oku
            csv_file_path = os.path.join(os.getcwd(), "test_data.csv")
            
            if os.path.exists(csv_file_path):
                print(f"CSV dosyasından {current_row_index+1}. satır okunuyor...")
                
                # Bir sonraki satırı işle
                result, total_rows = process_csv_row(csv_file_path, current_row_index)
                
                if result is not None:
                    # İşlem sonucunu göster
                    print(f"\nİşlem tamamlandı: {'Başarılı' if result['success'] else 'Başarısız'}")
                    
                    # Sonraki satıra geç
                    current_row_index += 1
                    
                    # Eğer son satıra geldiyse başa dön
                    if current_row_index >= total_rows:
                        print(f"\nCSV dosyasındaki tüm satırlar işlendi. Başa dönülüyor...")
                        current_row_index = 0
                else:
                    print(f"\nCSV dosyasında işlenecek satır kalmadı. Başa dönülüyor...")
                    current_row_index = 0
            else:
                print(f"CSV dosyası bulunamadı: {csv_file_path}")
                print("Lütfen 'test_data.csv' dosyasını oluşturun ve içine 'tc_kimlik_no' ve 'barcode' sütunlarını ekleyin.")
            
            # 2 saat bekle
            wait_time_seconds = 2 * 60 * 60  # 2 saat = 7200 saniye
            next_run_time = datetime.now() + timedelta(seconds=wait_time_seconds)
            print(f"\n[{current_time}] İşlem tamamlandı. Sonraki çalışma zamanı: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if current_row_index == 0:
                print(f"2 saat ({wait_time_seconds} saniye) bekleniyor... Süre sonunda CSV dosyasının ilk satırından tekrar başlanacak.")
            else:
                print(f"2 saat ({wait_time_seconds} saniye) bekleniyor... Süre sonunda CSV dosyasının {current_row_index+1}. satırı işlenecek.")
            
            time.sleep(wait_time_seconds)
    
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\nHata oluştu: {str(e)}")
        raise 