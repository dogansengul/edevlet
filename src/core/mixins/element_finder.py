from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

logger = logging.getLogger("ElementFinder")

class ElementFinderMixin:
    """Web element bulma işlemlerini kolaylaştırmak için yardımcı sınıf"""
    
    def find_element_with_strategies(self, strategies, context_message="", screenshot_on_fail=True):
        """Birden fazla stratejiyi deneyerek element bulma"""
        for strategy in strategies:
            try:
                selector_type = strategy.get("type")
                selector_value = strategy.get("value", "")
                wait_time = strategy.get("wait_time", 5)
                
                logger.debug(f"Arama stratejisi deneniyor: {selector_type} - '{selector_value}'")
                
                if strategy.get("wait_for_clickable", False):
                    element = WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                else:
                    element = WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                
                logger.info(f"Element bulundu: {selector_type} - '{selector_value}'")
                return element
            except Exception as e:
                logger.debug(f"Element bulunamadı ({selector_type} - '{selector_value}'): {str(e)}")
        
        if screenshot_on_fail:
            self.take_screenshot(f"element_not_found_{int(time.time())}")
        
        error_msg = f"Element bulunamadı: {context_message}"
        logger.error(error_msg)
        return None
    
    def take_screenshot(self, name_prefix):
        """Ekran görüntüsü alma işlemi"""
        try:
            screenshot_path = f"src/screenshots/{name_prefix}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Ekran görüntüsü kaydedildi: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Ekran görüntüsü alınamadı: {str(e)}")
            return None 