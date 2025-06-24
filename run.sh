#!/bin/bash

echo "🚀 EDevlet Event-Driven System Starting..."
echo "============================================="

# SSL sertifikalarını kontrol et
echo "🔐 Checking SSL certificates..."
python3 src/utils/fix_macos_ssl.py > /dev/null 2>&1

# Gerekli dosyaları oluştur
echo "📁 Setting up queue files..."
touch events.json processed_events.log failed_updates.json

# Event Receiver'ı başlat
echo "▶️ Starting Event Receiver..."
python3 -m src.core.event_receiver &
RECEIVER_PID=$!

# Kısa bekleme - receiver'ın başlaması için
sleep 2

# Orchestrator'ı başlat
echo "▶️ Starting Event Orchestrator..."
python3 -m src.core.orchestrator &
ORCHESTRATOR_PID=$!

echo ""
echo "✅ Event-Driven System is now running!"
echo "================================================="
echo "📡 Event Receiver PID: $RECEIVER_PID"
echo "🎯 Orchestrator PID: $ORCHESTRATOR_PID"
echo ""
echo "🌐 Event Receiver: http://localhost:443"
echo "🏥 Health Check: http://localhost:443/health"
echo "📨 Events Endpoint: http://localhost:443/api/events"
echo ""
echo "📁 Queue Files:"
echo "   - events.json (incoming events)"
echo "   - processed_events.log (processed events tracking)"
echo "   - failed_updates.json (retry queue)"
echo ""
echo "📋 To stop the system:"
echo "   kill $RECEIVER_PID $ORCHESTRATOR_PID"
echo "   or press Ctrl+C"
echo ""
echo "🔍 Monitor logs:"
echo "   tail -f logs/all_operations.txt"
echo "================================================="

# Trap SIGINT and SIGTERM to gracefully shutdown
trap 'echo ""; echo "🛑 Shutting down Event-Driven System..."; kill $RECEIVER_PID $ORCHESTRATOR_PID 2>/dev/null; exit 0' INT TERM

# Wait for both processes to exit
wait $RECEIVER_PID
wait $ORCHESTRATOR_PID

echo "✅ Event-Driven System stopped."

# Usage: ./run.sh