from selenium.webdriver.common.by import By
import time
import logging
from ..config.config import config
from .human_behavior import HumanBehaviorSimulator
from .mixins.element_finder import ElementFinderMixin
from .mixins.error_handler import ErrorHandlerMixin
from .factories.strategy_factory import StrategyFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('edevlet_automation.log')
    ]
)
logger = logging.getLogger("DocumentValidator")

class DocumentValidator(ElementFinderMixin, ErrorHandlerMixin):
    """E-Devlet belge doğrulama işlemlerini yöneten sınıf"""
    
    def __init__(self, driver):
        self.driver = driver
        self.human = HumanBehaviorSimulator(driver)
        logger.info("DocumentValidator başlatıldı")
    
    def navigate_to_validation_page(self):
        """Belge doğrulama sayfasına git"""
        try:
            logger.info("Web sayfasına gidiliyor...")
            self.driver.get(config.EDEVLET_BELGE_DOGRULAMA_URL)
            self.human.random_sleep(2, 4)  # Sayfa yüklenme süresi
            logger.info("Belge doğrulama sayfasına ulaşıldı.")
            
            # Sayfa yüklendikten sonra insan benzeri davranışlar sergile
            self.human.simulate_human_behavior()
            return {"success": True}
        except Exception as e:
            return self.handle_error("Doğrulama sayfasına gidilirken hata oluştu", e, "navigation_error")
    
    def enter_barcode(self, barcode=None):
        """Barkod numarasını gir"""
        if barcode is None:
            barcode = config.BARCODE_NUMBER
        
        logger.info(f"Barkod numarası giriliyor: {barcode}")
        
        try:
            # Barkod giriş alanını bul
            barcode_input = self.find_element_with_strategies(
                StrategyFactory.get_strategies_for("barcode_input"), 
                "Barkod giriş alanı"
            )
            
            if not barcode_input:
                return self.handle_error("Barkod giriş alanı bulunamadı", "Element not found", "element_not_found")
            
            # İnsan benzeri yazma davranışı
            self.human.human_like_type(barcode_input, barcode)
            
            # Submit butonunu bul
            submit_button = self.find_element_with_strategies(
                StrategyFactory.get_strategies_for("submit_button"),
                "Devam Et butonu"
            )
            
            if not submit_button:
                return self.handle_error("Devam Et butonu bulunamadı", "Element not found", "element_not_found")
                
            # Butona tıkla
            self.human.human_like_click(submit_button)
            self.human.random_sleep(1, 2)
            
            # Hata kontrolü
            return self.check_barcode_errors()
            
        except Exception as e:
            return self.handle_error("Barkod girişi sırasında hata oluştu", e, "barcode_input_error")
    
    def check_barcode_errors(self):
        """Barkod girişinden sonra olası hataları kontrol et"""
        try:
            # Hata containerlarını kontrol et
            error_container = self.find_element_with_strategies(
                StrategyFactory.get_strategies_for("error_container"), 
                "Hata mesajı", 
                screenshot_on_fail=False
            )
            
            if error_container:
                error_text = error_container.text
                logger.warning(f"Barkod hatası tespit edildi: {error_text}")
                
                # Hata türüne göre özel mesaj döndür
                if "Lütfen geçerli bir barkod numarası giriniz" in error_text:
                    return {
                        "success": False,
                        "error_type": "invalid_barcode_format",
                        "message": "Barkod numarası formatı geçersiz. Lütfen doğru formatı kullanın."
                    }
                elif "Girilen barkod numarası e-Devlet Kapısında tanımlı değildir" in error_text:
                    return {
                        "success": False,
                        "error_type": "barcode_not_registered",
                        "message": "Barkod numarası e-Devlet sisteminde tanımlı değil."
                    }
                else:
                    return {
                        "success": False,
                        "error_type": "barcode_error",
                        "message": f"Barkod hatası: {error_text}"
                    }
            
            # Hata yoksa başarılı
            return {"success": True}
        except Exception as e:
            return self.handle_error("Barkod hatası kontrolünde sorun", e, "barcode_check_error")
    
    def enter_tc_kimlik_no(self, tc_kimlik_no=None):
        """TC Kimlik numarasını gir"""
        if tc_kimlik_no is None:
            tc_kimlik_no = config.TC_KIMLIK_NO
        
        logger.info(f"TC Kimlik No giriliyor: {tc_kimlik_no}")
        
        # Sayfanın yüklenmesi için bekle
        self.human.random_sleep(3, 5)
        
        # URL ve sayfa başlığını kaydet (geçiş kontrolü için)
        before_url = self.driver.current_url
        before_title = self.driver.title
        
        try:
            # TC Kimlik No giriş alanını bul
            tc_input = self.find_element_with_strategies(
                StrategyFactory.get_strategies_for("tc_kimlik_input"),
                "TC Kimlik No giriş alanı"
            )
            
            if not tc_input:
                return self.handle_error("TC Kimlik No alanı bulunamadı", "Element not found", "tc_input_not_found")
            
            # Görünür olana kadar bekle ve scroll yap
            self.human.scroll_to_element(tc_input)
            self.human.random_sleep(1, 2)
            
            # İnsan benzeri yazma davranışıyla doldur
            tc_input.click()
            tc_input.clear()
            self.human.human_like_type(tc_input, tc_kimlik_no)
            logger.info("TC Kimlik No insan benzeri davranışla girildi")
            
            # Form içeriğini kaydet (değişim kontrolü için)
            before_form_error = len(self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored"))
            before_page_content = self.driver.page_source
            
            # Submit butonunu bul
            submit_button = self.find_element_with_strategies(
                StrategyFactory.get_strategies_for("submit_button"),
                "Devam Et butonu"
            )
            
            if not submit_button:
                # Butonu bulamazsak form submit etmeyi dene
                logger.warning("Devam Et butonu bulunamadı, form submit etmeyi deniyorum...")
                form = self.driver.find_element(By.TAG_NAME, "form")
                self.driver.execute_script("arguments[0].submit();", form)
            else:
                # Butonu görünür hale getir ve tıkla
                self.human.scroll_to_element(submit_button)
                self.human.random_sleep(1, 2)
                
                try:
                    submit_button.click()
                    logger.info("Devam Et butonuna standart yöntemle tıklandı")
                except Exception as click_error:
                    logger.warning(f"Standart tıklama hatası: {click_error}, JavaScript ile tıklama deniyorum...")
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    logger.info("Devam Et butonuna JavaScript ile tıklandı")
            
            # Tıklama sonrası kısa bir bekleyiş
            self.human.random_sleep(2, 3)
            
            # TC Kimlik No hata kontrolü
            return self.check_tc_kimlik_validation(before_url, before_title, before_form_error, before_page_content)
            
        except Exception as e:
            return self.handle_error("TC Kimlik No girişi sırasında hata oluştu", e, "tc_input_error")
    
    def check_tc_kimlik_validation(self, before_url, before_title, before_form_error, before_page_content):
        """TC Kimlik No doğrulama sonuçlarını kontrol et"""
        try:
            # Sayfa içindeki hata mesajlarını kontrol et
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored")
            if len(error_elements) > before_form_error:
                try:
                    error_message = self.driver.find_element(By.ID, "ikinciAlan-error").text
                    if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_message:
                        logger.warning(f"TC Kimlik No hatası: {error_message}")
                        return {
                            "success": False,
                            "error_type": "invalid_tc_kimlik_format",
                            "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                        }
                except:
                    # ID'ye göre bulunamazsa genel hata mesajını dene
                    error_text = error_elements[0].text
                    if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_text:
                        logger.warning(f"TC Kimlik No hatası: {error_text}")
                        return {
                            "success": False,
                            "error_type": "invalid_tc_kimlik_format",
                            "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                        }
            
            # Sayfa değişikliğini kontrol et
            wait_time = 10
            logger.info(f"Sayfa değişikliği bekleniyor... ({wait_time} saniye)")
            
            for _ in range(wait_time):
                time.sleep(1)
                current_url = self.driver.current_url
                current_title = self.driver.title
                
                # URL veya başlık değişimi oldu mu?
                if current_url != before_url or current_title != before_title:
                    logger.info(f"Sayfa değişikliği tespit edildi! Yeni URL: {current_url}")
                    break
                
                # Her saniye hata kontrolü yap
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored")
                if len(error_elements) > before_form_error:
                    try:
                        error_message = self.driver.find_element(By.ID, "ikinciAlan-error").text
                        if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_message:
                            logger.warning(f"TC Kimlik No hatası: {error_message}")
                            return {
                                "success": False,
                                "error_type": "invalid_tc_kimlik_format",
                                "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                            }
                    except:
                        pass
            
            # Sayfa içeriği değişti mi?
            current_page_content = self.driver.page_source
            if current_page_content != before_page_content:
                logger.info("Sayfa içeriği değişti, işlem devam ediyor...")
                
                # Son bir hata kontrolü daha
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored, div.warningContainer, div.errorContainer")
                if error_elements:
                    error_text = error_elements[0].text
                    if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_text:
                        logger.warning(f"Form hatası: {error_text}")
                        return {
                            "success": False,
                            "error_type": "invalid_tc_kimlik_format",
                            "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                        }
            
            # Başarılı olduğunu varsay
            return {"success": True}
            
        except Exception as e:
            return self.handle_error("TC Kimlik No doğrulama kontrolünde hata oluştu", e, "tc_validation_error")
    
    def accept_terms(self):
        """Onay kutusunu işaretle ve devam et"""
        logger.info("Onay işlemi başlatılıyor...")
        
        try:
            # Sayfanın tamamen yüklenmesini bekle
            self.human.random_sleep(2, 3)
            
            # Sayfayı yukarı kaydır
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.human.random_sleep(1, 2)
            
            # Checkbox'ı bul
            checkbox = self.find_element_with_strategies(
                StrategyFactory.get_strategies_for("checkbox"),
                "Onay kutusu"
            )
            
            if not checkbox:
                return self.handle_error("Onay kutusu bulunamadı", "Element not found", "checkbox_not_found")
            
            # Checkbox'a scroll yap ve tıkla
            self.human.scroll_to_element(checkbox)
            self.human.random_sleep(1, 2)
            
            # JavaScript ile tıkla (daha güvenilir)
            self.driver.execute_script("arguments[0].click();", checkbox)
            logger.info("Onay kutusu işaretlendi")
            
            # Submit butonunu bul
            submit_button = self.find_element_with_strategies(
                StrategyFactory.get_strategies_for("submit_button"),
                "Devam Et butonu"
            )
            
            if not submit_button:
                return self.handle_error("Devam Et butonu bulunamadı", "Element not found", "submit_button_not_found")
            
            # Butona scroll yap ve tıkla
            self.human.scroll_to_element(submit_button)
            self.human.random_sleep(1, 2)
            
            # JavaScript ile tıkla
            self.driver.execute_script("arguments[0].click();", submit_button)
            logger.info("Devam Et butonuna tıklandı")
            
            self.human.random_sleep(2, 4)
            return {"success": True}
            
        except Exception as e:
            return self.handle_error("Onay işlemi sırasında hata oluştu", e, "accept_terms_error")
    
    def is_validation_successful(self):
        """Doğrulama işleminin başarılı olup olmadığını kontrol et"""
        try:
            # URL'yi kontrol et
            current_url = self.driver.current_url
            logger.info(f"Doğrulama sonrası URL: {current_url}")
            
            # Hata sayfasını kontrol et
            if "hata=sayfasi" in current_url:
                error_container = self.find_element_with_strategies(
                    StrategyFactory.get_strategies_for("error_container"),
                    "Hata mesajı",
                    screenshot_on_fail=False
                )
                
                error_message = "Belge doğrulama hatası"
                if error_container:
                    error_message = error_container.text
                
                logger.warning(f"Doğrulama hatası: {error_message}")
                
                # Doğrulama kodu sistem kayıtlarında bulunamadı hatası
                if "Doğrulama kodu sistem kayıtlarında bulunamadı" in error_message:
                    return {
                        "success": False,
                        "error_type": "barcode_not_found",
                        "message": "Doğrulama kodu sistem kayıtlarında bulunamadı. Barkod geçerli fakat sistemde kayıtlı değil."
                    }
                else:
                    return {
                        "success": False,
                        "error_type": "validation_error",
                        "message": error_message
                    }
            
            # Belge gösterme sayfasını kontrol et
            if "belge=goster" in current_url or "belge-dogrulama" in current_url:
                logger.info("Doğrulama başarılı! Sonuç sayfasına ulaşıldı.")
                return {
                    "success": True
                }
            else:
                logger.warning(f"Beklenmedik bir sayfa durumu. URL: {current_url}")
                self.take_screenshot(f"unexpected_state_{int(time.time())}")
                return {
                    "success": False,
                    "error_type": "unexpected_state",
                    "message": f"Beklenmedik bir sayfa durumu. URL: {current_url}"
                }
        except Exception as e:
            return self.handle_error("Doğrulama sonucu kontrolünde hata oluştu", e, "validation_check_error")
    
    def get_download_link(self):
        """Dosya indirme bağlantısını bul"""
        try:
            download_link = self.find_element_with_strategies(
                StrategyFactory.get_strategies_for("download_link"),
                "İndirme bağlantısı"
            )
            
            if not download_link:
                return None, None
                
            download_link_url = download_link.get_attribute("href")
            logger.info(f"Dosya indirme bağlantısı bulundu: {download_link_url}")
            return download_link, download_link_url
        except Exception as e:
            logger.error(f"Dosya indirme bağlantısında hata: {str(e)}")
            return None, None 