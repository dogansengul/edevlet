"""
Browser Infrastructure Package - Clean Architecture
Advanced web automation capabilities with human-like behavior and anti-detection
"""

from .browser_factory import BrowserFactory
from .human_behavior_simulator import HumanBehaviorSimulator
from .strategy_factory import StrategyFactory, ElementStrategy
from .element_finder import ElementFinder

__all__ = [
    'BrowserFactory',
    'HumanBehaviorSimulator', 
    'StrategyFactory',
    'ElementStrategy',
    'ElementFinder'
] 