from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import logging
from ..config.config import config

# Get logger
logger = logging.getLogger("HumanBehaviorSimulator")

class HumanBehaviorSimulator:
    def __init__(self, driver):
        self.driver = driver
        self.actions = ActionChains(driver)
        self.wait = WebDriverWait(driver, 10)
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        logger.info("HumanBehaviorSimulator başlatıldı")
    
    def random_sleep(self, min_time=None, max_time=None):
        """Rastgele bir süre bekle"""
        min_time = min_time or config.WAIT_TIMES["min"]
        max_time = max_time or config.WAIT_TIMES["max"]
        sleep_time = random.uniform(min_time, max_time)
        logger.debug(f"Bekleniyor: {sleep_time:.2f} saniye")
        time.sleep(sleep_time)
    
    def scroll_to_element(self, element):
        """Elemente scroll yap"""
        try:
            # JavaScript ile elemente scroll yap
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
            logger.debug("Elemente scroll yapıldı")
            self.random_sleep(0.5, 1.0)
            return True
        except Exception as e:
            logger.error(f"Elemente scroll yapılırken hata: {str(e)}")
            return False
    
    def ensure_element_visible(self, element):
        """Elementin görünür olduğundan emin ol"""
        try:
            # Elementin görünür olup olmadığını kontrol et
            if not element.is_displayed():
                # Görünür değilse scroll yap
                logger.debug("Element görünür değil, scroll yapılıyor")
                self.scroll_to_element(element)
                self.random_sleep(0.5, 1.0)
                
                # Tekrar kontrol et
                if not element.is_displayed():
                    logger.warning("Element hala görünür değil, direkt JavaScript ile tıklamayı dene")
                    return False
            return True
        except Exception as e:
            logger.error(f"Element görünürlük kontrolünde hata: {str(e)}")
            return False
    
    def human_like_click(self, element):
        """İnsan benzeri tıklama hareketi"""
        try:
            # Önce elementin görünür olduğundan emin ol
            if not self.ensure_element_visible(element):
                # Görünür değilse JavaScript ile tıkla
                logger.debug("Element görünür değil, JavaScript ile tıklanıyor")
                self.driver.execute_script("arguments[0].click();", element)
                self.random_sleep(0.1, 0.3)
                return
            
            # ActionChains ile tıkla
            self.actions = ActionChains(self.driver)  # Yeni bir ActionChains oluştur
            self.actions.move_to_element(element)
            self.random_sleep(0.1, 0.3)
            self.actions.click()
            self.actions.perform()
            logger.debug("Element insan benzeri davranışla tıklandı")
        except Exception as e:
            logger.error(f"İnsan benzeri tıklama sırasında hata: {str(e)}")
            # Hata durumunda JavaScript ile tıkla
            try:
                logger.debug("Alternatif olarak JavaScript ile tıklanıyor")
                self.driver.execute_script("arguments[0].click();", element)
            except Exception as js_error:
                logger.error(f"JavaScript ile tıklama sırasında hata: {str(js_error)}")
    
    def human_like_type(self, element, text):
        """İnsan benzeri yazma hareketi"""
        try:
            # Önce elementin görünür olduğundan emin ol
            if not self.ensure_element_visible(element):
                # Görünür değilse JavaScript ile değer ata
                logger.debug("Element görünür değil, JavaScript ile değer atanıyor")
                self.driver.execute_script(f"arguments[0].value = '{text}';", element)
                self.random_sleep(0.1, 0.3)
                return
            
            # Elemente tıkla
            self.actions = ActionChains(self.driver)  # Yeni bir ActionChains oluştur
            self.actions.move_to_element(element)
            self.random_sleep(0.1, 0.3)
            self.actions.click()
            self.actions.perform()
            
            # Metni temizle
            element.clear()
            
            # Karakterleri tek tek yaz
            logger.debug(f"İnsan benzeri yazma başlıyor: {len(text)} karakter")
            for char in text:
                element.send_keys(char)
                self.random_sleep(0.05, 0.15)
            logger.debug("İnsan benzeri yazma tamamlandı")
        except Exception as e:
            logger.error(f"İnsan benzeri yazma sırasında hata: {str(e)}")
            # Hata durumunda JavaScript ile değer ata
            try:
                logger.debug("Alternatif olarak JavaScript ile değer atanıyor")
                self.driver.execute_script(f"arguments[0].value = '{text}';", element)
            except Exception as js_error:
                logger.error(f"JavaScript ile değer atama sırasında hata: {str(js_error)}")
    
    def random_scroll(self, scroll_amount=None):
        """Rastgele scroll hareketi"""
        if scroll_amount is None:
            scroll_amount = random.randint(100, 500)
        
        try:
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            logger.debug(f"Rastgele scroll yapıldı: {scroll_amount}px")
            self.random_sleep(0.2, 0.5)
        except Exception as e:
            logger.error(f"Rastgele scroll sırasında hata: {str(e)}")
    
    def move_mouse_randomly(self):
        """Fareyi rastgele hareket ettir"""
        try:
            viewport_width = self.driver.execute_script("return window.innerWidth;")
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            
            # Mevcut fare konumundan göreceli hareket
            max_move = 200  # Maksimum hareket mesafesi
            x_offset = random.randint(-max_move, max_move)
            y_offset = random.randint(-max_move, max_move)
            
            # Yeni konumun viewport sınırları içinde kalmasını sağla
            new_x = max(0, min(viewport_width - 10, self.last_mouse_x + x_offset))
            new_y = max(0, min(viewport_height - 10, self.last_mouse_y + y_offset))
            
            # Göreceli hareketi hesapla
            x_move = new_x - self.last_mouse_x
            y_move = new_y - self.last_mouse_y
            
            # Fareyi hareket ettir
            try:
                self.actions = ActionChains(self.driver)  # Yeni bir ActionChains oluştur
                self.actions.move_by_offset(x_move, y_move)
                self.actions.perform()
                
                # Son konumu güncelle
                self.last_mouse_x = new_x
                self.last_mouse_y = new_y
                logger.debug(f"Fare rastgele hareket ettirildi: ({x_move}, {y_move})")
            except:
                # Hareket başarısız olursa fareyi merkeze al
                logger.debug("Fare hareketi başarısız, fareyi merkeze alıyorum")
                self.actions = ActionChains(self.driver)
                self.actions.move_to_element(self.driver.find_element(By.TAG_NAME, "body"))
                self.actions.perform()
                self.last_mouse_x = viewport_width // 2
                self.last_mouse_y = viewport_height // 2
            
            self.random_sleep(0.1, 0.3)
        except Exception as e:
            logger.error(f"Fare hareketi sırasında hata: {str(e)}")
            # Hata durumunda fareyi sıfırla
            self.last_mouse_x = 0
            self.last_mouse_y = 0
    
    def simulate_human_behavior(self):
        """Genel insan benzeri davranışları simüle et"""
        try:
            logger.debug("İnsan davranışı simülasyonu başlatılıyor")
            # Rastgele mouse hareketi
            self.move_mouse_randomly()
            
            # Rastgele scroll
            self.random_scroll()
            
            # Kısa bir bekleme
            self.random_sleep()
            logger.debug("İnsan davranışı simülasyonu tamamlandı")
        except Exception as e:
            logger.error(f"İnsan davranışı simülasyonu sırasında hata: {str(e)}")
    
    def wait_for_element(self, by, value, timeout=10):
        """Element yüklenene kadar bekle ve insan benzeri davranış sergile"""
        try:
            logger.debug(f"Element bekleniyor: {by} - {value}, timeout: {timeout}s")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            # Elemente scroll yap
            self.scroll_to_element(element)
            self.simulate_human_behavior()
            logger.debug(f"Element bulundu ve insan davranışı simüle edildi: {by} - {value}")
            return element
        except Exception as e:
            logger.error(f"Element bekleme sırasında hata: {str(e)}")
            raise
    
    def wait_for_clickable(self, by, value, timeout=10):
        """Element tıklanabilir olana kadar bekle ve insan benzeri davranış sergile"""
        try:
            logger.debug(f"Tıklanabilir element bekleniyor: {by} - {value}, timeout: {timeout}s")
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            # Elemente scroll yap
            self.scroll_to_element(element)
            self.simulate_human_behavior()
            logger.debug(f"Tıklanabilir element bulundu ve insan davranışı simüle edildi: {by} - {value}")
            return element
        except Exception as e:
            logger.error(f"Tıklanabilir element bekleme sırasında hata: {str(e)}")
            raise 