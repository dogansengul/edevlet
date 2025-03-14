import os
import time
import config

class FileManager:
    """Dosya indirme ve yönetme işlemlerini sağlayan sınıf"""
    
    def __init__(self, driver):
        self.driver = driver
        self.download_dir = config.DOWNLOAD_DIR
    
    def download_file(self, download_link):
        """Dosyayı indir"""
        try:
            print("Dosya indirme bağlantısına tıklanıyor...")
            download_link.click()
            print("Dosya indirme bağlantısına tıklandı.")
            
            # Dosyanın indirilmesini bekle
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Dosya indirme sırasında hata: {str(e)}")
            return False
    
    def download_file_alternative(self, download_link_url):
        """Alternatif dosya indirme yöntemi"""
        try:
            print("Alternatif indirme yöntemi deneniyor...")
            self.driver.get(download_link_url)
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Alternatif indirme sırasında hata: {str(e)}")
            return False
    
    def check_downloaded_files(self):
        """İndirilen dosyaları kontrol et"""
        downloaded_files = os.listdir(self.download_dir)
        pdf_files = [f for f in downloaded_files if f.endswith('.pdf')]
        
        if pdf_files:
            print("İndirilen PDF dosyaları:")
            for pdf_file in pdf_files:
                full_path = os.path.join(self.download_dir, pdf_file)
                file_size = os.path.getsize(full_path) / 1024  # KB olarak boyut
                print(f"- {pdf_file} ({file_size:.2f} KB)")
                print(f"  Tam konum: {full_path}")
            return pdf_files
        else:
            print("İndirilen PDF dosyası bulunamadı.")
            return [] 