"""
Strategy Factory - Infrastructure Layer
Clean Architecture - Element finding strategies for robust web automation
"""
import logging
from typing import List, Dict, Any, Optional

from selenium.webdriver.common.by import By


class ElementStrategy:
    """
    Represents a single element finding strategy.
    
    Encapsulates locator type, value, and wait configurations.
    """
    
    def __init__(
        self, 
        locator_type: By, 
        value: str, 
        wait_time: int = 5,
        wait_for_clickable: bool = False,
        description: Optional[str] = None
    ):
        """
        Initialize element strategy.
        
        Args:
            locator_type: Selenium By locator type
            value: Locator value/selector
            wait_time: Maximum wait time in seconds
            wait_for_clickable: Whether to wait for clickable state
            description: Human readable description
        """
        self.locator_type = locator_type
        self.value = value
        self.wait_time = wait_time
        self.wait_for_clickable = wait_for_clickable
        self.description = description or f"{locator_type} = {value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert strategy to dictionary format."""
        return {
            "type": self.locator_type,
            "value": self.value,
            "wait_time": self.wait_time,
            "wait_for_clickable": self.wait_for_clickable,
            "description": self.description
        }


class StrategyFactory:
    """
    Factory for creating element finding strategies.
    
    Single Responsibility: Only creates element location strategies
    Open/Closed: Easy to extend with new strategy types
    """
    
    def __init__(self):
        """Initialize strategy factory."""
        self.logger = logging.getLogger(__name__)
    
    def get_strategies_for(self, element_type: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get ordered list of strategies for element type.
        
        Args:
            element_type: Type of element to find
            context: Additional context for strategy selection
            
        Returns:
            List of strategy dictionaries ordered by reliability
        """
        self.logger.debug(f"🎯 Creating strategies for '{element_type}' (context: {context})")
        
        # Strategy dispatch based on element type
        strategy_methods = {
            "barcode_input": self._get_barcode_input_strategies,
            "tc_kimlik_input": self._get_tc_kimlik_input_strategies,
            "submit_button": self._get_submit_button_strategies,
            "checkbox": self._get_checkbox_strategies,
            "error_container": self._get_error_container_strategies,
            "download_link": self._get_download_link_strategies,
            "verification_result": self._get_verification_result_strategies,
            "form": self._get_form_strategies
        }
        
        strategy_method = strategy_methods.get(element_type)
        if not strategy_method:
            self.logger.warning(f"⚠️ Unknown element type: {element_type}")
            return []
        
        strategies = strategy_method(context)
        strategy_dicts = [s.to_dict() for s in strategies]
        
        self.logger.debug(f"✅ Created {len(strategy_dicts)} strategies for {element_type}")
        return strategy_dicts
    
    def _get_barcode_input_strategies(self, context: Optional[str] = None) -> List[ElementStrategy]:
        """Get strategies for barcode input field."""
        return [
            ElementStrategy(
                By.ID, "sorgulananBarkod", 
                wait_time=10,
                description="Primary barcode input by ID"
            ),
            ElementStrategy(
                By.NAME, "sorgulananBarkod",
                wait_time=5,
                description="Barcode input by name attribute"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[type='text'][name='sorgulananBarkod']",
                wait_time=5,
                description="Barcode input by CSS selector"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[type='text']:first-of-type",
                wait_time=3,
                description="First text input fallback"
            )
        ]
    
    def _get_tc_kimlik_input_strategies(self, context: Optional[str] = None) -> List[ElementStrategy]:
        """Get strategies for TC Kimlik No input field."""
        return [
            ElementStrategy(
                By.ID, "tckn",
                wait_time=5,
                description="TC Kimlik by tckn ID"
            ),
            ElementStrategy(
                By.ID, "ikinciAlan",
                wait_time=5,
                description="TC Kimlik by ikinciAlan ID"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[name='tckn']",
                wait_time=5,
                description="TC Kimlik by name attribute"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[name*='kimlik']",
                wait_time=5,
                description="TC Kimlik by partial name match"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[id*='kimlik']",
                wait_time=5,
                description="TC Kimlik by partial ID match"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[placeholder*='Kimlik']",
                wait_time=5,
                description="TC Kimlik by placeholder text"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input.text:not(#sorgulananBarkod)",
                wait_time=3,
                description="Text input excluding barcode field"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[type='text']:not(#sorgulananBarkod):nth-of-type(2)",
                wait_time=3,
                description="Second text input field"
            )
        ]
    
    def _get_submit_button_strategies(self, context: Optional[str] = None) -> List[ElementStrategy]:
        """Get strategies for submit button."""
        return [
            ElementStrategy(
                By.CSS_SELECTOR, "input.submitButton",
                wait_time=10,
                wait_for_clickable=True,
                description="Primary submit button by class"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input.submitButton[value='Devam Et']",
                wait_time=5,
                wait_for_clickable=True,
                description="Submit button with 'Devam Et' value"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[type='submit'][value='Devam Et']",
                wait_time=5,
                wait_for_clickable=True,
                description="Submit input with 'Devam Et' value"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[type='submit']",
                wait_time=5,
                wait_for_clickable=True,
                description="Any submit input"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "button[type='submit']",
                wait_time=3,
                wait_for_clickable=True,
                description="Submit button element"
            ),
            ElementStrategy(
                By.XPATH, "//input[@value='Devam Et' or @value='Doğrula' or @value='Gönder']",
                wait_time=3,
                wait_for_clickable=True,
                description="Submit button by value text"
            )
        ]
    
    def _get_checkbox_strategies(self, context: Optional[str] = None) -> List[ElementStrategy]:
        """Get strategies for checkbox elements."""
        return [
            ElementStrategy(
                By.ID, "chkOnay",
                wait_time=10,
                description="Primary approval checkbox"
            ),
            ElementStrategy(
                By.NAME, "chkOnay",
                wait_time=5,
                description="Approval checkbox by name"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[type='checkbox'][id*='onay']",
                wait_time=5,
                description="Checkbox with 'onay' in ID"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "input[type='checkbox']",
                wait_time=3,
                description="Any checkbox"
            ),
            ElementStrategy(
                By.XPATH, "//input[@type='checkbox' and contains(@id, 'onay')]",
                wait_time=3,
                description="Checkbox containing 'onay' in ID"
            )
        ]
    
    def _get_error_container_strategies(self, context: Optional[str] = None) -> List[ElementStrategy]:
        """Get strategies for error message containers."""
        return [
            ElementStrategy(
                By.CSS_SELECTOR, "div.warningContainer",
                wait_time=3,
                description="Warning container"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "div.errorContainer",
                wait_time=3,
                description="Error container"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "div.formRow.required.errored",
                wait_time=3,
                description="Form row with error"
            ),
            ElementStrategy(
                By.ID, "ikinciAlan-error",
                wait_time=2,
                description="Second field error message"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, ".error, .warning, .alert",
                wait_time=2,
                description="Generic error/warning classes"
            ),
            ElementStrategy(
                By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'warning')]",
                wait_time=2,
                description="Elements with error/warning in class"
            )
        ]
    
    def _get_download_link_strategies(self, context: Optional[str] = None) -> List[ElementStrategy]:
        """Get strategies for download links."""
        return [
            ElementStrategy(
                By.CSS_SELECTOR, "a.download",
                wait_time=5,
                description="Download link by class"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "a[href*='download']",
                wait_time=3,
                description="Link with 'download' in href"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "a[href$='.pdf']",
                wait_time=3,
                description="PDF file link"
            ),
            ElementStrategy(
                By.XPATH, "//a[contains(@href,'download') or contains(text(),'İndir') or contains(text(),'Download')]",
                wait_time=3,
                description="Download link by href or text"
            ),
            ElementStrategy(
                By.XPATH, "//a[contains(@href,'.pdf') or contains(@href,'.doc')]",
                wait_time=2,
                description="Document file links"
            )
        ]
    
    def _get_verification_result_strategies(self, context: Optional[str] = None) -> List[ElementStrategy]:
        """Get strategies for verification result indicators."""
        return [
            ElementStrategy(
                By.CSS_SELECTOR, ".result, .verification-result",
                wait_time=5,
                description="Result container by class"
            ),
            ElementStrategy(
                By.XPATH, "//*[contains(text(), 'doğrulandı') or contains(text(), 'geçerli')]",
                wait_time=3,
                description="Success indicators by text"
            ),
            ElementStrategy(
                By.XPATH, "//*[contains(text(), 'bulunamadı') or contains(text(), 'hata')]",
                wait_time=3,
                description="Error indicators by text"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, ".success, .valid, .verified",
                wait_time=2,
                description="Success classes"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, ".error, .invalid, .failed",
                wait_time=2,
                description="Error classes"
            )
        ]
    
    def _get_form_strategies(self, context: Optional[str] = None) -> List[ElementStrategy]:
        """Get strategies for form elements."""
        return [
            ElementStrategy(
                By.TAG_NAME, "form",
                wait_time=5,
                description="Main form element"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "form[method='post']",
                wait_time=3,
                description="POST form"
            ),
            ElementStrategy(
                By.ID, "mainForm",
                wait_time=3,
                description="Main form by ID"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "div.form-container",
                wait_time=2,
                description="Form container"
            )
        ]
    
    def create_custom_strategy(
        self, 
        locator_type: By, 
        value: str, 
        wait_time: int = 5,
        wait_for_clickable: bool = False,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a custom element strategy.
        
        Args:
            locator_type: Selenium By locator type
            value: Locator value
            wait_time: Wait timeout
            wait_for_clickable: Whether to wait for clickable
            description: Strategy description
            
        Returns:
            Strategy dictionary
        """
        strategy = ElementStrategy(
            locator_type, value, wait_time, wait_for_clickable, description
        )
        return strategy.to_dict()
    
    def get_fallback_strategies(self, element_type: str) -> List[Dict[str, Any]]:
        """
        Get fallback strategies when primary strategies fail.
        
        Args:
            element_type: Element type
            
        Returns:
            List of fallback strategies
        """
        fallback_strategies = [
            ElementStrategy(
                By.XPATH, "//*",
                wait_time=1,
                description="Universal XPath fallback"
            ),
            ElementStrategy(
                By.CSS_SELECTOR, "*",
                wait_time=1,
                description="Universal CSS fallback"
            )
        ]
        
        return [s.to_dict() for s in fallback_strategies] 