from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import platform

# İndirilen dosyaların kaydedileceği klasör
download_dir = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

print(f"İndirme dizini: {download_dir}")
print(f"İşletim sistemi: {platform.system()} {platform.machine()}")
q
# Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Yeni headless modu
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# İndirme tercihleri
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True  # PDF'leri otomatik olarak indir
}
chrome_options.add_experimental_option("prefs", prefs)

try:
    print("WebDriver başlatılıyor...")
    # Yeni Selenium sürümü ile basitleştirilmiş başlatma
    driver = webdriver.Chrome(options=chrome_options)
    print("WebDriver başarıyla başlatıldı.")
    
    print("Web sayfasına gidiliyor...")
    driver.get("https://www.turkiye.gov.tr/belge-dogrulama")

    print("Barkod numarası alanı bulunuyor...")
    barcode_input = driver.find_element(By.ID, "sorgulananBarkod")
    print("Barkod numarası alanı bulundu.")

    barcode_number = "ADB02291277363" # Belge Barkod numarası
    barcode_input.send_keys(barcode_number)

    print("Devam Et butonuna tıklanıyor...")
    submit_button = driver.find_element(By.CSS_SELECTOR, "input.submitButton")
    submit_button.click()
    print("Devam Et butonuna tıklandı.")

    time.sleep(1)

    print("İkinci alandaki input bulunuyor...")
    second_input = driver.find_element(By.ID, "ikinciAlan")
    print("İkinci alandaki input bulundu.")

    second_value = "23327276170"  # TC Kimlik No
    second_input.send_keys(second_value)

    print("Devam Et butonuna tekrar tıklanıyor...")
    submit_button = driver.find_element(By.CSS_SELECTOR, "input.submitButton")
    submit_button.click()
    print("Devam Et butonuna tekrar tıklandı.")

    time.sleep(3)  

    print("Checkbox bulunuyor ve işaretleniyor...")
    checkbox = driver.find_element(By.ID, "chkOnay")
    checkbox.click()
    print("Checkbox işaretlendi.")

    print("Devam Et butonuna tekrar tıklanıyor...")
    time.sleep(2)
    submit_button = driver.find_element(By.CSS_SELECTOR, "input.submitButton")
    submit_button.click()
    print("Devam Et butonuna tekrar tıklandı.")

    time.sleep(3)

    current_url = driver.current_url
    if "belge=goster" in current_url or "belge-dogrulama" in current_url:
        print("İşlem başarılı! Sonuç sayfasına ulaşıldı.")
        
        # Dosyayı indir bağlantısını bulma ve tıklama
        try:
            download_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.download"))
            )
            download_link_url = download_link.get_attribute("href")
            print(f"Dosya indirme bağlantısı bulundu: {download_link_url}")
            
            # Bağlantıya tıklama
            download_link.click()
            print("Dosya indirme bağlantısına tıklandı.")
            
            # Dosyanın indirilmesini bekle
            time.sleep(3)
        
            # İndirilen dosyaları kontrol et
            downloaded_files = os.listdir(download_dir)
            pdf_files = [f for f in downloaded_files if f.endswith('.pdf')]
            
            if pdf_files:
                print("İndirilen PDF dosyaları:")
                for pdf_file in pdf_files:
                    full_path = os.path.join(download_dir, pdf_file)
                    file_size = os.path.getsize(full_path) / 1024  # KB olarak boyut
                    print(f"- {pdf_file} ({file_size:.2f} KB)")
                    print(f"  Tam konum: {full_path}")
            else:
                print("İndirilen PDF dosyası bulunamadı.")
                
                # Plan B: Doğrudan URL'e git ve indirmeyi dene
                print("Alternatif indirme yöntemi deneniyor...")
                driver.get(download_link_url)
                time.sleep(5)
                
                # Tekrar kontrol et
                downloaded_files = os.listdir(download_dir)
                pdf_files = [f for f in downloaded_files if f.endswith('.pdf')]
                
                if pdf_files:
                    print("İndirilen PDF dosyaları (alternatif yöntem sonrası):")
                    for pdf_file in pdf_files:
                        full_path = os.path.join(download_dir, pdf_file)
                        file_size = os.path.getsize(full_path) / 1024  # KB olarak boyut
                        print(f"- {pdf_file} ({file_size:.2f} KB)")
                        print(f"  Tam konum: {full_path}")
                else:
                    print("Alternatif yöntem sonrası da PDF dosyası bulunamadı.")
        
        except Exception as e:
            print(f"Dosya indirme bağlantısında hata: {str(e)}")
    else:
        print(f"Beklenmedik bir durum oluştu. URL: {current_url}")
        
    print("\nİşlem tamamlandı.")
    
except Exception as e:
    print(f"Hata oluştu: {str(e)}")
        
finally:
    try:
        driver.quit()
        print("WebDriver kapatıldı.")
    except:
        pass
    print(f"İndirilen dosyalar şu klasörde bulunabilir: {download_dir}")