#!/usr/bin/env python3
"""
Smart Event-Driven Orchestrator for E-Devlet Automation System.
Uses SQLite queue for reliable event processing with 2-hour batch intervals.
"""

import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.utils.sqlite_queue import SQLiteEventQueue
from src.models.entities import ProcessingStats
from src.services.document_verification_service import DocumentVerificationService
from src.services.backend_integration_service import BackendIntegrationService
from src.services.document_processing_service import DocumentProcessingService
from src.utils.logging import LogManager
from src.utils.system_setup import SystemSetup, DirectoryManager
from src.config.config import config
from src.constants import ERROR_MESSAGES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('orchestrator.log')
    ]
)

logger = logging.getLogger(__name__)

class SmartEDevletOrchestrator:
    """
    Smart orchestrator that processes events from SQLite queue every 2 hours.
    Includes robust state management and batch processing capabilities.
    """
    
    def __init__(self, db_path: str = 'queue.db'):
        """
        Initialize the smart orchestrator.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self.queue = SQLiteEventQueue(db_path)
        self.state_file = 'orchestrator_state.json'
        
        # Timing configuration (2 hours = 7200 seconds)
        self.processing_interval_hours = 2
        self.processing_interval_seconds = self.processing_interval_hours * 3600
        self.check_interval_seconds = 60  # Check every minute
        
        # Processing configuration
        self.batch_size = 100  # Events to process per batch
        
        # Service components
        self.directory_manager = None
        self.log_manager = None
        self.verification_service = None
        self.backend_service = None
        self.processing_service = None
        
        # Initialize services
        self._setup_system()
        
        logger.info(f"🎯 Smart E-Devlet Orchestrator initialized")
        logger.info(f"📊 Database: {self.db_path}")
        logger.info(f"⏰ Processing interval: {self.processing_interval_hours} hours")
        logger.info(f"🔍 Check interval: {self.check_interval_seconds} seconds")
    
    def _setup_system(self):
        """Setup system components and services."""
        try:
            logger.info("🔧 Setting up system components...")
            
            # Setup SSL certificates
            SystemSetup.setup_ssl_certificates()
            
            # Validate environment
            SystemSetup.validate_environment()
            
            # Setup directories
            project_root = SystemSetup.get_project_root()
            self.directory_manager = DirectoryManager(project_root)
            self.directory_manager.setup_all_directories()
            
            # Setup logging
            self.log_manager = LogManager(self.directory_manager.get_logs_directory())
            
            # Setup services
            self._setup_services()
            
            logger.info("✅ System setup completed successfully")
            
        except Exception as e:
            logger.error(f"💥 System setup failed: {str(e)}")
            raise
    
    def _setup_services(self):
        """Setup all processing services."""
        try:
            # Document verification service
            self.verification_service = DocumentVerificationService()
            
            # Backend integration service
            self.backend_service = BackendIntegrationService(
                base_url=config.BACKEND_API_BASE_URL,
                email=config.BACKEND_API_EMAIL,
                password=config.BACKEND_API_PASSWORD
            )
            
            # Document processing service
            self.processing_service = DocumentProcessingService(
                verification_service=self.verification_service,
                backend_service=self.backend_service,
                log_manager=self.log_manager
            )
            
            logger.info("🔧 All services initialized successfully")
            
        except Exception as e:
            logger.error(f"💥 Service setup failed: {str(e)}")
            raise
    
    def _get_orchestrator_state(self) -> Dict[str, Any]:
        """
        Get the current orchestrator state from file.
        
        Returns:
            Dict containing state information
        """
        default_state = {
            "last_successful_run_timestamp": None,
            "is_processing": False,
            "last_batch_size": 0,
            "total_processed_today": 0,
            "last_cleanup_timestamp": None
        }
        
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    # Merge with defaults to handle new fields
                    return {**default_state, **state}
            else:
                # Create initial state file
                self._save_orchestrator_state(default_state)
                return default_state
                
        except Exception as e:
            logger.error(f"💥 Failed to read orchestrator state: {str(e)}")
            return default_state
    
    def _save_orchestrator_state(self, state: Dict[str, Any]) -> None:
        """
        Save the orchestrator state to file.
        
        Args:
            state: State dictionary to save
        """
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            logger.debug(f"📝 Orchestrator state saved: {state}")
            
        except Exception as e:
            logger.error(f"💥 Failed to save orchestrator state: {str(e)}")
    
    def _should_start_processing(self) -> tuple[bool, str]:
        """
        Check if processing should start based on timing and queue status.
        
        Returns:
            Tuple of (should_process: bool, reason: str)
        """
        state = self._get_orchestrator_state()
        
        # Check if already processing
        if state.get("is_processing", False):
            return False, "🔄 Already processing events"
        
        # Check if there are events to process
        new_event_count = self.queue.get_new_event_count()
        if new_event_count == 0:
            return False, f"📭 No new events in queue"
        
        # Check timing constraint (2-hour interval)
        last_run_timestamp = state.get("last_successful_run_timestamp")
        if last_run_timestamp:
            try:
                last_run = datetime.fromisoformat(last_run_timestamp)
                time_since_last = datetime.now() - last_run
                
                if time_since_last.total_seconds() < self.processing_interval_seconds:
                    remaining_seconds = self.processing_interval_seconds - time_since_last.total_seconds()
                    remaining_minutes = int(remaining_seconds / 60)
                    return False, f"⏰ Too soon - {remaining_minutes} minutes remaining until next run"
                    
            except ValueError:
                logger.warning(f"⚠️ Invalid timestamp format: {last_run_timestamp}")
        
        return True, f"✅ Ready to process {new_event_count} events"
    
    def _convert_queue_event_to_processing_format(self, queue_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert a queue event to the format expected by the processing service.
        
        Args:
            queue_event: Event from the SQLite queue
            
        Returns:
            Processed event data or None if invalid
        """
        try:
            # Parse the event_data JSON string
            event_data = json.loads(queue_event['event_data'])
            
            # Handle nested event structure
            if 'event' in event_data:
                event = event_data['event']
            else:
                event = event_data
            
            # Extract required fields
            user_id = event.get('userId', '')
            identity_number = event.get('identityNumber', '')
            event_type = event.get('eventType', '')
            
            if not user_id or not identity_number:
                logger.warning(f"⚠️ Event missing required data: userId={user_id}, identityNumber={identity_number}")
                return None
            
            if not event_type:
                logger.warning(f"⚠️ Event missing eventType: userId={user_id}")
                return None
            
            # Extract document data
            document_number = ''
            document_id = ''
            
            if 'eventData' in event:
                event_data_inner = event['eventData']
                document_number = event_data_inner.get('documentNumber', '')
                document_id = event_data_inner.get('id', '')
            
            if not document_number:
                logger.warning(f"⚠️ Event missing document number: userId={user_id}")
                return None
            
            # Create processing format based on event type
            result = {
                "identityNumber": identity_number,
                "documentNumber": document_number,
                "userId": user_id,
                "eventType": event_type,
                "queueEventId": queue_event['id']  # Add queue event ID for status updates
            }
            
            # Add document type specific fields
            if "Education" in event_type:
                result["educationId"] = document_id or user_id  # Fallback to user_id
            elif "Security" in event_type:
                result["securityId"] = document_id or user_id  # Fallback to user_id
            else:
                logger.warning(f"⚠️ Unknown event type: {event_type} for userId={user_id}")
                return None
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"💥 Invalid JSON in event data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"💥 Error converting event: {str(e)}")
            return None
    
    def _process_single_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a single event and update its status in the queue.
        
        Args:
            event_data: Event data with queueEventId
            
        Returns:
            True if processing was successful, False otherwise
        """
        queue_event_id = event_data.get("queueEventId")
        
        try:
            # Remove queueEventId from event data before processing
            processing_data = {k: v for k, v in event_data.items() if k != "queueEventId"}
            
            # Process the event
            success = self.processing_service.process_verification_event(processing_data)
            
            # Update queue status
            if success:
                self.queue.update_event_status(queue_event_id, 'processed')
                logger.info(f"✅ Event {queue_event_id} processed successfully")
            else:
                self.queue.update_event_status(
                    queue_event_id, 
                    'failed', 
                    'Document verification or backend update failed'
                )
                logger.warning(f"❌ Event {queue_event_id} processing failed")
            
            return success
            
        except Exception as e:
            error_msg = f"Exception during event processing: {str(e)}"
            logger.error(f"💥 {error_msg}")
            
            # Update queue status with error
            try:
                self.queue.update_event_status(queue_event_id, 'failed', error_msg)
            except Exception as status_error:
                logger.error(f"💥 Failed to update event status: {str(status_error)}")
            
            return False
    
    def _process_batch(self) -> ProcessingStats:
        """
        Process a batch of events from the queue.
        
        Returns:
            ProcessingStats: Statistics for the batch processing
        """
        stats = ProcessingStats()
        
        try:
            logger.info(f"📦 Fetching batch of {self.batch_size} events...")
            
            # Fetch events from queue (this marks them as 'processing')
            queue_events = self.queue.fetch_new_events_for_processing(self.batch_size)
            
            if not queue_events:
                logger.info("📭 No events to process")
                return stats
            
            stats.total_users = len(queue_events)
            logger.info(f"🎯 Processing {len(queue_events)} events...")
            
            # Convert events to processing format
            processing_events = []
            for queue_event in queue_events:
                converted_event = self._convert_queue_event_to_processing_format(queue_event)
                if converted_event:
                    processing_events.append(converted_event)
                else:
                    # Mark unconvertible events as failed
                    self.queue.update_event_status(
                        queue_event['id'], 
                        'failed', 
                        'Invalid event format or missing required data'
                    )
                    stats.add_failed_verification()
            
            logger.info(f"📋 {len(processing_events)} events ready for processing")
            
            # Process each event
            for event_index, event_data in enumerate(processing_events, 1):
                try:
                    logger.info(f"🔄 Processing event {event_index}/{len(processing_events)}: {event_data.get('userId', 'unknown')}")
                    
                    success = self._process_single_event(event_data)
                    
                    if success:
                        stats.add_successful_verification()
                    else:
                        stats.add_failed_verification()
                    
                    stats.increment_processed_users()
                    
                except Exception as e:
                    logger.error(f"💥 Error processing event {event_index}: {str(e)}")
                    stats.add_failed_verification()
                    stats.increment_processed_users()
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"💥 Batch processing error: {str(e)}")
            return stats
    
    def _run_processing_cycle(self) -> None:
        """
        Run a complete processing cycle with proper state management.
        """
        state = self._get_orchestrator_state()
        
        try:
            # Lock processing
            state["is_processing"] = True
            self._save_orchestrator_state(state)
            
            logger.info("🚀 Starting processing cycle...")
            
            # Test backend connection
            if not self.backend_service.test_connection():
                logger.warning("⚠️ Backend connection failed - will continue with verification only")
            
            # Process batch
            stats = self._process_batch()
            
            # Log results
            summary = f"✅ Cycle completed - Processed: {stats.processed_users}, " \
                     f"Successful: {stats.successful_verifications}, " \
                     f"Failed: {stats.failed_verifications}"
            
            logger.info(summary)
            self.log_manager.log_processing_cycle(summary)
            
            # Update state with success
            state["last_successful_run_timestamp"] = datetime.now().isoformat()
            state["last_batch_size"] = stats.processed_users
            state["total_processed_today"] = state.get("total_processed_today", 0) + stats.processed_users
            
        except Exception as e:
            error_msg = f"Processing cycle error: {str(e)}"
            logger.error(f"💥 {error_msg}")
            self.log_manager.log_error(e, "Processing cycle failed")
            
        finally:
            # Always unlock processing
            state["is_processing"] = False
            self._save_orchestrator_state(state)
            logger.info("🔓 Processing cycle completed, lock released")
    
    def _perform_maintenance(self) -> None:
        """Perform maintenance tasks like cleaning up old events."""
        try:
            state = self._get_orchestrator_state()
            last_cleanup = state.get("last_cleanup_timestamp")
            
            # Cleanup once per day
            should_cleanup = False
            if not last_cleanup:
                should_cleanup = True
            else:
                try:
                    last_cleanup_time = datetime.fromisoformat(last_cleanup)
                    time_since_cleanup = datetime.now() - last_cleanup_time
                    should_cleanup = time_since_cleanup.total_seconds() > 86400  # 24 hours
                except ValueError:
                    should_cleanup = True
            
            if should_cleanup:
                logger.info("🧹 Performing maintenance - cleaning up old events...")
                deleted_count = self.queue.cleanup_old_events(days_old=30)
                
                state["last_cleanup_timestamp"] = datetime.now().isoformat()
                self._save_orchestrator_state(state)
                
                logger.info(f"🧹 Maintenance completed - {deleted_count} old events cleaned up")
            
        except Exception as e:
            logger.error(f"💥 Maintenance error: {str(e)}")
    
    def run(self) -> None:
        """
        Main orchestrator loop - checks conditions and processes events every 2 hours.
        """
        logger.info("🎯 Smart E-Devlet Orchestrator started")
        logger.info(f"📊 Queue statistics: {self.queue.get_queue_stats()}")
        logger.info("=" * 60)
        
        try:
            while True:
                try:
                    # Check if processing should start
                    should_process, reason = self._should_start_processing()
                    
                    logger.info(f"🔍 Check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {reason}")
                    
                    if should_process:
                        # Run processing cycle
                        self._run_processing_cycle()
                        
                        # Perform maintenance after processing
                        self._perform_maintenance()
                    
                    # Sleep until next check
                    time.sleep(self.check_interval_seconds)
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Shutdown requested by user")
                    break
                except Exception as e:
                    logger.error(f"💥 Error in main loop: {str(e)}")
                    self.log_manager.log_error(e, "Main loop error")
                    
                    # Sleep before retrying
                    time.sleep(self.check_interval_seconds)
                    continue
                    
        except KeyboardInterrupt:
            logger.info("🛑 Orchestrator stopped by user")
        except Exception as e:
            logger.error(f"💥 Fatal error: {str(e)}")
            raise
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up resources and reset processing lock."""
        try:
            logger.info("🧹 Cleaning up orchestrator...")
            
            # Reset processing lock in case of unexpected shutdown
            state = self._get_orchestrator_state()
            if state.get("is_processing", False):
                logger.warning("⚠️ Clearing processing lock from previous run")
                state["is_processing"] = False
                self._save_orchestrator_state(state)
            
            # Cleanup services
            if self.verification_service:
                try:
                    self.verification_service._cleanup()
                except:
                    pass
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"💥 Cleanup error: {str(e)}")

def run_orchestrator(db_path: str = 'queue.db'):
    """
    Entry point for running the orchestrator.
    
    Args:
        db_path: Path to the SQLite database
    """
    try:
        orchestrator = SmartEDevletOrchestrator(db_path)
        orchestrator.run()
    except Exception as e:
        logger.error(f"💥 Failed to start orchestrator: {str(e)}")
        raise

# Alias for backward compatibility
main = run_orchestrator

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart E-Devlet Orchestrator')
    parser.add_argument('--db-path', default='queue.db', help='SQLite database path')
    parser.add_argument('--check-interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--processing-interval', type=int, default=2, help='Processing interval in hours')
    
    args = parser.parse_args()
    
    # Create orchestrator with custom settings
    orchestrator = SmartEDevletOrchestrator(args.db_path)
    
    if args.check_interval != 60:
        orchestrator.check_interval_seconds = args.check_interval
        
    if args.processing_interval != 2:
        orchestrator.processing_interval_hours = args.processing_interval
        orchestrator.processing_interval_seconds = args.processing_interval * 3600
    
    # Run the orchestrator
    orchestrator.run()
