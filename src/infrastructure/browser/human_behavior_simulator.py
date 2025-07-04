"""
Human Behavior Simulator - Infrastructure Layer
Clean Architecture - Advanced human-like browser interactions for anti-detection
"""
import logging
import random
import time
from typing import Optional

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome


class HumanBehaviorSimulator:
    """
    Simulates human-like browser interactions to avoid detection.
    
    Single Responsibility: Only handles human behavior simulation
    No domain dependencies - pure infrastructure concern
    """
    
    def __init__(self, driver: Chrome):
        """
        Initialize human behavior simulator.
        
        Args:
            driver: Chrome WebDriver instance
        """
        self.driver = driver
        self.actions = ActionChains(driver)
        self.wait = WebDriverWait(driver, 10)
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🤖 HumanBehaviorSimulator initialized")
    
    def random_sleep(self, min_time: float = 1.0, max_time: float = 3.0) -> None:
        """
        Sleep for a random duration to simulate human behavior.
        
        Args:
            min_time: Minimum sleep duration in seconds
            max_time: Maximum sleep duration in seconds
        """
        sleep_time = random.uniform(min_time, max_time)
        self.logger.debug(f"😴 Random sleep: {sleep_time:.2f}s")
        time.sleep(sleep_time)
    
    def scroll_to_element(self, element) -> bool:
        """
        Scroll to element with smooth human-like behavior.
        
        Args:
            element: WebElement to scroll to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # JavaScript smooth scroll to center the element
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", 
                element
            )
            self.logger.debug("📜 Smooth scroll to element")
            self.random_sleep(0.5, 1.0)
            return True
        except Exception as e:
            self.logger.error(f"💥 Scroll error: {str(e)}")
            return False
    
    def ensure_element_visible(self, element) -> bool:
        """
        Ensure element is visible and interactable.
        
        Args:
            element: WebElement to check
            
        Returns:
            True if element is visible, False otherwise
        """
        try:
            if not element.is_displayed():
                self.logger.debug("👁️ Element not visible, attempting scroll")
                self.scroll_to_element(element)
                self.random_sleep(0.5, 1.0)
                
                if not element.is_displayed():
                    self.logger.warning("⚠️ Element still not visible after scroll")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"💥 Visibility check error: {str(e)}")
            return False
    
    def human_like_click(self, element) -> None:
        """
        Perform human-like click with mouse movement and timing.
        
        Args:
            element: WebElement to click
        """
        try:
            # Ensure element is visible
            if not self.ensure_element_visible(element):
                self.logger.debug("🖱️ Element not visible, using JavaScript click")
                self.driver.execute_script("arguments[0].click();", element)
                self.random_sleep(0.1, 0.3)
                return
            
            # Human-like ActionChains click
            self.actions = ActionChains(self.driver)
            self.actions.move_to_element(element)
            self.random_sleep(0.1, 0.3)  # Natural pause before click
            self.actions.click()
            self.actions.perform()
            
            self.logger.debug("🖱️ Human-like click performed")
            
        except Exception as e:
            self.logger.error(f"💥 Click error: {str(e)}")
            # Fallback to JavaScript click
            try:
                self.logger.debug("🔄 Fallback to JavaScript click")
                self.driver.execute_script("arguments[0].click();", element)
            except Exception as js_error:
                self.logger.error(f"💥 JavaScript click error: {str(js_error)}")
    
    def human_like_type(self, element, text: str) -> None:
        """
        Type text with human-like timing and behavior.
        
        Args:
            element: Input WebElement
            text: Text to type
        """
        try:
            # Ensure element is visible and clickable
            if not self.ensure_element_visible(element):
                self.logger.debug("⌨️ Element not visible, using JavaScript")
                self.driver.execute_script(f"arguments[0].value = '{text}';", element)
                self.random_sleep(0.1, 0.3)
                return
            
            # Click to focus
            self.actions = ActionChains(self.driver)
            self.actions.move_to_element(element)
            self.random_sleep(0.1, 0.3)
            self.actions.click()
            self.actions.perform()
            
            # Clear field
            element.clear()
            
            # Type character by character with human timing
            self.logger.debug(f"⌨️ Typing {len(text)} characters with human timing")
            for char in text:
                element.send_keys(char)
                # Random typing speed between 50-150ms per character
                self.random_sleep(0.05, 0.15)
            
            self.logger.debug("✅ Human-like typing completed")
            
        except Exception as e:
            self.logger.error(f"💥 Typing error: {str(e)}")
            # Fallback to JavaScript
            try:
                self.logger.debug("🔄 Fallback to JavaScript value assignment")
                self.driver.execute_script(f"arguments[0].value = '{text}';", element)
            except Exception as js_error:
                self.logger.error(f"💥 JavaScript typing error: {str(js_error)}")
    
    def random_scroll(self, scroll_amount: Optional[int] = None) -> None:
        """
        Perform random scrolling to simulate natural browsing.
        
        Args:
            scroll_amount: Pixels to scroll (random if None)
        """
        if scroll_amount is None:
            scroll_amount = random.randint(100, 500)
        
        try:
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self.logger.debug(f"📜 Random scroll: {scroll_amount}px")
            self.random_sleep(0.2, 0.5)
        except Exception as e:
            self.logger.error(f"💥 Random scroll error: {str(e)}")
    
    def move_mouse_randomly(self) -> None:
        """
        Move mouse randomly to simulate natural user behavior.
        """
        try:
            viewport_width = self.driver.execute_script("return window.innerWidth;")
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            
            # Calculate safe movement within viewport
            max_move = 200
            x_offset = random.randint(-max_move, max_move)
            y_offset = random.randint(-max_move, max_move)
            
            # Ensure movement stays within viewport bounds
            new_x = max(0, min(viewport_width - 10, self.last_mouse_x + x_offset))
            new_y = max(0, min(viewport_height - 10, self.last_mouse_y + y_offset))
            
            # Calculate relative movement
            x_move = new_x - self.last_mouse_x
            y_move = new_y - self.last_mouse_y
            
            # Perform mouse movement
            try:
                self.actions = ActionChains(self.driver)
                self.actions.move_by_offset(x_move, y_move)
                self.actions.perform()
                
                # Update position tracking
                self.last_mouse_x = new_x
                self.last_mouse_y = new_y
                self.logger.debug(f"🖱️ Random mouse movement: ({x_move}, {y_move})")
                
            except Exception:
                # Reset mouse to center if movement fails
                self.logger.debug("🔄 Mouse movement failed, resetting to center")
                body = self.driver.find_element(By.TAG_NAME, "body")
                self.actions = ActionChains(self.driver)
                self.actions.move_to_element(body)
                self.actions.perform()
                self.last_mouse_x = viewport_width // 2
                self.last_mouse_y = viewport_height // 2
            
            self.random_sleep(0.1, 0.3)
            
        except Exception as e:
            self.logger.error(f"💥 Mouse movement error: {str(e)}")
            # Reset tracking on error
            self.last_mouse_x = 0
            self.last_mouse_y = 0
    
    def simulate_human_behavior(self) -> None:
        """
        Perform a combination of human-like behaviors.
        """
        try:
            self.logger.debug("🎭 Simulating human behavior sequence")
            
            # Random mouse movement
            self.move_mouse_randomly()
            
            # Random scrolling
            self.random_scroll()
            
            # Natural pause
            self.random_sleep()
            
            self.logger.debug("✅ Human behavior simulation completed")
            
        except Exception as e:
            self.logger.error(f"💥 Human behavior simulation error: {str(e)}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """
        Wait for element with human behavior simulation.
        
        Args:
            by: Locator type
            value: Locator value
            timeout: Maximum wait time
            
        Returns:
            WebElement when found
        """
        try:
            self.logger.debug(f"⏳ Waiting for element: {by} = {value} (timeout: {timeout}s)")
            
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            
            # Scroll to element and simulate behavior
            self.scroll_to_element(element)
            self.simulate_human_behavior()
            
            self.logger.debug(f"✅ Element found with human behavior: {by} = {value}")
            return element
            
        except Exception as e:
            self.logger.error(f"💥 Element wait error: {str(e)}")
            raise
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = 10):
        """
        Wait for clickable element with human behavior.
        
        Args:
            by: Locator type
            value: Locator value  
            timeout: Maximum wait time
            
        Returns:
            Clickable WebElement
        """
        try:
            self.logger.debug(f"🖱️ Waiting for clickable: {by} = {value} (timeout: {timeout}s)")
            
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            
            # Scroll to element and simulate behavior
            self.scroll_to_element(element)
            self.simulate_human_behavior()
            
            self.logger.debug(f"✅ Clickable element found: {by} = {value}")
            return element
            
        except Exception as e:
            self.logger.error(f"💥 Clickable element wait error: {str(e)}")
            raise 