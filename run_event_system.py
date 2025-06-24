#!/usr/bin/env python3
"""
Event-Driven E-Devlet Automation System Launcher
Starts both the Event Receiver and Smart Orchestrator services.
"""

import subprocess
import sys
import time
import signal
import os
from threading import Thread

def run_event_receiver():
    """Run the event receiver service."""
    print("🚀 Starting Event Receiver Service...")
    try:
        subprocess.run([
            sys.executable, '-m', 'src.core.event_receiver',
            '--host', '127.0.0.1',
            '--port', '5001',  # Running behind Nginx reverse proxy
            '--db-path', 'queue.db'
        ])
    except KeyboardInterrupt:
        print("📨 Event Receiver stopped")
    except Exception as e:
        print(f"💥 Event Receiver error: {str(e)}")

def run_orchestrator():
    """Run the smart orchestrator service."""
    print("🎯 Starting Smart Orchestrator...")
    try:
        subprocess.run([
            sys.executable, '-m', 'src.core.orchestrator',
            '--db-path', 'queue.db',
            '--check-interval', '60',
            '--processing-interval', '2'
        ])
    except KeyboardInterrupt:
        print("🎯 Smart Orchestrator stopped")
    except Exception as e:
        print(f"💥 Smart Orchestrator error: {str(e)}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Shutdown signal received. Stopping services...")
    sys.exit(0)

def main():
    """Main entry point - starts both services in parallel."""
    print("=" * 60)
    print("🎯 E-DEVLET EVENT-DRIVEN AUTOMATION SYSTEM")
    print("=" * 60)
    print("🔧 Starting services...")
    print("📨 Event Receiver: https://localhost:443 (via Nginx proxy to internal port 5001)")
    print("🎯 Smart Orchestrator: 2-hour processing intervals")
    print("📊 Database: queue.db (SQLite)")
    print("⚠️  Note: Ensure Nginx reverse proxy is configured and running")
    print("=" * 60)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start both services in separate threads
        receiver_thread = Thread(target=run_event_receiver, daemon=True)
        orchestrator_thread = Thread(target=run_orchestrator, daemon=True)
        
        receiver_thread.start()
        time.sleep(2)  # Give receiver time to start
        orchestrator_thread.start()
        
        print("✅ Both services started successfully!")
        print("\n📋 Available endpoints (via Nginx proxy):")
        print("   📨 POST https://localhost/api/events - Receive events")
        print("   💚 GET  https://localhost/health - Health check")
        print("   📊 GET  https://localhost/api/queue/stats - Queue statistics")
        print("\n🔍 To test the system:")
        print("   curl -X POST https://localhost/api/events \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"event\": {\"userId\": \"test-123\", \"identityNumber\": \"12345678901\", \"eventType\": \"UserCvCreated\", \"eventData\": {\"id\": \"cv-123\", \"documentNumber\": \"BARCODE12345\"}}}'")
        print("\n⏰ Orchestrator will process events every 2 hours")
        print("🔄 Press Ctrl+C to stop both services")
        print("=" * 60)
        
        # Keep main thread alive
        try:
            receiver_thread.join()
            orchestrator_thread.join()
        except KeyboardInterrupt:
            pass
            
    except KeyboardInterrupt:
        print("\n🛑 Services stopped by user")
    except Exception as e:
        print(f"💥 System error: {str(e)}")
    finally:
        print("🧹 System shutdown complete")

if __name__ == '__main__':
    main() 