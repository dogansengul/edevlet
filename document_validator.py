from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import config
from human_behavior import HumanBehaviorSimulator

class DocumentValidator:
    """E-Devlet belge doğrulama işlemlerini yöneten sınıf"""
    
    def __init__(self, driver):
        self.driver = driver
        self.human = HumanBehaviorSimulator(driver)
    
    def navigate_to_validation_page(self):
        """Belge doğrulama sayfasına git"""
        print("Web sayfasına gidiliyor...")
        self.driver.get(config.EDEVLET_BELGE_DOGRULAMA_URL)
        self.human.random_sleep(2, 4)  # Sayfa yüklenme süresi
        print("Belge doğrulama sayfasına ulaşıldı.")
        
        # Sayfa yüklendikten sonra insan benzeri davranışlar sergile
        self.human.simulate_human_behavior()
    
    def enter_barcode(self, barcode=None):
        """Barkod numarasını gir"""
        if barcode is None:
            barcode = config.BARCODE_NUMBER
            
        try:
            print("Barkod numarası alanı bulunuyor...")
            barcode_input = self.human.wait_for_element(By.ID, "sorgulananBarkod")
            print("Barkod numarası alanı bulundu.")
            
            # İnsan benzeri yazma davranışı
            self.human.human_like_type(barcode_input, barcode)
            
            print("Devam Et butonuna tıklanıyor...")
            submit_button = self.human.wait_for_clickable(By.CSS_SELECTOR, "input.submitButton")
            self.human.human_like_click(submit_button)
            print("Devam Et butonuna tıklandı.")
            
            self.human.random_sleep(1, 2)
            return True
        except Exception as e:
            print(f"Barkod girişi sırasında hata: {str(e)}")
            # Alternatif yöntem dene
            try:
                print("Alternatif barkod girişi yöntemi deneniyor...")
                barcode_input = self.driver.find_element(By.ID, "sorgulananBarkod")
                barcode_input.clear()
                barcode_input.send_keys(barcode)
                
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
                self.driver.execute_script("arguments[0].click();", submit_button)
                
                self.human.random_sleep(1, 2)
                return True
            except Exception as alt_e:
                print(f"Alternatif barkod girişi sırasında hata: {str(alt_e)}")
                return False
    
    def enter_tc_kimlik_no(self, tc_kimlik_no=None):
        """TC Kimlik numarasını gir"""
        if tc_kimlik_no is None:
            tc_kimlik_no = config.TC_KIMLIK_NO
            
        try:
            print("İkinci alandaki input bulunuyor...")
            # Sayfanın yüklenmesi için biraz bekle
            self.human.random_sleep(2, 3)
            
            # Sayfayı yukarı kaydır (TC Kimlik No alanı genellikle sayfanın üst kısmında olur)
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.human.random_sleep(1, 2)
            
            # Önce elementin varlığını kontrol et
            second_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ikinciAlan"))
            )
            print("İkinci alandaki input bulundu.")
            
            # Elemente scroll yap
            self.human.scroll_to_element(second_input)
            self.human.random_sleep(1, 2)
            
            # JavaScript ile değer ata ve tıkla (daha güvenilir)
            self.driver.execute_script(f"arguments[0].value = '{tc_kimlik_no}';", second_input)
            self.human.random_sleep(0.5, 1)
            
            print("Devam Et butonuna tekrar tıklanıyor...")
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.submitButton"))
            )
            
            # JavaScript ile tıkla
            self.driver.execute_script("arguments[0].click();", submit_button)
            print("Devam Et butonuna tekrar tıklandı.")
            
            self.human.random_sleep(2, 4)
            
            # TC Kimlik No doğrulama kontrolü
            validation_result = self.check_tc_kimlik_validation()
            return validation_result
        except Exception as e:
            print(f"TC Kimlik No girişi sırasında hata: {str(e)}")
            # Alternatif yöntem dene
            try:
                print("Alternatif TC Kimlik No girişi yöntemi deneniyor...")
                second_input = self.driver.find_element(By.ID, "ikinciAlan")
                second_input.clear()
                second_input.send_keys(tc_kimlik_no)
                
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
                self.driver.execute_script("arguments[0].click();", submit_button)
                
                self.human.random_sleep(2, 4)
                
                # TC Kimlik No doğrulama kontrolü
                validation_result = self.check_tc_kimlik_validation()
                return validation_result
            except Exception as alt_e:
                print(f"Alternatif TC Kimlik No girişi sırasında hata: {str(alt_e)}")
                return {
                    "success": False,
                    "error_type": "input_error",
                    "message": f"TC Kimlik No girişi yapılamadı: {str(alt_e)}"
                }
    
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
        try:
            print("Checkbox bulunuyor ve işaretleniyor...")
            checkbox = self.human.wait_for_clickable(By.ID, "chkOnay")
            self.human.human_like_click(checkbox)
            print("Checkbox işaretlendi.")
            
            print("Devam Et butonuna tekrar tıklanıyor...")
            self.human.random_sleep(1, 2)
            submit_button = self.human.wait_for_clickable(By.CSS_SELECTOR, "input.submitButton")
            self.human.human_like_click(submit_button)
            print("Devam Et butonuna tekrar tıklandı.")
            
            self.human.random_sleep(2, 4)
            return True
        except Exception as e:
            print(f"Onay işlemi sırasında hata: {str(e)}")
            # Alternatif yöntem dene
            try:
                print("Alternatif onay işlemi yöntemi deneniyor...")
                checkbox = self.driver.find_element(By.ID, "chkOnay")
                self.driver.execute_script("arguments[0].click();", checkbox)
                
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
                self.driver.execute_script("arguments[0].click();", submit_button)
                
                self.human.random_sleep(2, 4)
                return True
            except Exception as alt_e:
                print(f"Alternatif onay işlemi sırasında hata: {str(alt_e)}")
                return False
    
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
        try:
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
        except Exception as e:
            print(f"Doğrulama kontrolü sırasında hata: {str(e)}")
            return False
    
    def get_download_link(self):
        """Dosya indirme bağlantısını bul"""
        try:
            download_link = self.human.wait_for_element(By.CSS_SELECTOR, "a.download")
            download_link_url = download_link.get_attribute("href")
            print(f"Dosya indirme bağlantısı bulundu: {download_link_url}")
            return download_link, download_link_url
        except Exception as e:
            print(f"Dosya indirme bağlantısında hata: {str(e)}")
            return None, None 