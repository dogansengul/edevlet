from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import config

class HumanBehaviorSimulator:
    def __init__(self, driver):
        self.driver = driver
        self.actions = ActionChains(driver)
        self.wait = WebDriverWait(driver, 10)
    
    def random_sleep(self, min_time=None, max_time=None):
        """Rastgele bir süre bekle"""
        min_time = min_time or config.WAIT_TIMES["min"]
        max_time = max_time or config.WAIT_TIMES["max"]
        time.sleep(random.uniform(min_time, max_time))
    
    def scroll_to_element(self, element):
        """Elemente scroll yap"""
        try:
            # JavaScript ile elemente scroll yap
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
            self.random_sleep(0.5, 1.0)
            return True
        except Exception as e:
            print(f"Elemente scroll yapılırken hata: {str(e)}")
            return False
    
    def ensure_element_visible(self, element):
        """Elementin görünür olduğundan emin ol"""
        try:
            # Elementin görünür olup olmadığını kontrol et
            if not element.is_displayed():
                # Görünür değilse scroll yap
                self.scroll_to_element(element)
                self.random_sleep(0.5, 1.0)
                
                # Tekrar kontrol et
                if not element.is_displayed():
                    print("Element hala görünür değil, direkt JavaScript ile tıklamayı dene")
                    return False
            return True
        except Exception as e:
            print(f"Element görünürlük kontrolünde hata: {str(e)}")
            return False
    
    def human_like_click(self, element):
        """İnsan benzeri tıklama hareketi"""
        try:
            # Önce elementin görünür olduğundan emin ol
            if not self.ensure_element_visible(element):
                # Görünür değilse JavaScript ile tıkla
                self.driver.execute_script("arguments[0].click();", element)
                self.random_sleep(0.1, 0.3)
                return
            
            # ActionChains ile tıkla
            self.actions = ActionChains(self.driver)  # Yeni bir ActionChains oluştur
            self.actions.move_to_element(element)
            self.random_sleep(0.1, 0.3)
            self.actions.click()
            self.actions.perform()
        except Exception as e:
            print(f"İnsan benzeri tıklama sırasında hata: {str(e)}")
            # Hata durumunda JavaScript ile tıkla
            try:
                self.driver.execute_script("arguments[0].click();", element)
            except Exception as js_error:
                print(f"JavaScript ile tıklama sırasında hata: {str(js_error)}")
    
    def human_like_type(self, element, text):
        """İnsan benzeri yazma hareketi"""
        try:
            # Önce elementin görünür olduğundan emin ol
            if not self.ensure_element_visible(element):
                # Görünür değilse JavaScript ile değer ata
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
            for char in text:
                element.send_keys(char)
                self.random_sleep(0.05, 0.15)
        except Exception as e:
            print(f"İnsan benzeri yazma sırasında hata: {str(e)}")
            # Hata durumunda JavaScript ile değer ata
            try:
                self.driver.execute_script(f"arguments[0].value = '{text}';", element)
            except Exception as js_error:
                print(f"JavaScript ile değer atama sırasında hata: {str(js_error)}")
    
    def random_scroll(self, scroll_amount=None):
        """Rastgele scroll hareketi"""
        if scroll_amount is None:
            scroll_amount = random.randint(100, 500)
        
        try:
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self.random_sleep(0.2, 0.5)
        except Exception as e:
            print(f"Rastgele scroll sırasında hata: {str(e)}")
    
    def move_mouse_randomly(self):
        """Fareyi rastgele hareket ettir"""
        try:
            viewport_width = self.driver.execute_script("return window.innerWidth;")
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            
            x = random.randint(0, viewport_width - 100)  # Sınırları aşmamak için marj bırak
            y = random.randint(0, viewport_height - 100)  # Sınırları aşmamak için marj bırak
            
            self.actions = ActionChains(self.driver)  # Yeni bir ActionChains oluştur
            self.actions.move_by_offset(x, y)
            self.actions.perform()
            self.random_sleep(0.1, 0.3)
        except Exception as e:
            print(f"Fare hareketi sırasında hata: {str(e)}")
    
    def simulate_human_behavior(self):
        """Genel insan benzeri davranışları simüle et"""
        try:
            # Rastgele mouse hareketi
            self.move_mouse_randomly()
            
            # Rastgele scroll
            self.random_scroll()
            
            # Kısa bir bekleme
            self.random_sleep()
        except Exception as e:
            print(f"İnsan davranışı simülasyonu sırasında hata: {str(e)}")
    
    def wait_for_element(self, by, value, timeout=10):
        """Element yüklenene kadar bekle ve insan benzeri davranış sergile"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            # Elemente scroll yap
            self.scroll_to_element(element)
            self.simulate_human_behavior()
            return element
        except Exception as e:
            print(f"Element bekleme sırasında hata: {str(e)}")
            raise
    
    def wait_for_clickable(self, by, value, timeout=10):
        """Element tıklanabilir olana kadar bekle ve insan benzeri davranış sergile"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            # Elemente scroll yap
            self.scroll_to_element(element)
            self.simulate_human_behavior()
            return element
        except Exception as e:
            print(f"Tıklanabilir element bekleme sırasında hata: {str(e)}")
            raise 