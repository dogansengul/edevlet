"""
EDevlet Automation System

A modular system for automating document verification through eDevlet platform.

Main Components:
- Models: Data structures and entities
- Services: Business logic layers
- Utils: Utility functions and helpers
- Constants: System-wide constants
- Exceptions: Custom exception classes
- Core: Main orchestrator and entry points
"""

__version__ = "2.0.0"
__author__ = "EDevlet Automation Team"

# Main entry point
from .core.orchestrator import run_orchestrator

__all__ = ['run_orchestrator']