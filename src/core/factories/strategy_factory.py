from selenium.webdriver.common.by import By
import logging

logger = logging.getLogger("StrategyFactory")

class StrategyFactory:
    """Element bulma stratejilerini üreten fabrika sınıfı"""
    
    @staticmethod
    def get_strategies_for(element_type, context=None):
        """Element tipine göre strateji üret"""
        logger.debug(f"'{element_type}' için stratejiler oluşturuluyor. Context: {context}")
        
        # Barkod input stratejileri
        if element_type == "barcode_input":
            return [
                {"type": By.ID, "value": "sorgulananBarkod", "wait_time": 10},
                {"type": By.NAME, "value": "sorgulananBarkod", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[type='text']", "wait_time": 5}
            ]
        
        # TC Kimlik No input stratejileri
        elif element_type == "tc_kimlik_input":
            return [
                {"type": By.ID, "value": "tckn", "wait_time": 5},
                {"type": By.ID, "value": "ikinciAlan", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[name='tckn']", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[name*='kimlik']", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[id*='kimlik']", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[placeholder*='Kimlik']", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input.text:not(#sorgulananBarkod)", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[type='text']:not(#sorgulananBarkod)", "wait_time": 5}
            ]
        
        # Submit butonu stratejileri
        elif element_type == "submit_button":
            return [
                {"type": By.CSS_SELECTOR, "value": "input.submitButton", "wait_for_clickable": True, "wait_time": 10},
                {"type": By.CSS_SELECTOR, "value": "input.submitButton[value='Devam Et']", "wait_for_clickable": True, "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[type='submit'][value='Devam Et']", "wait_for_clickable": True, "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[type='submit']", "wait_for_clickable": True, "wait_time": 5}
            ]
        
        # Onay kutusu stratejileri
        elif element_type == "checkbox":
            return [
                {"type": By.ID, "value": "chkOnay", "wait_time": 10},
                {"type": By.NAME, "value": "chkOnay", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "input[type='checkbox']", "wait_time": 5}
            ]
        
        # Hata mesajı stratejileri
        elif element_type == "error_container":
            return [
                {"type": By.CSS_SELECTOR, "value": "div.warningContainer", "wait_time": 3},
                {"type": By.CSS_SELECTOR, "value": "div.errorContainer", "wait_time": 3}
            ]
        
        # İndirme bağlantısı stratejileri
        elif element_type == "download_link":
            return [
                {"type": By.CSS_SELECTOR, "value": "a.download", "wait_time": 5},
                {"type": By.CSS_SELECTOR, "value": "a[href*='download']", "wait_time": 3},
                {"type": By.XPATH, "value": "//a[contains(@href,'download') or contains(text(),'İndir')]", "wait_time": 3}
            ]
        
        # Bilinmeyen element tipi için varsayılan strateji
        else:
            logger.warning(f"Bilinmeyen element tipi: {element_type}")
            return [] 