#!/usr/bin/env python3
"""
Event Receiver Service - Flask-based HTTP service for receiving events.
Receives events via REST API and queues them in SQLite database for processing.
"""

import os
import sys
import json
import logging
import ipaddress
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, abort

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.utils.sqlite_queue import SQLiteEventQueue
from src.config.config import config

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('event_receiver.log')
    ]
)

logger = logging.getLogger(__name__)

def ip_whitelist_required(f):
    """
    Decorator to enforce IP whitelisting for API endpoints.
    
    This decorator checks if the client's IP address is in the ALLOWED_IPS list.
    It properly handles X-Forwarded-For header for clients behind reverse proxies.
    
    Args:
        f: The Flask route function to decorate
        
    Returns:
        The decorated function that includes IP whitelist validation
        
    Raises:
        403 Forbidden: If the client IP is not in the whitelist
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the client IP address, accounting for reverse proxy headers
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Handle X-Forwarded-For header which may contain multiple IPs
        if client_ip and ',' in client_ip:
            # Take the first IP (original client) from comma-separated list
            client_ip = client_ip.split(',')[0].strip()
        
        # Remove any port number if present (e.g., "192.168.1.1:12345" -> "192.168.1.1")
        if client_ip and ':' in client_ip and not '::' in client_ip:  # Avoid breaking IPv6
            client_ip = client_ip.split(':')[0]
        
        logger.info(f"🔍 IP whitelist check: Client IP = {client_ip}")
        
        # Check if IP is in whitelist
        is_allowed = False
        
        try:
            for allowed_ip in config.ALLOWED_IPS:
                allowed_ip = allowed_ip.strip()
                
                # Handle CIDR notation (e.g., "192.168.1.0/24")
                if '/' in allowed_ip:
                    try:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if ipaddress.ip_address(client_ip) in network:
                            is_allowed = True
                            logger.info(f"✅ IP {client_ip} allowed by network range {allowed_ip}")
                            break
                    except (ipaddress.AddressValueError, ValueError) as e:
                        logger.warning(f"⚠️ Invalid network range in config: {allowed_ip} - {str(e)}")
                        continue
                
                # Handle exact IP match
                elif client_ip == allowed_ip:
                    is_allowed = True
                    logger.info(f"✅ IP {client_ip} allowed by exact match")
                    break
            
            if not is_allowed:
                logger.warning(f"🚫 Access denied for IP: {client_ip} (not in whitelist)")
                logger.info(f"📋 Current whitelist: {config.ALLOWED_IPS}")
                abort(403)  # Forbidden
            
            logger.info(f"✅ IP whitelist check passed for: {client_ip}")
            
        except Exception as e:
            logger.error(f"💥 Error in IP whitelist validation: {str(e)}")
            # In case of validation error, deny access for security
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

class EventReceiver:
    """
    Event receiver service class that handles HTTP endpoints
    and manages the SQLite event queue.
    """
    
    def __init__(self, db_path: str = 'queue.db'):
        """
        Initialize the event receiver with database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.queue = SQLiteEventQueue(db_path)
        logger.info(f"Event receiver initialized with database: {db_path}")
    
    def receive_event(self, event_data: dict) -> dict:
        """
        Process incoming event and add to queue.
        
        Args:
            event_data: The event data as a dictionary
            
        Returns:
            dict: Response containing success status and event ID
        """
        try:
            # Convert event data to JSON string for storage
            event_json_str = json.dumps(event_data)
            
            # Add event to queue
            event_id = self.queue.add_event(event_json_str)
            
            logger.info(f"✅ Event received and queued successfully - ID: {event_id}")
            logger.info(f"📋 Event content: {json.dumps(event_data, indent=2)}")
            
            # Get current queue statistics
            stats = self.queue.get_queue_stats()
            
            return {
                "success": True,
                "message": "Event received and queued successfully",
                "event_id": event_id,
                "queue_stats": stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except ValueError as e:
            error_msg = f"Invalid event data format: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"Failed to process event: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }

# Initialize event receiver
event_receiver = EventReceiver()

