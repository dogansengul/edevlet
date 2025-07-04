"""
SQLite Event Repository - Infrastructure Layer
Clean Architecture - Concrete implementation of domain repository interface
"""
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from domain.entities.event import Event, EventStatus
from domain.value_objects.event_type import EventType
from domain.value_objects.document_number import DocumentNumber
from domain.value_objects.identity_number import IdentityNumber
from domain.repositories.event_repository import IEventRepository


class SqliteEventRepository(IEventRepository):
    """
    SQLite implementation of Event Repository.
    
    Implements IEventRepository interface (Liskov Substitution Principle)
    Single Responsibility: Only handles Event persistence
    """
    
    def __init__(self, db_path: str):
        """Initialize repository and create tables if they don't exist."""
        self.db_path = db_path
        self.logger = logging.getLogger("queue")
        self._init_db()
    
    def _init_db(self) -> None:
        """Create database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create events table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        identity_number TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        document_number TEXT,
                        status TEXT NOT NULL DEFAULT 'new',
                        retry_count INTEGER DEFAULT 0,
                        event_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processed_at TIMESTAMP,
                        error_message TEXT
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)")
                
                conn.commit()
                self.logger.info("Database tables created/verified successfully", extra={"db_path": self.db_path})
                
        except Exception as e:
            self.logger.error(f"Database creation error: {str(e)}", extra={"db_path": self.db_path}, exc_info=True)
            raise
    
    def save(self, event: Event) -> Event:
        """Save event to database."""
        is_new = event.id is None
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if is_new:
                    # Insert new event
                    cursor.execute("""
                        INSERT INTO events (
                            user_id, identity_number, event_type, document_number,
                            status, retry_count, event_data, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event.user_id,
                        str(event.identity_number),
                        event.event_type.value,
                        str(event.document_number) if event.document_number else None,
                        event.status.value,
                        event.retry_count,
                        json.dumps(event.event_data) if event.event_data else None,
                        event.created_at.isoformat(),
                        event.updated_at.isoformat()
                    ))
                    
                    event.id = cursor.lastrowid
                    self.logger.info(
                        "New event saved to queue",
                        extra={"event_id": event.id, "event_type": str(event.event_type), "status": event.status.value}
                    )
                    
                else:
                    # Update existing event
                    cursor.execute("""
                        UPDATE events SET
                            status = ?, retry_count = ?, updated_at = ?,
                            processed_at = ?, error_message = ?
                        WHERE id = ?
                    """, (
                        event.status.value,
                        event.retry_count,
                        event.updated_at.isoformat(),
                        event.processed_at.isoformat() if event.processed_at else None,
                        event.error_message,
                        event.id
                    ))
                    
                    self.logger.info(
                        "Event status updated",
                        extra={"event_id": event.id, "new_status": event.status.value, "retry_count": event.retry_count}
                    )
                
                conn.commit()
                return event
                
        except Exception as e:
            self.logger.error(
                "Error saving event to database",
                extra={"event_id": event.id, "is_new": is_new},
                exc_info=True
            )
            raise
    
    def find_by_id(self, event_id: int) -> Optional[Event]:
        """Find event by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
                row = cursor.fetchone()
                
                if row:
                    self.logger.debug(f"Event found by ID", extra={"event_id": event_id})
                    return self._row_to_event(row)
                
                self.logger.warning(f"Event not found by ID", extra={"event_id": event_id})
                return None
                
        except Exception as e:
            self.logger.error(f"Error finding event by ID", extra={"event_id": event_id}, exc_info=True)
            raise
    
    def find_pending_events(self, limit: int = 10) -> List[Event]:
        """Find pending events for processing."""
        self.logger.debug("Searching for pending events", extra={"limit": limit})
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM events 
                    WHERE status = 'new' 
                    ORDER BY created_at ASC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                self.logger.info(f"Found {len(rows)} pending events to process.", extra={"count": len(rows), "limit": limit})
                return [self._row_to_event(row) for row in rows]
                
        except Exception as e:
            self.logger.error("Error finding pending events", exc_info=True)
            raise
    
    def find_failed_events_for_retry(self, max_retries: int = 3, limit: int = 10) -> List[Event]:
        """Find failed events eligible for retry."""
        query = """
            SELECT * FROM events 
            WHERE status = ? AND retry_count < ?
            ORDER BY created_at ASC 
            LIMIT ?
        """
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (EventStatus.FAILED.value, max_retries, limit))
            rows = cursor.fetchall()
            self.logger.info(f"Found {len(rows)} failed events for retry.", extra={"count": len(rows), "limit": limit})
            return [self._row_to_event(row) for row in rows]
    
    def update_status(self, event: Event) -> None:
        """Update event status."""
        event.updated_at = datetime.now()
        self.save(event)
    
    def count_by_status(self, status: EventStatus) -> int:
        """Count events by status."""
        query = "SELECT COUNT(*) FROM events WHERE status = ?;"
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (status.value,))
            count = cursor.fetchone()[0]
            result = count if count is not None else 0
            self.logger.debug(f"Counted {result} events with status '{status.value}'", extra={"status": status.value, "count": result})
            return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count events by status
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM events 
                    GROUP BY status
                """)
                
                status_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Total events
                cursor.execute("SELECT COUNT(*) FROM events")
                total_events = cursor.fetchone()[0]
                
                return {
                    "total_events": total_events,
                    "new": status_counts.get("new", 0),
                    "processing": status_counts.get("processing", 0),
                    "processed": status_counts.get("processed", 0),
                    "failed": status_counts.get("failed", 0),
                    "verified_docs": status_counts.get("processed", 0),
                    "rejected_docs": status_counts.get("failed", 0),
                    "retried_events": sum(1 for _ in self._get_retried_events()),
                    "pending_backend_updates": status_counts.get("processing", 0),
                    "backend_updated": status_counts.get("processed", 0),
                    "backend_failed": status_counts.get("failed", 0)
                }
                
        except Exception as e:
            self.logger.error("Error getting repository statistics", exc_info=True)
            return {}
    
    def cleanup_old_events(self, days_old: int = 30) -> int:
        """Clean up old processed events."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM events 
                    WHERE status IN ('processed', 'failed') 
                    AND created_at < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old events", extra={"deleted_count": deleted_count, "days_old": days_old})
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old events", extra={"days_old": days_old}, exc_info=True)
            raise
    
    def _get_retried_events(self):
        """Get events that have been retried."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM events WHERE retry_count > 0")
                return cursor.fetchall()
        except:
            return []
    
    def _row_to_event(self, row: sqlite3.Row) -> Event:
        """Convert database row to Event entity."""
        try:
            # Parse event data
            event_data = json.loads(row['event_data']) if row['event_data'] else {}
            
            # Create value objects
            event_type_raw = row['event_type']
            # Handle legacy format: "EventType(value='UserEducationCreated')"
            if event_type_raw.startswith('EventType(value='):
                # Extract the value from EventType(value='...')
                event_type_value = event_type_raw.split("'")[1]
            else:
                event_type_value = event_type_raw
            
            event_type = EventType(event_type_value)
            identity_number = IdentityNumber(row['identity_number'])
            document_number = DocumentNumber(row['document_number']) if row['document_number'] else None
            
            # Parse timestamps
            created_at = datetime.fromisoformat(row['created_at'])
            updated_at = datetime.fromisoformat(row['updated_at'])
            processed_at = datetime.fromisoformat(row['processed_at']) if row['processed_at'] else None
            
            # Create event
            event = Event(
                user_id=row['user_id'],
                identity_number=identity_number,
                event_type=event_type,
                event_data=event_data,
                document_number=document_number
            )
            
            # Set database fields
            event.id = row['id']
            event.status = EventStatus(row['status'])
            event.retry_count = row['retry_count']
            event.created_at = created_at
            event.updated_at = updated_at
            event.processed_at = processed_at
            event.error_message = row['error_message']
            
            return event
            
        except Exception as e:
            self.logger.error(f"💥 Error converting row to event: {str(e)}")
            raise 