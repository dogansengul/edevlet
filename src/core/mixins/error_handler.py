import logging
import time

logger = logging.getLogger("ErrorHandler")

class ErrorHandlerMixin:
    """Hata yönetimi için yardımcı sınıf"""
    
    def handle_error(self, context, error, error_type="unknown_error", take_screenshot=True):
        """Hata durumlarını merkezi olarak yönetme"""
        logger.error(f"{context}: {str(error)}")
        
        if take_screenshot:
            screenshot_path = self.take_screenshot(f"{error_type}_{int(time.time())}")
        
        return {
            "success": False,
            "error_type": error_type,
            "message": f"{context}: {str(error)}",
            "screenshot": screenshot_path if take_screenshot else None
        } 