#!/usr/bin/env python3
"""
E-Devlet Automation Service
Simple Flask API + Background Job + Daemon Mode
"""
import os
import signal
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Domain imports
from domain.entities.event import Event
from domain.entities.user import User
from domain.value_objects.identity_number import IdentityNumber
from domain.value_objects.document_number import DocumentNumber
from domain.value_objects.event_type import EventType

# Application imports
from application.use_cases.receive_event_use_case import ReceiveEventUseCase
from application.use_cases.process_document_use_case import ProcessDocumentUseCase, ValidationResult

# Infrastructure imports
from infrastructure.config.app_config import AppConfig
from infrastructure.logging.logger_setup import setup_logging
from infrastructure.repositories.sqlite_event_repository import SqliteEventRepository
from infrastructure.scheduling.background_scheduler import BackgroundScheduler
from infrastructure.external_services.edevlet_service import EdevletService
from infrastructure.external_services.backend_integration_service import BackendIntegrationService


class EdevletServiceAdapter:
    """Adapter to make EdevletService compatible with IDocumentValidator interface."""
    
    def __init__(self, edevlet_service: EdevletService):
        self.edevlet_service = edevlet_service
        self.logger = logging.getLogger(__name__)
    
    def validate_document(self, document_number: str, identity_number: str) -> ValidationResult:
        """Adapt EdevletService.verify_document to ValidationResult."""
        try:
            result = self.edevlet_service.verify_document(document_number, identity_number)
            
            if result.get("success", False):
                return ValidationResult.success_result(
                    message=result.get("message", "Verification successful"),
                    files=result.get("files", [])
                )
            else:
                return ValidationResult.failure_result(
                    message=result.get("error", "Verification failed"),
                    error_code="EDEVLET_ERROR"
                )
        except Exception as e:
            self.logger.error(f"EdevletService adapter error: {str(e)}")
            return ValidationResult.failure_result(
                message=f"Adapter error: {str(e)}",
                error_code="ADAPTER_ERROR"
            )


def load_environment():
    """Load environment variables with defaults."""
    defaults = {
        "FLASK_HOST": "127.0.0.1",
        "FLASK_PORT": "5002",
        "FLASK_DEBUG": "false",
        "SQLITE_DB_PATH": "data/events.db",
        "LOG_LEVEL": "INFO",
        "LOG_FILE": "logs/edevlet_service.log",
        "BACKEND_BASE_URL": "https://api.example.com",
        "BACKEND_TIMEOUT": "30",
        "SCHEDULE_INTERVAL_HOURS": "2",
        "EDEVLET_USERNAME": "",
        "EDEVLET_PASSWORD": "",
        "EDEVLET_HEADLESS": "true",
        "EDEVLET_TIMEOUT": "60",
        "EDEVLET_WAIT_TIME": "3",
        "EDEVLET_DEBUG": "false"
    }
    
    # Set defaults if not present
    for key, value in defaults.items():
        if key not in os.environ:
            os.environ[key] = value

def setup_services():
    """Initialize all services."""
    logger = logging.getLogger(__name__)
    
    # Repository with database path
    db_path = os.getenv("SQLITE_DB_PATH", "data/events.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    event_repo = SqliteEventRepository(db_path)
    
    # Backend notifier
    backend_notifier = BackendIntegrationService(
        base_url=os.getenv("BACKEND_BASE_URL", "https://api.example.com"),
        email=os.getenv("BACKEND_EMAIL", ""),
        password=os.getenv("BACKEND_PASSWORD", ""),
        timeout=int(os.getenv("BACKEND_TIMEOUT", "30"))
    )
    
    # Document validator (real edevlet service with adapter)
    edevlet_service = EdevletService(
        headless=os.getenv("EDEVLET_HEADLESS", "true").lower() == "true",
        timeout=int(os.getenv("EDEVLET_TIMEOUT", "60"))
    )
    document_validator = EdevletServiceAdapter(edevlet_service)
    
    logger.info("✅ Real services initialized")
    
    return event_repo, backend_notifier, document_validator

def create_flask_app(event_repo, backend_notifier, document_validator):
    """Create and configure Flask application."""
    app = Flask(__name__)
    CORS(app)
    
    # Use cases
    receive_event_use_case = ReceiveEventUseCase(event_repo)
    process_document_use_case = ProcessDocumentUseCase(
        event_repo, 
        document_validator, 
        backend_notifier
    )
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'service': 'edevlet-automation',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/events', methods=['POST'])
    def receive_event():
        try:
            data = request.get_json()
            
            # Create domain objects
            user = User(IdentityNumber(data['identity_number']))
            document_number = DocumentNumber(data['document_number'])
            event_type = EventType(data['event_type'])
            
            # Create and save event
            event = Event.create(user, document_number, event_type)
            receive_event_use_case.execute(event)
            
            return jsonify({
                'success': True,
                'event_id': str(event.id),
                'message': 'Event received and queued'
            }), 201
            
        except Exception as e:
            logging.error(f"Error receiving event: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        try:
            pending_count = len(event_repo.find_pending_events())
            return jsonify({
                'pending_events': pending_count,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/process', methods=['POST'])
    def manual_process():
        try:
            events = event_repo.find_pending_events()
            processed = 0
            
            for event in events:
                process_document_use_case.execute(event)
                processed += 1
            
            return jsonify({
                'success': True,
                'processed': processed,
                'message': f'Processed {processed} events'
            })
            
        except Exception as e:
            logging.error(f"Error in manual processing: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app

def setup_background_processing(event_repo, document_validator, backend_notifier):
    """Setup background scheduler for automatic processing."""
    process_document_use_case = ProcessDocumentUseCase(
        event_repo, 
        document_validator, 
        backend_notifier
    )
    
    def process_pending_events():
        """Background job to process pending events."""
        logger = logging.getLogger(__name__)
        events = event_repo.find_pending_events()
        
        if not events:
            logger.info("📭 No pending events to process")
            return
            
        logger.info(f"📊 Processing {len(events)} pending events")
        
        for event in events:
            try:
                process_document_use_case.execute(event)
            except Exception as e:
                logger.error(f"Error processing event {event.id}: {e}")
    
    scheduler = BackgroundScheduler()
    interval_hours = int(os.getenv("SCHEDULE_INTERVAL_HOURS", "2"))
    scheduler.schedule_job(process_pending_events, interval_hours)
    
    return scheduler

def setup_signal_handlers(scheduler):
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger = logging.getLogger(__name__)
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        scheduler.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point."""
    # Load environment
    load_environment()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize services
        event_repo, backend_notifier, document_validator = setup_services()
        
        # Setup background processing
        scheduler = setup_background_processing(event_repo, document_validator, backend_notifier)
        scheduler.start()
        
        # Setup signal handlers
        setup_signal_handlers(scheduler)
        
        # Create Flask app
        app = create_flask_app(event_repo, backend_notifier, document_validator)
        
        # Start Flask app
        host = os.getenv("FLASK_HOST", "127.0.0.1")
        port = int(os.getenv("FLASK_PORT", "5002"))
        debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
        
        logger.info(f"🌐 Flask API starting on {host}:{port}")
        logger.info(f"📅 Background processing every {os.getenv('SCHEDULE_INTERVAL_HOURS', '2')} hours")
        logger.info(f"📝 Logs: {os.getenv('LOG_FILE', 'logs/edevlet_service.log')}")
        logger.info("✅ Service ready!")
        
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 