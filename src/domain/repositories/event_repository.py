"""
Event Repository Interface - Domain Layer
Clean Architecture - Dependency Inversion Principle
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.event import Event, EventStatus


class IEventRepository(ABC):
    """
    Event Repository Interface.
    
    Follows Dependency Inversion Principle:
    - High-level modules (Use Cases) depend on this abstraction
    - Low-level modules (Infrastructure) implement this interface
    
    Interface Segregation Principle:
    - Focused interface with only event-related operations
    """
    
    @abstractmethod
    def save(self, event: Event) -> Event:
        """
        Save an event to persistence.
        
        Args:
            event: Event entity to save
            
        Returns:
            Event with assigned ID if it was new
        """
        pass
    
    @abstractmethod
    def find_by_id(self, event_id: str) -> Optional[Event]:
        """
        Find event by ID.
        
        Args:
            event_id: Unique event identifier
            
        Returns:
            Event if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_pending_events(self, limit: int = 100) -> List[Event]:
        """
        Find events that can be processed (NEW or RETRYING status).
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of events ready for processing
        """
        pass
    
    @abstractmethod
    def find_failed_events_for_retry(self, limit: int = 10) -> List[Event]:
        """
        Find failed events that are eligible for retry.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of failed events that can be retried
        """
        pass
    
    @abstractmethod
    def update_status(self, event: Event) -> None:
        """
        Update event status and metadata.
        
        Args:
            event: Event with updated status
        """
        pass
    
    @abstractmethod
    def count_by_status(self, status: EventStatus) -> int:
        """
        Count events by status.
        
        Args:
            status: Event status to count
            
        Returns:
            Number of events with given status
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> dict:
        """
        Get event processing statistics.
        
        Returns:
            Dictionary with counts by status
        """
        pass
    
    @abstractmethod
    def cleanup_old_events(self, days_old: int = 30) -> int:
        """
        Clean up old processed events.
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            Number of events deleted
        """
        pass 