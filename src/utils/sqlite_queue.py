import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

class SQLiteEventQueue:
    """
    Robust SQLite-based event queue with transactional safety.
    Manages event lifecycle: new -> processing -> processed/failed
    """
    
    def __init__(self, db_path: str = 'queue.db'):
        """
        Initialize the SQLite event queue.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.create_table()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper cleanup."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def create_table(self) -> None:
        """
        Create the event_queue table if it doesn't exist.
        Schema includes all necessary fields for event lifecycle management.
        """
        create_sql = """
        CREATE TABLE IF NOT EXISTS event_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_data TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            error_message TEXT,
            received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed_at DATETIME
        )
        """
        
        # Create index for better performance on status queries
        index_sql = """
        CREATE INDEX IF NOT EXISTS idx_event_queue_status 
        ON event_queue(status)
        """
        
        try:
            with self.get_connection() as conn:
                conn.execute(create_sql)
                conn.execute(index_sql)
                conn.commit()
            self.logger.info("Event queue table created/verified successfully")
        except Exception as e:
            self.logger.error(f"Failed to create event queue table: {str(e)}")
            raise
    
    def add_event(self, event_json_str: str) -> int:
        """
        Add a new event to the queue.
        
        Args:
            event_json_str: JSON string representation of the event
            
        Returns:
            int: The ID of the inserted event
            
        Raises:
            Exception: If insertion fails
        """
        try:
            # Validate JSON format
            json.loads(event_json_str)  # This will raise if invalid JSON
            
            insert_sql = """
            INSERT INTO event_queue (event_data, status) 
            VALUES (?, 'new')
            """
            
            with self.get_connection() as conn:
                cursor = conn.execute(insert_sql, (event_json_str,))
                event_id = cursor.lastrowid
                conn.commit()
                
            self.logger.info(f"Event added to queue with ID: {event_id}")
            return event_id
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            self.logger.error(f"Failed to add event to queue: {str(e)}")
            raise
    
    def fetch_new_events_for_processing(self, limit: int = 100) -> List[Dict]:
        """
        Transactionally fetch new events and mark them as processing.
        This is the critical method that ensures no race conditions.
        
        Args:
            limit: Maximum number of events to fetch
            
        Returns:
            List[Dict]: List of events ready for processing
        """
        try:
            with self.get_connection() as conn:
                # Start transaction
                conn.execute("BEGIN IMMEDIATE")
                
                # Select events to process
                select_sql = """
                SELECT id, event_data, received_at 
                FROM event_queue 
                WHERE status = 'new' 
                ORDER BY received_at ASC 
                LIMIT ?
                """
                
                cursor = conn.execute(select_sql, (limit,))
                events = [dict(row) for row in cursor.fetchall()]
                
                if not events:
                    conn.commit()
                    return []
                
                # Extract IDs for the update
                event_ids = [event['id'] for event in events]
                
                # Mark selected events as processing
                placeholders = ','.join(['?' for _ in event_ids])
                update_sql = f"""
                UPDATE event_queue 
                SET status = 'processing' 
                WHERE id IN ({placeholders})
                """
                
                conn.execute(update_sql, event_ids)
                conn.commit()
                
                self.logger.info(f"Fetched {len(events)} events for processing")
                return events
                
        except Exception as e:
            self.logger.error(f"Failed to fetch events for processing: {str(e)}")
            raise
    
    def update_event_status(self, event_id: int, status: str, error_message: str = None) -> None:
        """
        Update the status of a specific event.
        
        Args:
            event_id: ID of the event to update
            status: New status ('processed' or 'failed')
            error_message: Optional error message for failed events
        """
        valid_statuses = ['new', 'processing', 'processed', 'failed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        try:
            current_time = datetime.now().isoformat()
            
            update_sql = """
            UPDATE event_queue 
            SET status = ?, processed_at = ?, error_message = ?
            WHERE id = ?
            """
            
            with self.get_connection() as conn:
                cursor = conn.execute(update_sql, (status, current_time, error_message, event_id))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"No event found with ID: {event_id}")
                
                conn.commit()
                
            status_msg = f"Event {event_id} status updated to '{status}'"
            if error_message:
                status_msg += f" with error: {error_message}"
            self.logger.info(status_msg)
            
        except Exception as e:
            self.logger.error(f"Failed to update event status: {str(e)}")
            raise
    
    def get_new_event_count(self) -> int:
        """
        Get the count of events with 'new' status.
        
        Returns:
            int: Number of new events in the queue
        """
        try:
            count_sql = "SELECT COUNT(*) as count FROM event_queue WHERE status = 'new'"
            
            with self.get_connection() as conn:
                cursor = conn.execute(count_sql)
                result = cursor.fetchone()
                count = result['count'] if result else 0
                
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to get new event count: {str(e)}")
            raise
    
    def get_queue_stats(self) -> Dict[str, int]:
        """
        Get comprehensive queue statistics.
        
        Returns:
            Dict with counts for each status
        """
        try:
            stats_sql = """
            SELECT status, COUNT(*) as count 
            FROM event_queue 
            GROUP BY status
            """
            
            with self.get_connection() as conn:
                cursor = conn.execute(stats_sql)
                rows = cursor.fetchall()
                
            stats = {row['status']: row['count'] for row in rows}
            
            # Ensure all statuses are represented
            for status in ['new', 'processing', 'processed', 'failed']:
                if status not in stats:
                    stats[status] = 0
                    
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get queue statistics: {str(e)}")
            raise
    
    def cleanup_old_events(self, days_old: int = 30) -> int:
        """
        Clean up old processed events to prevent database bloat.
        
        Args:
            days_old: Remove events older than this many days
            
        Returns:
            int: Number of events cleaned up
        """
        try:
            cleanup_sql = """
            DELETE FROM event_queue 
            WHERE status IN ('processed', 'failed') 
            AND datetime(processed_at) < datetime('now', '-{} days')
            """.format(days_old)
            
            with self.get_connection() as conn:
                cursor = conn.execute(cleanup_sql)
                deleted_count = cursor.rowcount
                conn.commit()
                
            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old events")
                
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old events: {str(e)}")
            raise 