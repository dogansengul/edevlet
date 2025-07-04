"""
Element Finder - Infrastructure Layer
Clean Architecture - Robust element finding utilities for web automation
"""
import logging
import time
from typing import Optional, List, Dict, Any, Union

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .strategy_factory import StrategyFactory


class ElementFinder:
    """
    Robust element finder with multiple strategy support.
    
    Single Responsibility: Only handles element finding logic
    Uses Strategy pattern for different element location approaches
    """
    
    def __init__(self, driver: Chrome, strategy_factory: Optional[StrategyFactory] = None):
        """
        Initialize element finder.
        
        Args:
            driver: Chrome WebDriver instance
            strategy_factory: Factory for element strategies
        """
        self.driver = driver
        self.strategy_factory = strategy_factory or StrategyFactory()
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🔍 ElementFinder initialized")
    
    def find_element_with_strategies(
        self, 
        strategies: List[Dict[str, Any]], 
        context_message: str = "",
        screenshot_on_fail: bool = True,
        raise_on_fail: bool = False
    ) -> Optional[object]:
        """
        Find element using multiple strategies in order.
        
        Args:
            strategies: List of strategy dictionaries
            context_message: Context for logging
            screenshot_on_fail: Whether to take screenshot on failure
            raise_on_fail: Whether to raise exception on failure
            
        Returns:
            WebElement if found, None otherwise
            
        Raises:
            TimeoutException: If raise_on_fail=True and element not found
        """
        self.logger.debug(f"🎯 Searching for element: {context_message}")
        self.logger.debug(f"📋 Trying {len(strategies)} strategies")
        
        for i, strategy in enumerate(strategies, 1):
            try:
                selector_type = strategy.get("type")
                selector_value = strategy.get("value", "")
                wait_time = strategy.get("wait_time", 5)
                wait_for_clickable = strategy.get("wait_for_clickable", False)
                description = strategy.get("description", f"Strategy {i}")
                
                self.logger.debug(f"🔍 Strategy {i}/{len(strategies)}: {description}")
                self.logger.debug(f"   Locator: {selector_type} = '{selector_value}'")
                self.logger.debug(f"   Wait: {wait_time}s, Clickable: {wait_for_clickable}")
                
                # Choose appropriate wait condition
                if wait_for_clickable:
                    element = WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    self.logger.debug(f"   ✅ Found clickable element")
                else:
                    element = WebDriverWait(self.driver, wait_time).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    self.logger.debug(f"   ✅ Found element")
                
                self.logger.info(f"🎯 Element found using strategy {i}: {description}")
                return element
                
            except TimeoutException:
                self.logger.debug(f"   ⏰ Strategy {i} timeout after {wait_time}s")
            except Exception as e:
                self.logger.debug(f"   💥 Strategy {i} error: {str(e)}")
        
        # All strategies failed
        error_msg = f"Element not found after {len(strategies)} strategies: {context_message}"
        self.logger.error(error_msg)
        
        if screenshot_on_fail:
            self._take_screenshot(f"element_not_found_{int(time.time())}")
        
        if raise_on_fail:
            raise TimeoutException(error_msg)
        
        return None
    
    def find_element_by_type(
        self, 
        element_type: str, 
        context: Optional[str] = None,
        screenshot_on_fail: bool = True,
        raise_on_fail: bool = False
    ) -> Optional[object]:
        """
        Find element by predefined type using factory strategies.
        
        Args:
            element_type: Type of element (e.g., 'barcode_input', 'submit_button')
            context: Additional context for strategy selection
            screenshot_on_fail: Whether to take screenshot on failure
            raise_on_fail: Whether to raise exception on failure
            
        Returns:
            WebElement if found, None otherwise
        """
        strategies = self.strategy_factory.get_strategies_for(element_type, context)
        
        if not strategies:
            self.logger.warning(f"⚠️ No strategies available for element type: {element_type}")
            return None
        
        return self.find_element_with_strategies(
            strategies,
            context_message=f"{element_type} ({context or 'no context'})",
            screenshot_on_fail=screenshot_on_fail,
            raise_on_fail=raise_on_fail
        )
    
    def find_elements_with_strategies(
        self, 
        strategies: List[Dict[str, Any]], 
        context_message: str = ""
    ) -> List[object]:
        """
        Find multiple elements using strategies.
        
        Args:
            strategies: List of strategy dictionaries
            context_message: Context for logging
            
        Returns:
            List of WebElements (empty if none found)
        """
        self.logger.debug(f"🔍 Searching for multiple elements: {context_message}")
        
        for i, strategy in enumerate(strategies, 1):
            try:
                selector_type = strategy.get("type")
                selector_value = strategy.get("value", "")
                wait_time = strategy.get("wait_time", 5)
                description = strategy.get("description", f"Strategy {i}")
                
                self.logger.debug(f"🔍 Strategy {i}: {description}")
                
                # Wait for at least one element to be present
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                
                # Find all matching elements
                elements = self.driver.find_elements(selector_type, selector_value)
                
                if elements:
                    self.logger.info(f"🎯 Found {len(elements)} elements using strategy {i}: {description}")
                    return elements
                    
            except TimeoutException:
                self.logger.debug(f"   ⏰ Strategy {i} timeout")
            except Exception as e:
                self.logger.debug(f"   💥 Strategy {i} error: {str(e)}")
        
        self.logger.warning(f"⚠️ No elements found: {context_message}")
        return []
    
    def wait_for_element_to_disappear(
        self, 
        by: By, 
        value: str, 
        timeout: int = 10
    ) -> bool:
        """
        Wait for element to disappear from DOM.
        
        Args:
            by: Locator type
            value: Locator value
            timeout: Maximum wait time
            
        Returns:
            True if element disappeared, False if still present
        """
        try:
            self.logger.debug(f"⏳ Waiting for element to disappear: {by} = {value}")
            
            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located((by, value))
            )
            
            self.logger.debug(f"✅ Element disappeared: {by} = {value}")
            return True
            
        except TimeoutException:
            self.logger.debug(f"⏰ Element still present after {timeout}s: {by} = {value}")
            return False
    
    def wait_for_text_to_appear(
        self, 
        by: By, 
        value: str, 
        expected_text: str, 
        timeout: int = 10
    ) -> bool:
        """
        Wait for specific text to appear in element.
        
        Args:
            by: Locator type
            value: Locator value
            expected_text: Text to wait for
            timeout: Maximum wait time
            
        Returns:
            True if text appeared, False otherwise
        """
        try:
            self.logger.debug(f"⏳ Waiting for text '{expected_text}' in: {by} = {value}")
            
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element((by, value), expected_text)
            )
            
            self.logger.debug(f"✅ Text appeared: '{expected_text}'")
            return True
            
        except TimeoutException:
            self.logger.debug(f"⏰ Text not found after {timeout}s: '{expected_text}'")
            return False
    
    def wait_for_url_change(
        self, 
        current_url: str, 
        timeout: int = 10
    ) -> str:
        """
        Wait for URL to change from current value.
        
        Args:
            current_url: Current URL to wait to change from
            timeout: Maximum wait time
            
        Returns:
            New URL or current URL if no change
        """
        try:
            self.logger.debug(f"⏳ Waiting for URL change from: {current_url}")
            
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.current_url != current_url
            )
            
            new_url = self.driver.current_url
            self.logger.debug(f"✅ URL changed to: {new_url}")
            return new_url
            
        except TimeoutException:
            self.logger.debug(f"⏰ URL did not change after {timeout}s")
            return self.driver.current_url
    
    def is_element_visible(self, element) -> bool:
        """
        Check if element is visible and interactable.
        
        Args:
            element: WebElement to check
            
        Returns:
            True if element is visible
        """
        try:
            return element.is_displayed() and element.is_enabled()
        except Exception as e:
            self.logger.debug(f"💥 Visibility check error: {str(e)}")
            return False
    
    def get_element_text_safe(self, element) -> str:
        """
        Safely get text from element.
        
        Args:
            element: WebElement
            
        Returns:
            Element text or empty string
        """
        try:
            return element.text.strip()
        except Exception as e:
            self.logger.debug(f"💥 Text extraction error: {str(e)}")
            return ""
    
    def get_element_attribute_safe(self, element, attribute: str) -> str:
        """
        Safely get attribute from element.
        
        Args:
            element: WebElement
            attribute: Attribute name
            
        Returns:
            Attribute value or empty string
        """
        try:
            value = element.get_attribute(attribute)
            return value if value is not None else ""
        except Exception as e:
            self.logger.debug(f"💥 Attribute extraction error: {str(e)}")
            return ""
    
    def find_element_containing_text(
        self, 
        text: str, 
        tag: str = "*", 
        timeout: int = 5
    ) -> Optional[object]:
        """
        Find element containing specific text.
        
        Args:
            text: Text to search for
            tag: HTML tag to search in (default: any)
            timeout: Maximum wait time
            
        Returns:
            WebElement containing text or None
        """
        try:
            xpath = f"//{tag}[contains(text(), '{text}')]"
            self.logger.debug(f"🔍 Searching for text: '{text}' in {tag} tags")
            
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            
            self.logger.debug(f"✅ Found element containing: '{text}'")
            return element
            
        except TimeoutException:
            self.logger.debug(f"⏰ No element found containing: '{text}'")
            return None
    
    def _take_screenshot(self, filename: str) -> None:
        """
        Take screenshot for debugging.
        
        Args:
            filename: Screenshot filename
        """
        try:
            screenshot_path = f"screenshots/{filename}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.debug(f"📸 Screenshot saved: {screenshot_path}")
        except Exception as e:
            self.logger.error(f"💥 Screenshot error: {str(e)}")
    
    def debug_page_info(self) -> Dict[str, Any]:
        """
        Get debugging information about current page.
        
        Returns:
            Dictionary with page information
        """
        try:
            info = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "page_source_length": len(self.driver.page_source),
                "window_size": self.driver.get_window_size(),
                "cookies_count": len(self.driver.get_cookies())
            }
            
            self.logger.debug(f"📊 Page info: {info}")
            return info
            
        except Exception as e:
            self.logger.error(f"💥 Page info error: {str(e)}")
            return {"error": str(e)} 