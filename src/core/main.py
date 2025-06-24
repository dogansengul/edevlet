"""
Main entry point for the eDevlet automation system.

This module serves as the entry point and delegates the actual processing
to the orchestrator which manages all the business logic and services.
"""
from .orchestrator import main

if __name__ == "__main__":
    main() 