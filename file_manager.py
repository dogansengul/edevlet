import os
import time
import config
import platform
import ssl
import requests
from urllib3.exceptions import InsecureRequestWarning

# SSL sertifika doğrulama hatasını çözmek için
if platform.system() == 'Darwin':  # macOS için
    ssl._create_default_https_context = ssl._create_unverified_context
    # Uyarıları bastır
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class FileManager:
    """Dosya indirme ve yönetme işlemlerini sağlayan sınıf"""
    
    def __init__(self, driver):
        self.driver = driver
        self.download_dir = config.DOWNLOAD_DIR
    
    def download_file(self, download_link):
        """Dosyayı indir"""
        try:
            print("Dosya indirme bağlantısına tıklanıyor...")
            # Önce JavaScript ile scroll yap
            self.driver.execute_script("arguments[0].scrollIntoView(true);", download_link)
            time.sleep(1)  # Scroll işleminin tamamlanmasını bekle
            
            try:
                # Önce normal tıklama dene
                download_link.click()
            except Exception as click_error:
                print(f"Normal tıklama başarısız oldu, JavaScript ile deneniyor: {str(click_error)}")
                # JavaScript ile tıkla
                self.driver.execute_script("arguments[0].click();", download_link)
            
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
            
            # SSL hatalarını yoksayarak indirme
            if platform.system() == 'Darwin':  # macOS için
                try:
                    # Requests ile indirme dene
                    print(f"Requests ile indirme deneniyor: {download_link_url}")
                    response = requests.get(download_link_url, verify=False, stream=True)
                    
                    if response.status_code == 200:
                        # Dosya adını URL'den çıkar
                        filename = download_link_url.split('/')[-1]
                        if not filename.endswith('.pdf'):
                            filename = f"downloaded_document_{int(time.time())}.pdf"
                        
                        # Dosyayı kaydet
                        file_path = os.path.join(self.download_dir, filename)
                        with open(file_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        print(f"Dosya başarıyla indirildi: {file_path}")
                        return True
                except Exception as e:
                    print(f"Requests ile indirme hatası: {str(e)}")
            
            # Tarayıcı ile indirme
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