import config
import platform
import ssl
import os
import certifi
from driver_manager import DriverManager
from document_validator import DocumentValidator
from file_manager import FileManager

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
        
        # Belge doğrulama işlemleri
        validator = DocumentValidator(driver)
        validator.navigate_to_validation_page()
        
        # Barkod girişi
        if not validator.enter_barcode(barcode):
            print("Barkod girişi başarısız oldu.")
            return {
                "success": False,
                "error": {
                    "error_type": "barcode_input_error",
                    "message": "Barkod girişi yapılamadı."
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
                "error": tc_validation_result,
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
        if validator.is_validation_successful():
            # Dosya indirme bağlantısını al
            download_link, download_link_url = validator.get_download_link()
            
            if download_link and download_link_url:
                # Dosya yöneticisini başlat
                file_manager = FileManager(driver)
                
                # Dosyayı indir
                if file_manager.download_file(download_link):
                    # İndirilen dosyaları kontrol et
                    pdf_files = file_manager.check_downloaded_files()
                    
                    # Eğer dosya indirilemediyse alternatif yöntemi dene
                    if not pdf_files:
                        file_manager.download_file_alternative(download_link_url)
                        pdf_files = file_manager.check_downloaded_files()
                    
                    return {
                        "success": True,
                        "files": pdf_files
                    }
        
        return {
            "success": False,
            "error": {
                "error_type": "validation_failed",
                "message": "Belge doğrulama işlemi başarısız oldu."
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
        # print(f"İndirilen dosyalar şu klasörde bulunabilir: {config.DOWNLOAD_DIR}")

if __name__ == "__main__":
    # Varsayılan değerlerle çalıştır
    result = validate_and_download_document()
    
    if result["success"]:
        print(f"\nİşlem başarılı! {len(result['files'])} dosya indirildi.")
        for file in result["files"]:
            print(f"- {file}")
    else:
        print("\nİşlem başarısız oldu.")
        print(f"Hata: {result['error']['message']}")
    
    # Örnek: Özel parametrelerle çalıştırma
    # result = validate_and_download_document(
    #     barcode="ÖZEL_BARKOD_NUMARASI", 
    #     tc_kimlik_no="ÖZEL_TC_KIMLIK_NO"
    # ) 