@app.route('/api/events', methods=['POST'])
@ip_whitelist_required
def receive_events():
    """
    REST endpoint to receive events via HTTP POST.
    
    Expected JSON format:
    {
        "event": {
            "userId": "guid-here",
            "identityNumber": "12345678901",
            "eventType": "UserCvCreated",
            "eventData": {
                "id": "cv-guid-here",
                "documentNumber": "BARCODE12345"
            }
        }
    }
    """
    try:
        # Check if request contains JSON data
        if not request.is_json:
            logger.warning("⚠️ Request does not contain JSON data")
            return jsonify({
                "success": False,
                "message": "Request must contain JSON data",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            logger.warning("⚠️ Empty request body")
            return jsonify({
                "success": False,
                "message": "Empty request body",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Log the incoming request
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        logger.info(f"📨 Incoming event from {client_ip}")
        
        # Process the event
        result = event_receiver.receive_event(data)
        
        # Return appropriate status code
        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        error_msg = f"Unexpected error processing request: {str(e)}"
        logger.error(f"💥 {error_msg}")
        return jsonify({
            "success": False,
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns service status and queue statistics.
    """
    try:
        # Test database connectivity
        stats = event_receiver.queue.get_queue_stats()
        
        return jsonify({
            "status": "healthy",
            "service": "event-receiver",
            "database": "connected",
            "queue_stats": stats,
            "timestamp": datetime.now().isoformat(),
            "uptime": "Available"  # Could be enhanced with actual uptime tracking
        }), 200
        
    except Exception as e:
        logger.error(f"💥 Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "service": "event-receiver",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/api/queue/stats', methods=['GET'])
def get_queue_stats():
    """
    Get detailed queue statistics.
    Useful for monitoring and debugging.
    """
    try:
        stats = event_receiver.queue.get_queue_stats()
        new_count = event_receiver.queue.get_new_event_count()
        
        return jsonify({
            "success": True,
            "queue_stats": stats,
            "new_events_count": new_count,
            "database_path": event_receiver.db_path,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        error_msg = f"Failed to get queue stats: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return jsonify({
            "success": False,
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with JSON response."""
    return jsonify({
        "success": False,
        "message": "Endpoint not found",
        "available_endpoints": [
            "POST /api/events",
            "GET /health",
            "GET /api/queue/stats"
        ],
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(403)
def access_forbidden(error):
    """Handle 403 Forbidden errors with JSON response."""
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    return jsonify({
        "success": False,
        "message": "Access denied: IP address not authorized",
        "client_ip": client_ip,
        "error_code": "IP_NOT_WHITELISTED",
        "timestamp": datetime.now().isoformat()
    }), 403

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors with JSON response."""
    return jsonify({
        "success": False,
        "message": "Method not allowed for this endpoint",
        "timestamp": datetime.now().isoformat()
    }), 405

def run_server(host: str = '127.0.0.1', port: int = 5001, debug: bool = False):
    """
    Run the Flask event receiver server.
    
    Args:
        host: Host address to bind to
        port: Port number to listen on
        debug: Enable debug mode
    """
    logger.info(f"🚀 Starting Event Receiver Service on {host}:{port}")
    logger.info(f"📊 Database path: {event_receiver.db_path}")
    logger.info(f"🔒 IP Whitelist enabled with {len(config.ALLOWED_IPS)} allowed IPs")
    logger.info(f"📋 Allowed IPs: {config.ALLOWED_IPS}")
    logger.info(f"🔗 Available endpoints:")
    logger.info(f"   📨 POST /api/events - Receive events (IP restricted)")
    logger.info(f"   💚 GET /health - Health check")
    logger.info(f"   📊 GET /api/queue/stats - Queue statistics")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.error(f"💥 Failed to start server: {str(e)}")
        raise

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Event Receiver Service')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5001, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--db-path', default='queue.db', help='SQLite database path')
    
    args = parser.parse_args()
    
    # Initialize event receiver with custom database path if provided
    if args.db_path != 'queue.db':
        event_receiver = EventReceiver(args.db_path)
    
    run_server(host=args.host, port=args.port, debug=args.debug) 