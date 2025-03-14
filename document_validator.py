from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import config

class DocumentValidator:
    """E-Devlet belge doğrulama işlemlerini yöneten sınıf"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def navigate_to_validation_page(self):
        """Belge doğrulama sayfasına git"""
        print("Web sayfasına gidiliyor...")
        self.driver.get(config.EDEVLET_BELGE_DOGRULAMA_URL)
        print("Belge doğrulama sayfasına ulaşıldı.")
    
    def enter_barcode(self, barcode=None):
        """Barkod numarasını gir"""
        if barcode is None:
            barcode = config.BARCODE_NUMBER
            
        print("Barkod numarası alanı bulunuyor...")
        barcode_input = self.driver.find_element(By.ID, "sorgulananBarkod")
        print("Barkod numarası alanı bulundu.")
        
        barcode_input.send_keys(barcode)
        
        print("Devam Et butonuna tıklanıyor...")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
        submit_button.click()
        print("Devam Et butonuna tıklandı.")
        
        time.sleep(1)
    
    def enter_tc_kimlik_no(self, tc_kimlik_no=None):
        """TC Kimlik numarasını gir"""
        if tc_kimlik_no is None:
            tc_kimlik_no = config.TC_KIMLIK_NO
            
        print("İkinci alandaki input bulunuyor...")
        second_input = self.driver.find_element(By.ID, "ikinciAlan")
        print("İkinci alandaki input bulundu.")
        
        second_input.send_keys(tc_kimlik_no)
        
        print("Devam Et butonuna tekrar tıklanıyor...")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
        submit_button.click()
        print("Devam Et butonuna tekrar tıklandı.")
        
        time.sleep(3)
        
        # TC Kimlik No doğrulama kontrolü
        validation_result = self.check_tc_kimlik_validation()
        return validation_result
    
    def check_tc_kimlik_validation(self):
        """TC Kimlik numarası doğrulama sonucunu kontrol et"""
        try:
            # Hata mesajı içeren div'i kontrol et
            error_div = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored")
            
            if error_div:
                # Hata mesajını bul
                error_message = self.driver.find_element(By.ID, "ikinciAlan-error").text
                print(f"TC Kimlik No Hatası: {error_message}")
                return {
                    "success": False,
                    "error_type": "tc_kimlik_error",
                    "message": error_message
                }
            
            # Hata yoksa başarılı
            return {
                "success": True
            }
            
        except Exception as e:
            print(f"TC Kimlik No doğrulama kontrolünde hata: {str(e)}")
            return {
                "success": False,
                "error_type": "unknown_error",
                "message": f"Beklenmeyen bir hata oluştu: {str(e)}"
            }
    
    def accept_terms(self):
        """Onay kutusunu işaretle ve devam et"""
        print("Checkbox bulunuyor ve işaretleniyor...")
        checkbox = self.driver.find_element(By.ID, "chkOnay")
        checkbox.click()
        print("Checkbox işaretlendi.")
        
        print("Devam Et butonuna tekrar tıklanıyor...")
        time.sleep(2)
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
        submit_button.click()
        print("Devam Et butonuna tekrar tıklandı.")
        
        time.sleep(3)
    
    def check_invalid_barcode_warning(self):
        """Geçersiz barkod uyarısını kontrol et"""
        try:
            warning_container = self.driver.find_elements(By.CSS_SELECTOR, "div.warningContainer[role='alert']")
            if warning_container:
                warning_text = warning_container[0].find_element(By.TAG_NAME, "span").text
                print(f"Geçersiz barkod uyarısı: {warning_text}")
                return True
            return False
        except Exception as e:
            print(f"Barkod uyarı kontrolünde hata: {str(e)}")
            return False

    def is_validation_successful(self):
        """Doğrulama işleminin başarılı olup olmadığını kontrol et"""
        # Önce geçersiz barkod uyarısını kontrol et
        if self.check_invalid_barcode_warning():
            print("Geçersiz barkod numarası tespit edildi!")
            return False
            
        current_url = self.driver.current_url
        if "belge=goster" in current_url or "belge-dogrulama" in current_url:
            print("İşlem başarılı! Sonuç sayfasına ulaşıldı.")
            return True
        else:
            print(f"Beklenmedik bir durum oluştu. URL: {current_url}")
            return False
    
    def get_download_link(self):
        """Dosya indirme bağlantısını bul"""
        try:
            download_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.download"))
            )
            download_link_url = download_link.get_attribute("href")
            print(f"Dosya indirme bağlantısı bulundu: {download_link_url}")
            return download_link, download_link_url
        except Exception as e:
            print(f"Dosya indirme bağlantısında hata: {str(e)}")
            return None, None 